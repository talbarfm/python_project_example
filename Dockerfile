# DEMO: Docker starts from a full operating-system image that already includes Python.
FROM python:3.12-slim

# DEMO: A container has its own filesystem, separate from your project folder.
WORKDIR /app

# DEMO: Copy only packaging metadata first so Docker can cache dependency installation better.
COPY pyproject.toml README.md LICENSE ./

# DEMO: Copy the importable package code into the image.
COPY src ./src

# DEMO: The same pip command installs this package and its PyPI dependencies inside the image.
RUN python -m pip install --no-cache-dir .

# DEMO: This default command proves the installed console script exists inside the container.
CMD ["dir-monitor-exellenteam", "--version"]
