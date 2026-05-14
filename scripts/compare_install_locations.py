#!/usr/bin/env python3
"""Compare local editable installation paths with PyPI dependency paths."""

from __future__ import annotations

import importlib.metadata as metadata
import importlib.util
import json
from pathlib import Path
import site
import sys
from typing import Optional


def main() -> int:
    print("=== Installation Location Comparison ===")
    print(f"Python executable: {sys.executable}")
    print(f"Virtualenv prefix: {sys.prefix}")
    print("site-packages:")
    for path in site.getsitepackages():
        print(f"  - {path}")

    # DEMO: The project package was installed from this local source tree with pip install -e .
    show_package("Local editable package", "dir-monitor-exellenteam", "dir_monitor_exellenteam")

    # DEMO: These dependencies were downloaded from PyPI during pip install -e .
    show_package("External PyPI dependency", "humanize", "humanize")
    show_package("External PyPI dependency", "colorama", "colorama")

    print("\nLesson:")
    print("  - The local editable package metadata lives in site-packages.")
    print("  - The local editable package code is imported from this repo's src/ directory.")
    print("  - External PyPI packages are downloaded into the virtualenv's site-packages directory.")
    return 0


def show_package(title: str, distribution_name: str, import_name: str) -> None:
    distribution = metadata.distribution(distribution_name)
    spec = importlib.util.find_spec(import_name)
    if spec is None or spec.origin is None:
        raise RuntimeError(f"Could not import {import_name}")

    distribution_root = Path(distribution.locate_file("")).resolve()
    import_file = Path(spec.origin).resolve()
    direct_url = find_direct_url(distribution)

    print(f"\n{title}: {distribution_name}")
    print(f"  version:       {distribution.version}")
    print(f"  import name:   {import_name}")
    print(f"  import file:   {import_file}")
    print(f"  metadata root: {distribution_root}")
    if direct_url is not None:
        print(f"  direct_url:    {direct_url}")
    else:
        print("  direct_url:    <none; this came from a package index such as PyPI>")


def find_direct_url(distribution: metadata.Distribution) -> Optional[dict]:
    for file in distribution.files or []:
        path = Path(file)
        if path.name != "direct_url.json":
            continue

        full_path = Path(distribution.locate_file(file))
        if full_path.exists():
            return json.loads(full_path.read_text(encoding="utf-8"))

    return None


if __name__ == "__main__":
    raise SystemExit(main())
