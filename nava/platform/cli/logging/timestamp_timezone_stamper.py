# initially borrowed from
#
# https://github.com/kierdavis/structlog-overtime/blob/main/structlog_overtime/timestamper.py
#
# which is in the public domain
import datetime
from typing import Callable, Literal

import structlog

__all__ = ["TimezoneAwareTimeStamper"]


def _default_now() -> datetime.datetime:
    return datetime.datetime.now().astimezone()  # pragma: no cover


class TimezoneAwareTimeStamper:
    """Add a timestamp to ``event_dict``.

    A workaround for the fact that structlog.processors.TimeStamper only
    supports UTC or naive (timezone-less) timestamps. Use this if you want to
    make the timezone explicit in the formatted log message.

    Args:
        fmt:
            strftime format string, or ``"iso"`` for `ISO 8601
            <https://en.wikipedia.org/wiki/ISO_8601>`_

        key: Target key in *event_dict* for added timestamps.

        now: Function that returns the current time when called


    """

    __slots__ = ("fmt", "key", "now")

    def __init__(
        self,
        *,
        fmt: str | Literal["iso"] = "%Y-%m-%dT%H:%M:%S%z",
        key: str = "timestamp",
        now: Callable[[], datetime.datetime] = _default_now,
    ):
        self.fmt = fmt
        self.key = key
        self.now = now

    def __call__(
        self,
        logger: structlog.types.WrappedLogger,
        method_name: str,
        event_dict: structlog.types.EventDict,
    ) -> structlog.types.EventDict:
        time = self.now().isoformat() if self.fmt == "iso" else self.now().strftime(self.fmt)
        event_dict[self.key] = time
        return event_dict
