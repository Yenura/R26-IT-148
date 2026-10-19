"""The candidate-code sandbox: policy, backend selection and real isolation.

Candidate-authored code runs on our server, so the container is the security
boundary.  The in-process import guard in ``routers/interview.py`` is a speed
bump, not a control -- ``().__class__.__base__.__subclasses__()`` reaches the
real ``os`` -- so these tests pin the *container* flags and, when a Docker
daemon is available, prove the container actually enforces them.

The policy tests run everywhere; the isolation tests skip without Docker.
"""
import os
import subprocess
import sys
import time
from pathlib import Path

import pytest

BACKEND = Path(__file__).resolve().parent.parent
if str(BACKEND) not in sys.path:
    sys.path.insert(0, str(BACKEND))

from services import code_sandbox  # noqa: E402

DOCKER_READY = code_sandbox.docker_daemon_available() and code_sandbox.image_available()
needs_docker = pytest.mark.skipif(
    not DOCKER_READY, reason="no Docker daemon / runner image available"
)


@pytest.fixture
def subprocess_backend(monkeypatch):
    """Force the development backend so these tests are deterministic."""
    monkeypatch.setenv("CODE_SANDBOX", "subprocess")
    code_sandbox.reset_cache()
    yield
    code_sandbox.reset_cache()


# ---------------------------------------------------------------------------
# The security contract, pinned without Docker
# ---------------------------------------------------------------------------
def test_docker_command_denies_the_network():
    command = code_sandbox.docker_command("c")
    assert "--network" in command
    assert command[command.index("--network") + 1] == "none"


def test_docker_command_has_a_read_only_filesystem():
    command = code_sandbox.docker_command("c")
    assert "--read-only" in command
    # The one writable path is a small tmpfs, and it is not executable.
    tmpfs = command[command.index("--tmpfs") + 1]
    assert tmpfs.startswith("/tmp:")
    assert "noexec" in tmpfs and "nosuid" in tmpfs


def test_docker_command_runs_as_a_non_root_user():
    command = code_sandbox.docker_command("c")
    assert "--user" in command
    uid = command[command.index("--user") + 1].split(":")[0]
    assert uid not in ("0", "root"), f"sandbox runs as root: {uid}"


def test_docker_command_drops_capabilities_and_blocks_escalation():
    command = code_sandbox.docker_command("c")
    assert command[command.index("--cap-drop") + 1] == "ALL"
    joined = " ".join(command)
    assert "no-new-privileges" in joined


def test_docker_command_imposes_resource_limits():
    command = code_sandbox.docker_command("c")
    for flag in ("--memory", "--memory-swap", "--cpus", "--pids-limit"):
        assert flag in command, f"{flag} is not set"
    assert any(arg.startswith("cpu=") for arg in command), "no CPU-time ulimit"


def test_docker_command_mounts_nothing_from_the_host():
    """The script goes in on stdin, so no host path is exposed to the container."""
    command = code_sandbox.docker_command("c")
    assert not any(
        arg in ("-v", "--volume", "--mount", "--privileged") for arg in command
    )
    assert command[-2:] == ["python3", "-"], command[-3:]
    assert "-i" in command, "stdin must be attached for the script to be piped in"


def test_container_name_is_used_so_a_timed_out_run_can_be_killed():
    command = code_sandbox.docker_command("code_sandbox_abc123")
    assert "--name" in command
    assert command[command.index("--name") + 1] == "code_sandbox_abc123"
    assert "--rm" in command


# ---------------------------------------------------------------------------
# Backend selection
# ---------------------------------------------------------------------------
def test_explicit_subprocess_setting_is_honoured(monkeypatch):
    monkeypatch.setenv("CODE_SANDBOX", "subprocess")
    code_sandbox.reset_cache()
    assert code_sandbox.active_backend() == "subprocess"
    code_sandbox.reset_cache()


def test_explicit_docker_setting_refuses_to_degrade(monkeypatch):
    """A production deployment must fail loudly rather than run unisolated."""
    if DOCKER_READY:
        pytest.skip("Docker is available, so there is nothing to degrade")
    monkeypatch.setenv("CODE_SANDBOX", "docker")
    code_sandbox.reset_cache()
    with pytest.raises(code_sandbox.SandboxError):
        code_sandbox.active_backend()
    code_sandbox.reset_cache()


def test_auto_never_returns_a_broken_backend():
    code_sandbox.reset_cache()
    assert code_sandbox.active_backend() in ("docker", "subprocess")
    code_sandbox.reset_cache()


def test_health_description_reports_the_backend():
    code_sandbox.reset_cache()
    info = code_sandbox.describe()
    assert info["backend"] in ("docker", "subprocess")
    assert info["timeout_seconds"] > 0
    assert info["image"]
    code_sandbox.reset_cache()


# ---------------------------------------------------------------------------
# Running candidate code
# ---------------------------------------------------------------------------
def test_subprocess_backend_runs_a_program(subprocess_backend):
    assert code_sandbox.run_python("print(6 * 7)") == "42"


def test_a_runaway_program_is_stopped(subprocess_backend):
    started = time.monotonic()
    assert code_sandbox.run_python("while True:\n    pass\n", timeout=2.0) == ""
    assert time.monotonic() - started < 12, "the time limit did not bite"


def test_a_crashing_program_scores_nothing_rather_than_raising(subprocess_backend):
    assert code_sandbox.run_python("raise ValueError('boom')") == ""
    assert code_sandbox.run_python("this is not python") == ""


# ---------------------------------------------------------------------------
# The container really enforces the policy (skipped without Docker)
# ---------------------------------------------------------------------------
def _raw_container(script: str, timeout: float = 60.0):
    """Run a program in the *bare* container, bypassing the in-process guard.

    This is what proves the container is the boundary: it deliberately does not
    install the import guard, so it exercises the isolation on its own.

    The timeout is deliberately generous.  These tests assert isolation, not
    speed, and a container start on Docker Desktop can take tens of seconds when
    the machine is busy -- a 20s budget made this flake under the full suite
    while passing in isolation.  The timeout is only here so a genuinely hung
    container fails instead of hanging the run.
    """
    return subprocess.run(
        code_sandbox.docker_command("code_sandbox_test")[:-1] + ["-c", script],
        capture_output=True, text=True, timeout=timeout,
    )


@needs_docker
def test_container_filesystem_is_read_only():
    result = _raw_container("open('/etc/should_not_write', 'w').write('x')")
    assert result.returncode != 0, "the container filesystem was writable"


@needs_docker
def test_container_user_is_not_root():
    result = _raw_container("import os; print(os.getuid())")
    assert result.stdout.strip() == "65534", result.stdout


@needs_docker
def test_container_has_no_network():
    script = (
        "import socket\n"
        "try:\n"
        "    socket.create_connection(('1.1.1.1', 80), timeout=3)\n"
        "    print('CONNECTED')\n"
        "except Exception as e:\n"
        "    print('blocked:', type(e).__name__)\n"
    )
    result = _raw_container(script)
    assert "CONNECTED" not in result.stdout, "the container reached the network"


@needs_docker
def test_docker_backend_runs_candidate_code_end_to_end(monkeypatch):
    monkeypatch.setenv("CODE_SANDBOX", "docker")
    code_sandbox.reset_cache()
    assert code_sandbox.run_python("print(6 * 7)") == "42"
    code_sandbox.reset_cache()
