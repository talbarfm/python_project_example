"""Public package API for dir_monitor_exellenteam."""

# DEMO: This __init__.py file makes dir_monitor_exellenteam a regular package.
from .import_examples import describe_import_styles
from .monitor import ChangeEvent, iter_directory_changes, monitor_directory

# DEMO: Package-level names let users import from dir_monitor_exellenteam directly.
__all__ = ["ChangeEvent", "describe_import_styles", "iter_directory_changes", "monitor_directory"]

__version__ = "0.1.0"
