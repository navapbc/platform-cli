import abc
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
        content = (root / self.path).read_text()
        content.replace(self.replaced_contents, self.new_contents)
        (root / self.path).write_text(content)


ChangeSet = list[Change]
