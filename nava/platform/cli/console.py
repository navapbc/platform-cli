"""Handling the CLIs output to users"""

from __future__ import annotations

import os
import sys
from typing import Any, cast

import click
import rich.traceback
from rich.console import Console

import nava.platform.cli.config as config


def initialize(level: config.OutputLevel) -> ConsoleWrapper:
    if level is config.OutputLevel.NONE:
        # this is hacky, but minimal effort for a working `--quiet` right now,
        # also see approach using os.dup2[1]
        #
        # contextlib.redirect_stdout/stderr[2] would be nice, but a globally
        # applied context manager (globally at least to click) is a little
        # tricky, maybe in the future we could look at the script args before
        # they hit click and check for `--quiet` to wrap things early
        #
        # [1] https://stackoverflow.com/questions/4675728/redirect-stdout-to-a-file-in-python/22434262#22434262
        # [2] https://docs.python.org/3/library/contextlib.html#contextlib.redirect_stdout
        sys.stdout = open(os.devnull, "a")  # noqa: SIM115
        sys.stderr = open(os.devnull, "a")  # noqa: SIM115

    global console
    console = ConsoleWrapper(
        output_level=level,
        default=Console(),
        warning=Console(stderr=True, style="yellow"),
        error=Console(stderr=True, style="bold red"),
    )

    rich.traceback.install(console=console.error, show_locals=True, suppress=[click])

    return console


class ConsoleWrapper(Console):
    """A high level console interface

    This is not a true sub-class of `rich.Console`, it merely proxies most calls
    to an underlying `rich.Console` instance, but that's hard to correctly type
    with mypy, so lie. Maybe life will be better one day[1].

    [1] https://github.com/python/typing/issues/802
    """

    output_level: config.OutputLevel
    default: Console
    warning: Console
    error: Console

    def __init__(
        self, output_level: config.OutputLevel, default: Console, warning: Console, error: Console
    ) -> None:
        self.output_level = output_level
        self.default = default
        self.warning = warning
        self.error = error

    def __getattr__(self, attr: str) -> Any:
        return getattr(self.default, attr)


console: ConsoleWrapper | None = None

# convience aliases, for where you are sure things have been set up correctly
unsafe_console = cast(ConsoleWrapper, console)

# TODO: remove?
# info = unsafe_console
# warning = cast(Console, console.warning if console else None)
# error = cast(Console, console.error if console else None)

# print = cast(info.print, info.print if info else None)
