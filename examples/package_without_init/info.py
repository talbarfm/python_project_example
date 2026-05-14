"""A module inside a namespace package folder."""


def namespace_package_message() -> str:
    # DEMO: This folder has no __init__.py, so Python treats it as a namespace package.
    return "Imported a namespace package without __init__.py: package_without_init"
