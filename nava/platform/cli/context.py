from dataclasses import dataclass
from typing import Callable, NoReturn

import nava.platform.cli.console
import nava.platform.cli.logging
from nava.platform.cli.config import AppDirs, OutputLevel, app_dirs

__all__ = ["AppDirs", "CliContext", "OutputLevel"]


@dataclass
class CliContext:
    """Holds various state and I/O for commands"""

    output_level: OutputLevel
    log: nava.platform.cli.logging.Logger
    console: nava.platform.cli.console.ConsoleWrapper
    fail: Callable[[str], NoReturn]
    """Aborts the execution of the program with a specific error message."""
    exit: Callable[[int], NoReturn]
    """Exits the application with a given exit code."""
    app_dirs: AppDirs = app_dirs
