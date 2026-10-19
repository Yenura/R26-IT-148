"""Execution sandbox for candidate code.

The interview asks candidates to write code, so *candidate-authored code runs on
our server*.  That is the one thing that blocks a public launch, and it needs a
real boundary.

Two backends are available:

``docker``
    Runs the candidate program in a throwaway container with no network, no
    writable filesystem, no capabilities, a non-root user and hard CPU, memory
    and process limits.  **This is the boundary that matters.**

``subprocess``
    The previous behaviour: a child ``python`` process with the import guard in
    ``routers/interview.py`` installed.  Development only.  The guard is a
    deliberate speed bump, *not* a security control -- it is trivially bypassed
    by walking ``().__class__.__base__.__subclasses__()`` to the real ``os`` --
    and the child shares the host filesystem and network.

Selection
---------
``CODE_SANDBOX`` selects the backend:

``auto`` (default)
    Use ``docker`` when a daemon and the runner image are available, otherwise
    fall back to ``subprocess`` *with a loud warning*.  The active backend is
    logged at startup and reported by ``/health``, so a deployment cannot
    silently ship the weak one.
``docker``
    Require Docker; raise rather than degrade.
``subprocess``
    Explicit opt-in for local development and for CI runners without Docker.

Configuration
-------------
``CODE_SANDBOX_IMAGE``      runner image (default ``recruitai-py-sandbox:1``)
``CODE_SANDBOX_TIMEOUT``    wall-clock seconds per run (default ``8``)
``CODE_SANDBOX_MEMORY``     memory limit (default ``256m``)
``CODE_SANDBOX_CPUS``       CPU limit (default ``1``)
``CODE_SANDBOX_PIDS``       process limit (default ``64``)
``CODE_SANDBOX_CPUTIME``    CPU seconds before SIGXCPU (default ``5``)
``CODE_SANDBOX_AUTOBUILD``  build the runner image if missing (default ``1``)
"""

from __future__ import annotations

import logging
import os
import shutil
import subprocess
import sys
import uuid
from pathlib import Path
from typing import List, Optional

logger = logging.getLogger(__name__)

#: Directory holding the Dockerfile for the runner image.
SANDBOX_DIR = Path(__file__).resolve().parent.parent / "sandbox"

#: The non-root uid:gid used inside the container (``nobody:nogroup``).
_SANDBOX_USER = "65534:65534"


class SandboxError(RuntimeError):
    """The sandbox could not run candidate code."""


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
def _env(name: str, default: str) -> str:
    value = os.environ.get(name, "").strip()
    return value or default


def backend_setting() -> str:
    """The configured backend: ``auto``, ``docker`` or ``subprocess``."""
    setting = _env("CODE_SANDBOX", "auto").lower()
    if setting not in ("auto", "docker", "subprocess"):
        logger.warning("Unknown CODE_SANDBOX=%r; falling back to 'auto'", setting)
        return "auto"
    return setting


def image_name() -> str:
    return _env("CODE_SANDBOX_IMAGE", "recruitai-py-sandbox:1")


def _limit(name: str, default: str) -> str:
    return _env(name, default)


# ---------------------------------------------------------------------------
# Backend detection
# ---------------------------------------------------------------------------
def docker_binary() -> Optional[str]:
    return shutil.which("docker")


def docker_daemon_available() -> bool:
    """True when a Docker daemon answers.  Cached -- probing costs ~1s."""
    global _DAEMON_PROBE
    if _DAEMON_PROBE is None:
        binary = docker_binary()
        if not binary:
            _DAEMON_PROBE = False
        else:
            try:
                result = subprocess.run(
                    [binary, "info", "--format", "{{.ServerVersion}}"],
                    capture_output=True, text=True, timeout=15,
                )
                _DAEMON_PROBE = result.returncode == 0
            except Exception:
                _DAEMON_PROBE = False
    return _DAEMON_PROBE


_DAEMON_PROBE: Optional[bool] = None


def image_available() -> bool:
    binary = docker_binary()
    if not binary or not docker_daemon_available():
        return False
    try:
        result = subprocess.run(
            [binary, "image", "inspect", image_name()],
            capture_output=True, text=True, timeout=30,
        )
        return result.returncode == 0
    except Exception:
        return False


def build_image(force: bool = False) -> bool:
    """Build the runner image.  Idempotent; returns True when it is usable."""
    if not docker_daemon_available():
        return False
    if image_available() and not force:
        return True

    binary = docker_binary()
    dockerfile = SANDBOX_DIR / "Dockerfile"
    if not (binary and dockerfile.exists()):
        logger.warning("Sandbox image cannot be built: %s missing", dockerfile)
        return False

    logger.info("Building sandbox runner image %s (one-off)...", image_name())
    try:
        result = subprocess.run(
            [binary, "build", "-t", image_name(), "-f", str(dockerfile), str(SANDBOX_DIR)],
            capture_output=True, text=True, timeout=900,
        )
    except Exception as exc:  # noqa: BLE001
        logger.warning("Sandbox image build failed: %s", exc)
        return False
    if result.returncode != 0:
        tail = (result.stderr or result.stdout or "").strip().splitlines()[-3:]
        logger.warning("Sandbox image build failed: %s", " | ".join(tail))
        return False
    logger.info("Sandbox runner image %s built", image_name())
    return True


def resolve_backend(allow_degradation: bool = True) -> str:
    """Decide which backend to use, honouring ``CODE_SANDBOX``."""
    setting = backend_setting()
    if setting == "subprocess":
        return "subprocess"

    usable = docker_daemon_available()
    if usable and not image_available():
        if _env("CODE_SANDBOX_AUTOBUILD", "1") == "1":
            usable = build_image()
        else:
            usable = False

    if usable:
        return "docker"
    if setting == "docker" or not allow_degradation:
        raise SandboxError(
            "CODE_SANDBOX=docker but no usable Docker daemon/image is available. "
            "Start Docker and build the runner image, or set CODE_SANDBOX=subprocess "
            "for local development (NOT for production)."
        )
    return "subprocess"


_backend_cache: Optional[str] = None


def active_backend() -> str:
    """The resolved backend, computed once per process."""
    global _backend_cache
    if _backend_cache is None:
        _backend_cache = resolve_backend()
        if _backend_cache == "subprocess":
            logger.warning(
                "⚠ Candidate code sandbox: 'subprocess' -- candidate code shares the "
                "host filesystem and network.  Development only; set CODE_SANDBOX=docker "
                "before a public deployment."
            )
        else:
            logger.info("✓ Candidate code sandbox: 'docker' (%s)", image_name())
    return _backend_cache


def reset_cache() -> None:
    """Forget the cached probes (used by tests and after a config change)."""
    global _DAEMON_PROBE, _backend_cache
    _DAEMON_PROBE = None
    _backend_cache = None


# ---------------------------------------------------------------------------
# Command construction
# ---------------------------------------------------------------------------
def docker_command(container_name: str) -> List[str]:
    """The hardened ``docker run`` argv for one candidate program.

    Every flag here is a security control, so the list is built in one place and
    pinned by a test.  Read it as: nothing from the network, nothing writable
    except a small no-exec tmpfs, no Linux capabilities, no privilege
    escalation, a non-root user, and hard CPU / memory / process / CPU-time
    limits.  The candidate's script is fed on stdin, so no host path is ever
    mounted into the container.
    """
    return [
        docker_binary() or "docker",
        "run", "--rm", "-i",
        "--name", container_name,
        "--network", "none",
        "--read-only",
        "--tmpfs", "/tmp:rw,noexec,nosuid,size=8m",
        "--user", _SANDBOX_USER,
        "--cap-drop", "ALL",
        "--security-opt", "no-new-privileges",
        "--memory", _limit("CODE_SANDBOX_MEMORY", "256m"),
        "--memory-swap", _limit("CODE_SANDBOX_MEMORY", "256m"),
        "--cpus", _limit("CODE_SANDBOX_CPUS", "1"),
        "--pids-limit", _limit("CODE_SANDBOX_PIDS", "64"),
        "--ulimit", f"cpu={_limit('CODE_SANDBOX_CPUTIME', '5')}",
        "--ulimit", "nofile=64",
        "-e", "PYTHONDONTWRITEBYTECODE=1",
        "-e", "PYTHONUTF8=1",
        "-e", "PYTHONIOENCODING=utf-8",
        image_name(),
        "python3", "-",
    ]


def run_timeout() -> float:
    try:
        return float(_limit("CODE_SANDBOX_TIMEOUT", "8"))
    except ValueError:
        return 8.0


# ---------------------------------------------------------------------------
# Execution
# ---------------------------------------------------------------------------
def run_python(script: str, timeout: Optional[float] = None) -> str:
    """Run ``script`` in the sandbox and return its stripped stdout.

    Returns ``""`` when the program fails, is killed for exceeding a limit, or
    the sandbox itself is broken -- never raises for candidate-caused failure.
    A broken *sandbox* is different from broken candidate code, so it is logged.
    """
    limit = run_timeout() if timeout is None else timeout
    if active_backend() == "docker":
        return _run_in_docker(script, limit)
    return _run_in_subprocess(script, limit)


def _run_in_docker(script: str, timeout: float) -> str:
    name = f"code_sandbox_{uuid.uuid4().hex[:12]}"
    command = docker_command(name)
    try:
        result = subprocess.run(
            command, input=script, capture_output=True, text=True,
            timeout=timeout, encoding="utf-8", errors="replace",
        )
    except subprocess.TimeoutExpired:
        # The CLI is gone but the container may not be; --rm only fires on exit.
        _kill_container(name)
        return ""
    except FileNotFoundError:
        logger.error("Sandbox: docker binary vanished; treating run as failed")
        return ""
    except Exception as exc:  # noqa: BLE001
        logger.error("Sandbox: docker run failed: %s", exc)
        return ""
    return result.stdout.strip()


def _kill_container(name: str) -> None:
    binary = docker_binary()
    if not binary:
        return
    try:
        subprocess.run([binary, "kill", name], capture_output=True, timeout=10)
    except Exception:  # noqa: BLE001
        pass


def _run_in_subprocess(script: str, timeout: float) -> str:
    """Development fallback: a child interpreter with the import guard.

    Shares the host filesystem and network -- see the module docstring.
    """
    import tempfile

    tmp = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".py", delete=False, encoding="utf-8"
        ) as handle:
            handle.write(script)
            tmp = handle.name
        child_env = {**os.environ, "PYTHONUTF8": "1", "PYTHONIOENCODING": "utf-8"}
        result = subprocess.run(
            [sys.executable, tmp], capture_output=True, text=True,
            timeout=timeout, encoding="utf-8", errors="replace", env=child_env,
        )
        return result.stdout.strip()
    except Exception:  # noqa: BLE001
        return ""
    finally:
        if tmp:
            try:
                os.unlink(tmp)
            except OSError:
                pass


def describe() -> dict:
    """Status for ``/health`` and startup logging."""
    return {
        "backend": active_backend(),
        "docker_available": docker_daemon_available(),
        "image": image_name(),
        "image_available": image_available(),
        "timeout_seconds": run_timeout(),
        "setting": backend_setting(),
    }
