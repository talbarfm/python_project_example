"""Run this file from the repository root with: python examples/01_import_examples.py"""

# DEMO: A single .py file can be imported as a module when its folder is on sys.path.
import single_module_example
print("after single module import")
# DEMO: A folder with __init__.py is a regular package and can expose a public API.
import package_with_init
print("after  package with init import")
# DEMO: A folder without __init__.py can still be imported as a namespace package in Python 3.
from package_without_init.info import namespace_package_message
print("after  package without init import")

def f():
    print("im another funciton in this moduel")
print(f)

def main() -> None:
    print(single_module_example.module_message())
    print(package_with_init.package_message())
    print(namespace_package_message())




print(f"the function was defined {str(main)}")
# DEMO: This common pattern keeps code importable without running it immediately.
if __name__ == "__main__":
    print("I was just ran as a main python scripts")
    main()
else:
    print(__name__)


print("Im the last line of the file why am i printed so early?")

# import 01_import_examples.py


"""
after single module import
ive been called __init__.py
hey im the inenr mopdule
the inner module has been imported
after  package with init import
after  package without init import
I was just ran as a main python scripts
Imported a single module: single_module_example.py
Imported a regular package: package_with_init
Imported a namespace package without __init__.py: package_without_init
"""
