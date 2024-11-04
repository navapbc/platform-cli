import logging
from enum import Enum, auto

from platformdirs import PlatformDirs

AppDirs = PlatformDirs


class OutputLevel(Enum):
    NONE = auto()
    NORMAL = auto()
    VERBOSE = auto()
    DEBUG = auto()

    def to_standard_logging_level(self) -> int:
        match self:
            case OutputLevel.NONE:
                return logging.CRITICAL
            case OutputLevel.NORMAL:
                return logging.INFO
            case OutputLevel.VERBOSE:
                return logging.DEBUG
            case OutputLevel.DEBUG:
                return logging.NOTSET


app_dirs = PlatformDirs("nava-platform-cli", "navapbc")
