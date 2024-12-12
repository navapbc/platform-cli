from collections.abc import Callable, Generator
from contextlib import contextmanager
from dataclasses import dataclass
from typing import NoReturn

import nava.platform.cli.console
import nava.platform.cli.logging
from nava.platform.cli.config import AppDirs, OutputLevel, app_dirs

__all__ = ["AppDirs", "CliContext", "OutputLevel"]


@dataclass
class CliContext:
    """Holds various state and I/O for commands."""

    output_level: OutputLevel
    log: nava.platform.cli.logging.Logger
    console: nava.platform.cli.console.ConsoleWrapper
    fail_with_usage: Callable[[str], NoReturn]
    """Aborts the execution of the program with a specific error message and CLI help message."""
    exit: Callable[[int], NoReturn]
    """Exits the application with a given exit code."""
    exception_handler: Callable[["CliContext", BaseException], None]
    """Handle exceptions with this context object."""
    app_dirs: AppDirs = app_dirs

    def fail(self, message: str) -> NoReturn:
        """Aborts the execution of the program with a specific error message."""
        self.console.error.print(message)
        self.exit(1)

    @contextmanager
    def handle_exceptions(self) -> Generator[None, None, None]:
        try:
            yield
        except BaseException as e:
            self.exception_handler(self, e)
