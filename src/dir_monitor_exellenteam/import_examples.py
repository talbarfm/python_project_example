"""Examples that compare relative and absolute imports inside a package."""

from __future__ import annotations

from pathlib import Path

# DEMO: A relative import starts with . and is resolved from this package folder.
from .formatting import human_duration as relative_human_duration

# DEMO: An absolute import names the full package path from the import root.
from dir_monitor_exellenteam.formatting import human_duration as absolute_human_duration

# DEMO: Relative imports are usually preferred inside a package when importing sibling modules.
from .monitor import ChangeEvent as RelativeChangeEvent

# DEMO: Absolute imports work too, but they spell out the full public package name.
from dir_monitor_exellenteam.monitor import ChangeEvent as AbsoluteChangeEvent


def describe_import_styles() -> list[str]:
    """Return short lines explaining the import examples above."""

    relative_event = RelativeChangeEvent("created", path=Path("relative-example.txt"))
    absolute_event = AbsoluteChangeEvent("deleted", path=Path("absolute-example.txt"))

    return [
        f"Relative import used .formatting: {relative_human_duration(3)}",
        f"Absolute import used dir_monitor_exellenteam.formatting: {absolute_human_duration(3)}",
        f"Relative sibling import created: {relative_event.event_type}",
        f"Absolute package import created: {absolute_event.event_type}",
    ]
