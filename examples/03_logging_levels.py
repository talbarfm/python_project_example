"""Run after local install with: python examples/03_logging_levels.py"""

from pathlib import Path

# DEMO: The package exposes a logging level so callers control how much gets printed.
from dir_monitor_exellenteam import monitor_directory


def main() -> None:
    demo_dir = Path("watched_demo")
    demo_dir.mkdir(exist_ok=True)

    print("DEBUG shows setup details, INFO shows normal events, WARNING shows no changes.", flush=True)
    # DEMO: DEBUG prints developer-focused details that INFO hides.
    monitor_directory(demo_dir, timeout=1, interval=0.25, log_level="DEBUG")

    print("\nERROR appears when something actually fails.", flush=True)
    try:
        # DEMO: ERROR logs are useful when an operation cannot complete.
        monitor_directory("missing_demo_directory", timeout=1, log_level="ERROR")
    except FileNotFoundError:
        print("The example caught the FileNotFoundError so the lesson can continue.", flush=True)


if __name__ == "__main__":
    main()
