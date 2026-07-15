# The judge image deliberately begins with the requested Python slim base.
FROM python:3.12-slim

# pytest is installed at image-build time; the judged container has no network.
RUN pip install --no-cache-dir pytest==8.3.5

WORKDIR /workspace
