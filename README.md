# dir_monitor_exellenteam

A small example package for teaching Python packaging, imports, dependencies, CLI entry points, logging, and testing.

PyPI is the package index pip downloads packages from. PyPy is a different Python runtime.

MIT is the license name; it does not mean this project is affiliated with MIT.

## What This Demonstrates

- a distributable Python package using `pyproject.toml`
- a package directory named `dir_monitor_exellenteam`
- a library API for monitoring directory changes
- a CLI command installed from the package
- logging with `DEBUG`, `INFO`, `WARNING`, and `ERROR` levels
- third-party runtime dependencies from PyPI
- relative imports with `.module` syntax inside a package
- absolute imports without dot syntax
- importing a single module
- importing a regular package with `__init__.py`
- importing a namespace package without `__init__.py`
- local editable installation
- virtualenv installation compared with Docker installation
- unit, integration, and system tests
- mocks and spies with `unittest.mock`

## Project Layout

```text
.
├── pyproject.toml
├── src/
│   └── dir_monitor_exellenteam/
│       ├── __init__.py
│       ├── __main__.py
│       ├── cli.py
│       ├── formatting.py
│       ├── import_examples.py
│       └── monitor.py
├── examples/
│   ├── 01_import_examples.py
│   ├── 02_use_installed_package.py
│   ├── 03_logging_levels.py
│   ├── 04_relative_vs_absolute_imports.py
│   ├── single_module_example.py
│   ├── package_with_init/
│   │   ├── __init__.py
│   │   └── greetings.py
│   └── package_without_init/
│       └── info.py
├── scripts/
│   ├── demo_docker_install.sh
│   ├── demo_virtualenv_install.sh
│   ├── compare_install_locations.py
│   ├── install_picker_and_show_paths.py
│   ├── install_local.sh
│   └── run_tests.sh
└── tests/
    ├── unit/
    ├── integration/
    └── system/
```

## Install Locally

```bash
./scripts/install_local.sh
```

That creates `.venv`, installs the package in editable mode, and runs the import examples.

It also compares where packages are installed/imported from:

- `dir-monitor-exellenteam` is installed locally with `pip install -e .`
- `humanize` and `colorama` are downloaded from PyPI as dependencies
- the local package metadata is in `.venv/.../site-packages`, but its code imports from this repo's `src/` folder
- the external PyPI packages import from `.venv/.../site-packages`

You can run just the comparison after local install:

```bash
source .venv/bin/activate
python scripts/compare_install_locations.py
```

## Class Exercise

Use [CLASS_EXERCISE.md](CLASS_EXERCISE.md) for a guided lesson where students compare editable installs, regular virtualenv installs, Docker installs, import paths, and logging behavior.

## Virtualenv vs Docker

Both examples install this package with `pip`, but they isolate different things.

Virtualenv:

- isolates Python packages
- still uses your computer's operating system, shell, and system libraries
- is fast and lightweight for local Python development
- installs with `python -m pip install .`

Run:

```bash
./scripts/demo_virtualenv_install.sh
```

Docker:

- isolates the filesystem and operating-system environment inside an image/container
- includes its own Python interpreter from the base image
- is heavier, but makes the runtime environment more reproducible
- also installs with `python -m pip install .`, this time inside the image

Run:

```bash
./scripts/demo_docker_install.sh
```

The important classroom comparison: `pip` installs the Python package in both cases; virtualenv changes the Python environment on the host, while Docker builds a separate container image with its own Python environment.

## Runtime Dependencies

This package depends on two packages from PyPI:

- `colorama` colors console log levels
- `humanize` turns numeric durations into friendly text in debug logs

They are declared in `pyproject.toml`:

```toml
dependencies = [
    "colorama>=0.4.6",
    "humanize>=4.9",
]
```

When students run `pip install -e .`, pip installs those dependencies from PyPI too.

## Relative vs Absolute Imports

Inside package code, a leading dot means "start from this package":

```python
from .formatting import human_duration
```

Without the dot, Python looks from the import root and uses the full package name:

```python
from dir_monitor_exellenteam.formatting import human_duration
```

Run:

```bash
python examples/04_relative_vs_absolute_imports.py
```

## Choose Install Type and Show Paths

```bash
python scripts/install_picker_and_show_paths.py
```

The picker can demonstrate:

- local development install with `pip install -e .`
- install-location inspection inside a fresh virtualenv

It prints the Python executable, virtualenv, import path, package folder, runtime dependencies, optional dependency metadata, `dist-info` metadata path, console script path, and editable-install helper files.

For non-interactive demos:

```bash
python scripts/install_picker_and_show_paths.py --mode local-dev
```

## Use the CLI

```bash
dir-monitor-exellenteam ./watched_demo --timeout 30 --interval 1 --log-level DEBUG --log-file changes.log
```

While it runs, create, edit, rename, move, or delete files inside `watched_demo`.

## Logging and Log Levels

The monitor uses Python's `logging` module for user-visible runtime information. The examples still use occasional `print()` calls for lesson headings, but package status and directory-monitor events go through logging.

The package demonstrates these levels:

- `DEBUG`: internal settings such as interval, timeout, recursion, and log file
- `INFO`: normal status such as "Watching", each detected change, and the final event count
- `WARNING`: unusual but non-fatal status, such as a timeout with no detected changes
- `ERROR`: failures, including tracebacks from `logger.exception(...)`

CLI examples:

```bash
dir-monitor-exellenteam ./watched_demo --timeout 5 --log-level DEBUG
dir-monitor-exellenteam ./watched_demo --timeout 5 --log-level WARNING
dir-monitor-exellenteam ./watched_demo --timeout 5 --log-level INFO --log-file changes.log
```

Library API example:

```python
from dir_monitor_exellenteam import monitor_directory

monitor_directory(
    "./watched_demo",
    timeout=5,
    interval=1,
    log_level="DEBUG",
    log_file="changes.log",
)
```

Run the focused logging lesson:

```bash
python examples/03_logging_levels.py
```

## Use the Library API

```python
from dir_monitor_exellenteam import monitor_directory

monitor_directory("./watched_demo", timeout=30, log_level="INFO", log_file="changes.log")
```

For more control, iterate over events yourself:

```python
from dir_monitor_exellenteam import iter_directory_changes

for event in iter_directory_changes("./watched_demo", timeout=30):
    print(event.to_log_line())
```

## Run Import Examples

```bash
python examples/01_import_examples.py
python examples/02_use_installed_package.py
python examples/03_logging_levels.py
python examples/04_relative_vs_absolute_imports.py
```

## Run Tests

```bash
./scripts/run_tests.sh
```

Run one layer at a time:

```bash
./scripts/run_tests.sh -m unit
./scripts/run_tests.sh -m integration
./scripts/run_tests.sh -m system
```

The tests intentionally demonstrate mocks:

- unit tests mock time, directory event iteration, and CLI-to-library calls
- integration tests use a real temporary directory plus a spy mock around a real logger
- system tests run subprocess commands and use a mocked environment where useful
