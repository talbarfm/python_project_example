#!/usr/bin/env bash
set -euo pipefail

# DEMO: This script shows OS-level isolation with Docker.
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT"

IMAGE_NAME="dir-monitor-exellenteam-demo"


# DEMO: docker build runs the Dockerfile, including python -m pip install .
docker build -t "$IMAGE_NAME" .

# DEMO: docker run starts a container from the image and proves the package is installed there.
docker run --rm "$IMAGE_NAME"
docker run --rm "$IMAGE_NAME" python -m pip show dir-monitor-exellenteam
docker run --rm "$IMAGE_NAME" python -m pip show colorama humanize
docker run --rm "$IMAGE_NAME" python -c "import sys, dir_monitor_exellenteam; print('Python:', sys.executable); print('Package:', dir_monitor_exellenteam.__file__)"
