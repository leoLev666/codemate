# Minimal Python image for secure code execution
# This container runs user-submitted code with no network, read-only filesystem,
# and dropped capabilities. Managed by docker_sandbox.py.
FROM python:3.11-slim

# Create unprivileged user
RUN useradd --create-home --shell /bin/bash sandbox

# Optional: pre-install safe math/data libraries
RUN pip install --no-cache-dir numpy pandas

USER sandbox
WORKDIR /home/sandbox
