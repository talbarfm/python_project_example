#!/usr/bin/env python3
"""Choose an installation style, install the package, and show where it landed."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
from typing import Optional, Union


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DIST_NAME = "dir-monitor-exellenteam"
IMPORT_NAME = "dir_monitor_exellenteam"
CLI_NAME = "dir-monitor-exellenteam"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    # DEMO: --mode makes the same script useful interactively and in automated classroom demos.
    parser.add_argument(
        "--mode",
        choices=["local-dev"],
        help="Installation flow to run. Omit it to choose from a menu.",
    )
    parser.add_argument(
        "--keep-venv",
        action="store_true",
        help="Reuse the selected virtual environment instead of recreating it.",
    )
    args = parser.parse_args()

    mode = args.mode or ask_for_mode()

    if mode == "local-dev":
        venv_path = PROJECT_ROOT / ".venv-local-dev-demo"
        prepare_venv(venv_path, keep=args.keep_venv)
        run([venv_python(venv_path), "-m", "pip", "install", "--upgrade", "pip"])
        # DEMO: Editable install points the installed package back to this source tree.
        run([venv_python(venv_path), "-m", "pip", "install", "-e", str(PROJECT_ROOT)])
        show_installed_paths(venv_path, title="Local development install")
        return 0

    raise ValueError(f"Unknown mode: {mode}")


def ask_for_mode() -> str:
    print("Choose an installation flow:\n")
    print("1. Local development install from this folder: pip install -e .")
    print("   This also shows where the local package is installed compared to PyPI dependencies.\n")

    choices = {
        "1": "local-dev",
    }

    while True:
        answer = input("Enter 1: ").strip()
        if answer in choices:
            return choices[answer]
        print("Please choose 1.")


def prepare_venv(venv_path: Path, *, keep: bool) -> None:
    if venv_path.exists() and not keep:
        shutil.rmtree(venv_path)

    if not venv_path.exists():
        # DEMO: A virtual environment makes the install location easy to inspect and remove.
        run([sys.executable, "-m", "venv", str(venv_path)])


def show_installed_paths(venv_path: Path, *, title: str) -> None:
    print(f"\n=== {title}: installed paths ===")
    run(
        [venv_python(venv_path), "-c", INSPECT_INSTALLED_PACKAGE],
        display=f"{venv_python(venv_path)} -c <inspect installed package paths>",
    )


def venv_python(venv_path: Path) -> str:
    if os.name == "nt":
        return str(venv_path / "Scripts" / "python.exe")
    return str(venv_path / "bin" / "python")


def run(
    command: Union[list[str], str],
    *,
    cwd: Path = PROJECT_ROOT,
    shell: bool = False,
    display: Optional[str] = None,
) -> None:
    printable = display or (command if isinstance(command, str) else " ".join(command))
    print(f"\n$ {printable}", flush=True)
    subprocess.run(command, cwd=cwd, shell=shell, check=True)


INSPECT_INSTALLED_PACKAGE = r"""
from __future__ import annotations

import importlib.metadata as metadata
import importlib.util
import json
from pathlib import Path
import shutil
import site
import sys

DIST_NAME = "dir-monitor-exellenteam"
IMPORT_NAME = "dir_monitor_exellenteam"
CLI_NAME = "dir-monitor-exellenteam"

distribution = metadata.distribution(DIST_NAME)
spec = importlib.util.find_spec(IMPORT_NAME)
if spec is None or spec.origin is None:
    raise SystemExit(f"Could not import {IMPORT_NAME}")

distribution_root = Path(distribution.locate_file("")).resolve()
package_file = Path(spec.origin).resolve()
package_directory = package_file.parent
script_dir = Path(sys.executable).parent
console_script_candidates = [script_dir / CLI_NAME, script_dir / f"{CLI_NAME}.exe"]
console_script = next((str(path.resolve()) for path in console_script_candidates if path.exists()), None)
console_script = console_script or shutil.which(CLI_NAME, path=str(script_dir)) or "<not found in virtualenv>"
dist_info_dirs = sorted({
    distribution_root / Path(file).parts[0]
    for file in (distribution.files or [])
    if Path(file).parts and Path(file).parts[0].endswith(".dist-info")
})
editable_files = sorted(distribution_root.glob("__editable__*"))
matching_files = sorted(distribution_root.glob("*dir_monitor_exellenteam*"))

print(f"Python executable:      {sys.executable}")
print(f"Virtualenv prefix:      {sys.prefix}")
print(f"Package version:        {distribution.version}")
print(f"Import package file:    {package_file}")
print(f"Import package folder:  {package_directory}")
print(f"Distribution root:      {distribution_root}")
print(f"Console script path:    {console_script}")

requirements = distribution.requires or []
runtime_requirements = [requirement for requirement in requirements if "extra ==" not in requirement]
optional_requirements = [requirement for requirement in requirements if "extra ==" in requirement]

print("Runtime dependencies:")
for requirement in runtime_requirements:
    print(f"  - {requirement}")
if not runtime_requirements:
    print("  - none")

print("Optional dependency metadata:")
for requirement in optional_requirements:
    print(f"  - {requirement}")
if not optional_requirements:
    print("  - none")

print("Site package paths:")
for path in site.getsitepackages():
    print(f"  - {path}")

print("Distribution metadata:")
for path in dist_info_dirs:
    print(f"  - {path}")
    direct_url = path / "direct_url.json"
    if direct_url.exists():
        data = json.loads(direct_url.read_text(encoding="utf-8"))
        print(f"    direct_url.json: {data}")

print("Editable-install helper files:")
if editable_files:
    for path in editable_files:
        print(f"  - {path}")
else:
    print("  - none")

print("Other matching installed files:")
if matching_files:
    for path in matching_files:
        print(f"  - {path}")
else:
    print("  - none")
"""


if __name__ == "__main__":
    raise SystemExit(main())
