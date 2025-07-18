import functools
from collections.abc import Callable
from typing import ParamSpec, TypeVar

P = ParamSpec("P")
R = TypeVar("R")


def print_call(func: Callable[P, R], printer: Callable[[str], None] = print) -> Callable[P, R]:
    return wrap_call(
        func,
        lambda *args, **kwargs: printer(
            f"Calling: {func.__name__} with args:\n{args}\n and kwargs:\n{kwargs}"
        ),
    )


def log_call(func: Callable[P, R], logger: Callable[..., None]) -> Callable[P, R]:
    return wrap_call(
        func,
        lambda *args, **kwargs: logger(
            "Calling function", name=func.__name__, args=args, kwargs=kwargs
        ),
    )


def wrap_call(func: Callable[P, R], do: Callable[P, None]) -> Callable[P, R]:
    @functools.wraps(func)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
        do(*args, **kwargs)
        return func(*args, **kwargs)

    return wrapper
