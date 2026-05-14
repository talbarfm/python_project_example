"""Shared pytest helpers for the package lesson."""

from __future__ import annotations

from pathlib import Path
import sys


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"

# DEMO: Tests import from src so they exercise the same package layout used by pyproject.toml.
sys.path.insert(0, str(SRC_DIR))
