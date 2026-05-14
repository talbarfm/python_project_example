"""Unit tests for formatting helpers and import examples."""

from __future__ import annotations

import importlib.metadata as metadata
import logging

import pytest

from dir_monitor_exellenteam import describe_import_styles
from dir_monitor_exellenteam.formatting import ColorfulLogFormatter, color_log_level, human_duration


@pytest.mark.unit
def test_runtime_dependencies_are_declared_in_distribution_metadata() -> None:
    requirements = metadata.requires("dir-monitor-exellenteam") or []

    # DEMO: This checks the dependencies students see when inspecting package metadata.
    assert any(requirement.startswith("colorama") for requirement in requirements)
    assert any(requirement.startswith("humanize") for requirement in requirements)


@pytest.mark.unit
def test_human_duration_uses_third_party_humanize_package() -> None:
    # DEMO: human_duration is a tiny wrapper around the external humanize dependency.
    assert human_duration(3) == "3 seconds"
    assert human_duration(None) == "forever"


@pytest.mark.unit
def test_color_log_level_uses_third_party_colorama_codes() -> None:
    colored = color_log_level("ERROR")

    assert "ERROR" in colored
    assert "\x1b[" in colored


@pytest.mark.unit
def test_colorful_formatter_restores_original_level_name() -> None:
    record = logging.LogRecord(
        name="demo",
        level=logging.WARNING,
        pathname=__file__,
        lineno=1,
        msg="hello",
        args=(),
        exc_info=None,
    )
    formatter = ColorfulLogFormatter("%(levelname)s %(message)s")

    formatted = formatter.format(record)

    assert "WARNING" in formatted
    assert "hello" in formatted
    assert "\x1b[" in formatted
    assert record.levelname == "WARNING"


@pytest.mark.unit
def test_describe_import_styles_mentions_relative_and_absolute_imports() -> None:
    lines = describe_import_styles()

    # DEMO: This verifies the package's relative-import and absolute-import teaching example.
    assert any("Relative import" in line for line in lines)
    assert any("Absolute import" in line for line in lines)
