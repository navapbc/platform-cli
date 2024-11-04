import platform

import structlog


class PlatformInfoAdder:
    def __init__(self, simple: bool = True) -> None:
        self.state = platform_info(simple)

    def __call__(
        self,
        logger: structlog.typing.WrappedLogger,
        name: str,
        event_dict: structlog.typing.EventDict,
    ) -> structlog.typing.EventDict:
        event_dict.update(self.state)
        return event_dict


def platform_info(simple: bool = True) -> dict[str, str]:
    info = {
        "platform.platform": platform.platform(),
        "platform.python_implementation": platform.python_implementation(),
        "platform.python_version": platform.python_version(),
    }

    if not simple:
        info |= {
            "platform.system": platform.system(),
            "platform.version": platform.version(),
            "platform.node": platform.node(),
            "platform.machine": platform.machine(),
            "platform.processor": platform.processor(),
        }

    return info
