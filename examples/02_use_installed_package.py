"""Run after local install with: python examples/02_use_installed_package.py"""

from pathlib import Path

# DEMO: This import works after the package is installed locally or from PyPI.
from dir_monitor_exellenteam import iter_directory_changes


def main() -> None:
    demo_dir = Path("watched_demo")
    demo_dir.mkdir(exist_ok=True)

    print("Monitoring watched_demo for 3 seconds.")
    print("Create, edit, move, rename, or delete a file there to see events.")

    # DEMO: Library users can iterate over raw events instead of using the CLI.
    for event in iter_directory_changes(demo_dir, timeout=3, interval=0.5):
        print(event.to_log_line())


if __name__ == "__main__":
    main()
