import atexit
import os
import resource
import sys
import time
from pathlib import Path

import structlog

import nava.platform.cli.config as cli_config
from nava.platform.util.strings import str_to_bool

from . import config

Logger = structlog.stdlib.BoundLogger


log: Logger = structlog.stdlib.get_logger()


def initialize(
    level: cli_config.OutputLevel, *, log_to_file: bool | None = None, log_file: Path | None = None
) -> Logger:
    log_level = level.to_standard_logging_level()
    log_to_console = level is cli_config.OutputLevel.DEBUG

    if log_to_file is None:
        log_to_file = str_to_bool(os.getenv("LOG_TO_FILE", "true"))

    if log_to_file and log_file is None:
        cli_config.app_dirs.user_log_path.mkdir(parents=True, exist_ok=True)
        log_file = cli_config.app_dirs.user_log_path / "log.json"

    config.configure(
        log_level=log_level,
        log_to_console=log_to_console,
        log_to_file=log_to_file,
        log_file=log_file,
    )

    log.info("start", argv=sys.argv)
    atexit.register(exit_handler, log)

    return log


_start_time = time.monotonic()


def exit_handler(logger: Logger) -> None:
    """Log a message at program exit."""
    t = time.monotonic() - _start_time
    ru = resource.getrusage(resource.RUSAGE_SELF)
    logger.info(
        "exit",
        real_s=t,
        user_s=ru.ru_utime,
        system_s=ru.ru_stime,
        peak_rss_kb=ru.ru_maxrss,
    )
