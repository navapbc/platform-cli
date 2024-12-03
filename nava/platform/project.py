from dataclasses import dataclass
from functools import cached_property
from pathlib import Path
from typing import Iterable

from nava.platform.util import git


@dataclass
class Project:
    dir: Path

    @cached_property
    def git(self) -> git.GitProject:
        return git.GitProject(self.dir)

    def installed_template_names(self) -> Iterable[str]:
        state_dirs = filter(lambda f: f.is_dir(), self.dir.glob(".template-*"))

        return map(lambda d: d.name, state_dirs)
