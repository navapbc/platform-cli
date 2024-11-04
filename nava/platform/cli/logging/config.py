import logging
import logging.config
from pathlib import Path

import structlog

from nava.platform.cli.logging.platform_info import PlatformInfoAdder
from nava.platform.cli.logging.timestamp_timezone_stamper import TimezoneAwareTimeStamper


def configure(
    log_level: int = logging.INFO,
    log_to_console: bool = False,
    log_to_file: bool = True,
    log_file: Path | None = None,
) -> None:
    # using local timezone timestamps for things to make slighly more sense when
    # looking at the local logs
    #
    # could additionally add a UTC version with something like:
    #
    #   timestamper_utc = structlog.processors.TimeStamper(fmt="iso", utc=True, key="timestamp_utc")
    timestamper = TimezoneAwareTimeStamper(fmt="iso")
    platform_info_adder = PlatformInfoAdder()

    # these are processors for log messages that do _not_ come through structlog
    pre_chain = [
        structlog.stdlib.add_log_level,
        # add extra attributes of LogRecord objects to the event dictionary so
        # that values passed in the extra parameter of log methods pass through
        # to log output
        structlog.stdlib.ExtraAdder(),
        structlog.processors.CallsiteParameterAdder(),
        platform_info_adder,
        timestamper,
    ]

    handlers = {}

    # TODO: could consolidate log_to_file and log_file maybe?
    if log_to_file:
        if log_file is None:
            raise ValueError("must specify a log file if logging to file")

        # TODO: TimedRotatingFileHandler may make more sense
        # https://docs.python.org/3/library/logging.handlers.html#timedrotatingfilehandler
        handlers["file"] = {
            "level": "DEBUG",
            "class": "logging.handlers.RotatingFileHandler",
            "filename": log_file,
            "formatter": "json",
            "maxBytes": 10 * 1024 * 1024,
            "backupCount": 5,
            "delay": True,
        }
    if log_to_console:
        handlers["console"] = {
            "level": "DEBUG",
            "class": "logging.StreamHandler",
            "formatter": "console",
            "stream": "ext://sys.stderr",
        }

    logging_config = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "json": {
                "()": structlog.stdlib.ProcessorFormatter,
                "processors": [
                    # structlog.processors.dict_tracebacks,
                    structlog.stdlib.ProcessorFormatter.remove_processors_meta,
                    structlog.processors.JSONRenderer(),
                ],
                "foreign_pre_chain": pre_chain,
            },
            "console": {
                "()": structlog.stdlib.ProcessorFormatter,
                "processors": [
                    # extract_from_record,
                    structlog.stdlib.ProcessorFormatter.remove_processors_meta,
                    structlog.dev.ConsoleRenderer(colors=True),
                ],
                "foreign_pre_chain": pre_chain,
            },
        },
        "handlers": handlers,
        "loggers": {
            "": {
                "handlers": list(handlers.keys()),
                "level": log_level,
                "propagate": True,
            },
        },
    }

    logging.config.dictConfig(logging_config)

    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.CallsiteParameterAdder(),
            platform_info_adder,
            timestamper,
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
        ],
        cache_logger_on_first_use=True,
        wrapper_class=structlog.make_filtering_bound_logger(log_level),
        logger_factory=structlog.stdlib.LoggerFactory(),
    )
