import abc
from collections import UserList
from dataclasses import dataclass
from pathlib import Path


class Change(abc.ABC):
    @abc.abstractmethod
    def apply(self, root: Path):
        pass


@dataclass
class RenameChange(Change):
    old: str
    new: str


@dataclass
class FileChange(Change):
    path: str
    replaced_contents: str
    new_contents: str

    def apply(self, root: Path):
        (root / self.path).write_text(self.new_contents)


class ChangeSet(UserList[Change]):
    def apply(self, root: Path):
        for change in self:
            change.apply(root)
