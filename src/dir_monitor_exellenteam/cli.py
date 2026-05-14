"""Command-line interface for dir_monitor_exellenteam."""

from __future__ import annotations

import argparse
import logging
from pathlib import Path
from typing import Optional, Sequence

from . import __version__
from .monitor import monitor_directory


def build_parser() -> argparse.ArgumentParser:
    """Create the CLI parser."""

    parser = argparse.ArgumentParser(
        prog="dir-monitor-exellenteam",
        description="Monitor a directory and log created, deleted, modified, and moved files.",
    )
    # DEMO: This required positional argument is the directory the user wants to watch.
    parser.add_argument("directory", help="Directory to monitor.")
    # DEMO: timeout=None means the monitor keeps running until the user stops it.
    parser.add_argument("--timeout", type=float, default=None, help="Seconds to run before stopping.")
    parser.add_argument("--interval", type=float, default=1.0, help="Seconds between directory scans.")
    parser.add_argument("--log-file", type=Path, default=None, help="Optional file to write change logs into.")
    # DEMO: Log levels let users choose how much information the program prints.
    parser.add_argument(
        "--log-level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        default="INFO",
        help="Minimum log level to print.",
    )
    parser.add_argument("--non-recursive", action="store_true", help="Only monitor direct children.")
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    return parser


def main(argv: Optional[Sequence[str]] = None) -> int:
    """Run the CLI command."""

    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        # DEMO: The CLI delegates real work to the library API instead of duplicating logic.
        monitor_directory(
            args.directory,
            timeout=args.timeout,
            interval=args.interval,
            log_file=args.log_file,
            log_level=args.log_level,
            recursive=not args.non_recursive,
        )
    except KeyboardInterrupt:
        # DEMO: Even interrupt messages go through logging instead of print.
        logging.getLogger("dir_monitor_exellenteam").warning("Stopped by user.")
        return 130
    except Exception as error:
        parser.error(str(error))
        return 2

    return 0
