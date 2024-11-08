"""Tweaked version of the upstream copier functionality

See the upstream:
https://github.com/copier-org/copier/blob/259f351fc3c017c82b235888c119b9010d80494a/copier/main.py
"""
from dataclasses import dataclass
from functools import cached_property
from pathlib import Path
from typing import Any, Callable, Sequence

from copier.main import Worker
from copier.types import (
    AnyByStrDict,
    StrOrPath,
)


@dataclass
class NavaWorker(Worker):
    """Some (hopefully) small tweaks of upstream functionality

    Copier's upstream exclusion logic only runs against paths after they have
    been rendered. This class supports exclusions based on the paths in the
    template itself, _before_ they have rendered, via `src_exclude` which can be
    specified in the `copier.yml` file or as arguments in the API call.
    """
    src_exclude: Sequence[str] = ()

    @cached_property
    def all_src_exclusions(self) -> Sequence[str]:
        """Combine template and user-chosen exclusions."""
        return tuple(self.template.config_data.get("src_exclude", [])) + tuple(self.src_exclude)

    @cached_property
    def match_src_exclude(self) -> Callable[[Path], bool]:
        """Get a callable to match paths against src file exclusions."""
        return self._path_matcher(self.all_src_exclusions)

    def _render_path(self, relpath: Path) -> Path | None:
        # if `_render_path()` returns `None`, `_render_template()` skips the
        # path, so seems like the least invasive place to hook in
        #
        # https://github.com/copier-org/copier/blob/259f351fc3c017c82b235888c119b9010d80494a/copier/main.py#L609-L613
        if self.match_src_exclude(relpath):
            return None

        return super()._render_path(relpath)


def run_copy(
    src_path: str,
    dst_path: StrOrPath = ".",
    data: AnyByStrDict | None = None,
    **kwargs: Any,
) -> Worker:
    """Copy a template to a destination, from zero."""
    if data is not None:
        kwargs["data"] = data
    with NavaWorker(src_path=src_path, dst_path=Path(dst_path), **kwargs) as worker:
        worker.run_copy()
    return worker


def run_update(
    dst_path: StrOrPath = ".",
    data: AnyByStrDict | None = None,
    **kwargs: Any,
) -> Worker:
    """Update a subproject, from its template."""
    if data is not None:
        kwargs["data"] = data
    with NavaWorker(dst_path=Path(dst_path), **kwargs) as worker:
        worker.run_update()
    return worker
