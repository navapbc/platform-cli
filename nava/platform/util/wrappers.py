import functools
from collections.abc import Callable
from typing import ParamSpec, TypeVar

P = ParamSpec("P")
R = TypeVar("R")


def print_call(func: Callable[P, R]) -> Callable[P, R]:
    @functools.wraps(func)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
        print(f"Calling: {func.__name__} with args:\n{args}\n and kwargs:\n{kwargs}")
        return func(*args, **kwargs)

    return wrapper
