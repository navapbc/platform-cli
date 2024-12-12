import inspect
from contextlib import AbstractContextManager, nullcontext
from typing import Any

import pytest

import nava.platform.util.collections.dict as dict_util


def test_least_recently_used_dict():
    lru_dict = dict_util.LeastRecentlyUsedDict(maxsize=4)

    assert lru_dict["a"] == 0
    assert len(lru_dict) == 0

    lru_dict["a"] = 10
    lru_dict["b"] = 20
    lru_dict["c"] = 30
    lru_dict["d"] = 40

    assert len(lru_dict) == 4
    assert tuple(lru_dict.items()) == (("a", 10), ("b", 20), ("c", 30), ("d", 40))
    assert lru_dict["a"] == 10
    assert lru_dict["b"] == 20
    assert lru_dict["c"] == 30
    assert lru_dict["d"] == 40
    assert lru_dict["e"] == 0
    assert len(lru_dict) == 4

    lru_dict["a"] += 1  # Write existing a, move to end
    assert len(lru_dict) == 4
    assert tuple(lru_dict.items()) == (("b", 20), ("c", 30), ("d", 40), ("a", 11))

    lru_dict["f"] = 50  # Write new key f, and evict oldest b
    lru_dict["c"] += 1  # Write existing c, move to end, and evict oldest d
    lru_dict["g"] = 60  # Write new key g, and evict oldest d
    assert len(lru_dict) == 4
    assert tuple(lru_dict.items()) == (("a", 11), ("f", 50), ("c", 31), ("g", 60))


@pytest.mark.parametrize(
    ("given", "expected"),
    [
        (None, None),
        ([""], None),
        (["key=value"], {"key": "value"}),
        (["key=value", ""], {"key": "value"}),
        (["", "key=value", ""], {"key": "value"}),
        (["key="], {"key": ""}),
        (["=value"], {"": "value"}),
        (["key=value", "key=value"], ValueError),
    ],
)
def test_from_str_values(given, expected):
    context: AbstractContextManager[Any] = nullcontext()
    if inspect.isclass(expected) and issubclass(expected, BaseException):
        context = pytest.raises(expected)

    with context:
        assert dict_util.from_str_values(given) == expected
