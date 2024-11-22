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
