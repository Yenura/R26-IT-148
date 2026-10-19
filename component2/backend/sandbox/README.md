# Candidate-code sandbox

Candidates write code during the interview, so **candidate-authored code runs on
our server**. That is the one thing that blocks a public launch.

This directory holds the runner image. `component2/backend/services/code_sandbox.py`
builds the command, launches the container and is the only thing that should
ever touch it.

## Why a container

The import guard in `routers/interview.py` blocks `os`, `sys`, `subprocess`,
`socket` and friends before the candidate's code runs. It is useful — it stops
the obvious `import os; os.system(...)` and it is all that protects the
development fallback — but it is **not a security boundary**. Three lines defeat
it:

```python
for cls in ().__class__.__base__.__subclasses__():
    ...
```

so the guard is a speed bump, and the container is the boundary.

## What the container guarantees

Every one of these is a flag in `docker_command()` and is pinned by
`tests/test_code_sandbox.py`:

| Flag | Prevents |
|---|---|
| `--network none` | exfiltrating the question bank, mining, calling out |
| `--read-only` | modifying anything on disk |
| `--tmpfs /tmp:noexec,nosuid` | the only writable space, and nothing in it can be executed |
| `--user 65534:65534` | running as root |
| `--cap-drop ALL` | retained Linux capabilities |
| `--security-opt no-new-privileges` | setuid escalation |
| `--memory` / `--memory-swap` | memory exhaustion (also bounds captured stdout) |
| `--cpus` | CPU starvation of the app |
| `--pids-limit` | fork bombs |
| `--ulimit cpu=5` | a runaway loop that never yields |
| no `-v` / `--mount` | any host path reaching the candidate |

The candidate's program is piped in on **stdin** (`docker run -i ... python3 -`),
so no host directory is mounted into the container at all.

## Building it

The backend builds it on demand (`CODE_SANDBOX_AUTOBUILD=1`, the default), or:

```bash
docker build -t recruitai-py-sandbox:1 component2/backend/sandbox
```

The context is this directory, so the build is one layer over
`python:3.12-slim-bookworm` and takes seconds.

## Verifying it

```bash
cd component2/backend
python -m pytest tests/test_code_sandbox.py -v
```

The policy tests always run. With a Docker daemon up, the isolation tests prove
the guarantees against the real container rather than trusting the flags:

* writing to `/etc` fails (read-only filesystem)
* `os.getuid()` is `65534` (non-root)
* a TCP connection is refused (no network)

## Switching backends

`CODE_SANDBOX` selects the backend:

| Value | Behaviour |
|---|---|
| `auto` (default) | Docker when a daemon and the image are usable, otherwise the subprocess fallback **with a loud startup warning** |
| `docker` | Require Docker; refuse to start otherwise. Use this in production. |
| `subprocess` | Development/CI only: a child interpreter with the import guard, sharing the host filesystem and network |

The resolved backend is logged at startup and returned by `GET /interview/health`
under `code_sandbox`, so a deployment cannot silently ship the weak one.

## Deployment note

The app itself runs in Docker (`docker-compose.yml`), so `c2` needs to reach a
daemon to launch the runner. Compose mounts `/var/run/docker.sock` into `c2` and
enables the CLI through the `WITH_DOCKER_CLI` build arg.

That socket is **root-equivalent on the host**, so `c2` must stay trusted. The
candidate's code never sees it — it runs in the runner container, which is
created *by* `c2` and gets no socket. If `c2` is ever compromised, the host is
too; that is a property of relying on the host daemon, and the alternative
(docker-in-docker or a dedicated remote runner) is a bigger change.

## Known limits

* No gVisor/Kata: this is `runc` + namespaces, so it defends against a malicious
  *program*, not against a kernel exploit.
* No disk quota beyond `--read-only` + the 8 MB `/tmp` tmpfs.
* Captured stdout is bounded by container memory (~256 MB per concurrent run).
* Wall-clock timeout is enforced by the host (`CODE_SANDBOX_TIMEOUT`, default
  8 s) and the container is killed by name if the CLI is killed first.
