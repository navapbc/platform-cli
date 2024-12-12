import collections
from collections.abc import Hashable, Iterable
from typing import Any


def from_str_values(value: Iterable[str] | None) -> dict[str, str] | None:
    """Convert a sequence of 'key=value' strings into a dictionary."""
    result = {}

    if value is None:
        return None

    for val in value:
        if not val.strip():
            continue

        k, v = val.split("=")

        if k in result:
            raise ValueError(f"Data {k} is specified twice")

        result[k] = v

    return result if result else None


class LeastRecentlyUsedDict(collections.OrderedDict[Hashable, int]):
    """A dict with a maximum size, evicting the least recently written key when full.

    Getting a key that is not present returns a default value of 0.

    Setting a key marks it as most recently used and removes the oldest key if full.

    May be useful for tracking the count of items where limited memory usage is needed even if
    the set of items can be unlimited.

    Based on the example at
    https://docs.python.org/3/library/collections.html#ordereddict-examples-and-recipes
    """

    def __init__(self, maxsize: int = 128, *args: Any, **kwargs: Any) -> None:
        self.maxsize = maxsize
        super().__init__(*args, **kwargs)

    def __getitem__(self, key: Hashable) -> int:
        if key in self:
            return super().__getitem__(key)
        return 0

    def __setitem__(self, key: Hashable, value: int) -> None:
        if key in self:
            self.move_to_end(key)
        super().__setitem__(key, value)
        if self.maxsize < len(self):
            self.popitem(last=False)
