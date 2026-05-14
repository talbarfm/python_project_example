"""Run this file from the repository root with: python examples/01_import_examples.py"""

# DEMO: A single .py file can be imported as a module when its folder is on sys.path.
import single_module_example

# DEMO: A folder with __init__.py is a regular package and can expose a public API.
import package_with_init

# DEMO: A folder without __init__.py can still be imported as a namespace package in Python 3.
from package_without_init.info import namespace_package_message


def main() -> None:
    print(single_module_example.module_message())
    print(package_with_init.package_message())
    print(namespace_package_message())


# DEMO: This common pattern keeps code importable without running it immediately.
if __name__ == "__main__":
    main()
