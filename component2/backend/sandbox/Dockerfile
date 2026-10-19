# Runner image for candidate-authored code.
#
# Built and driven by services/code_sandbox.py.  This container IS the security
# boundary for candidate code, so it deliberately carries as little as possible:
# a CPython interpreter, the standard library, and no way for candidate code to
# escalate, install anything, or reach the network.
#
#   docker build -t recruitai-py-sandbox:1 component2/backend/sandbox
#
# The sandbox also passes every one of these as a runtime flag (see
# docker_command()), so the guarantees are enforced even if this file is edited
# carelessly.  They are repeated here so the image is safe when run by hand.

FROM python:3.12-slim-bookworm

# Strip the package manager and the setuid/setgid bits.  --cap-drop ALL and
# --read-only already make these unusable, but a candidate who escapes the
# interpreter should find nothing to work with.
RUN python3 -m pip uninstall -y pip setuptools wheel >/dev/null 2>&1 || true \
 && find / -xdev \( -perm -4000 -o -perm -2000 \) -type f -exec chmod a-s {} + 2>/dev/null || true \
 && rm -rf /root/.cache /tmp/* /var/tmp/*

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONHASHSEED=0 \
    PYTHONUTF8=1

# Non-root by default (65534 = nobody:nogroup on Debian).  The sandbox forces
# the same uid at runtime via `--user`.
USER 65534:65534

# The container is run with --read-only; /tmp is the one writable path and is
# mounted noexec,nosuid by the sandbox.
WORKDIR /tmp

# No ENTRYPOINT on purpose.  The sandbox always passes the full command
# (`docker run ... <image> python3 -`) so it works with any Python image, not
# only this one -- and so the candidate program arriving on stdin is the only
# thing that determines what runs.
