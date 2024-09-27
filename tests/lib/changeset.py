import abc
from dataclasses import dataclass


class Change(abc.ABC):
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


ChangeSet = list[Change]
