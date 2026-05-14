"""Run after local install with: python examples/04_relative_vs_absolute_imports.py"""

# DEMO: Code outside the package uses an absolute import with the package name.
from dir_monitor_exellenteam import describe_import_styles


def main() -> None:
    # DEMO: The package function demonstrates relative and absolute imports inside package modules.
    for line in describe_import_styles():
        print(line)


if __name__ == "__main__":
    main()
