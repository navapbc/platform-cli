from collections.abc import Iterable
from dataclasses import dataclass
from functools import cached_property
from pathlib import Path

from nava.platform.util import git


@dataclass
class Project:
    dir: Path

    @cached_property
    def git(self) -> git.GitProject:
        return git.GitProject(self.dir)

    def installed_template_names(self) -> Iterable[str]:
        state_dirs = filter(lambda f: f.is_dir(), self.dir.glob(".template-*"))

        return map(lambda d: d.name.removeprefix("."), state_dirs)

    def installed_template_names_for_app(self, app_name: str) -> Iterable[str]:
        answer_files = self._installed_template_answer_files_for_app(app_name)

        return map(lambda f: f.parent.name.removeprefix("."), answer_files)

    def _installed_template_answer_files_for_app(self, app_name: str) -> Iterable[Path]:
        answer_files = filter(lambda f: f.is_file(), self.dir.glob(f".template-*/*{app_name}*"))

        return answer_files
