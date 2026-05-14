"""A regular package because this folder contains __init__.py."""
print("ive been called __init__.py")
# DEMO: __init__.py can re-export names from submodules for easier imports.
from .greetings import package_message
print("the inner module has been imported")
# DEMO: __all__ lists the names this package intentionally exposes as its public API.
__all__ = ["package_message"]




