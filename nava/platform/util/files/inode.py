import abc
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class Inode(abc.ABC):
    path: Path

    @abc.abstractmethod
    def is_file(self) -> bool:
        raise NotImplementedError()


class FileNode(Inode):
    def is_file(self) -> bool:
        return True


@dataclass
class DirNode(Inode):
    children: dict[str, Inode] = field(default_factory=dict)

    def is_file(self) -> bool:
        return False

    def add_file(self, path: Path) -> None:
        """Add a file to the inode tree at the given path"""

        if len(path.parts) < 1:
            return

        node = self
        for i, part in enumerate(path.parts[:-1]):
            if part not in node.children:
                subpath = Path(*path.parts[: i + 1])
                node.children[part] = DirNode(subpath)
            child = node.children[part]
            if not isinstance(child, DirNode):
                raise ValueError(
                    f"Cannot add path {path}. {node.children[part].path} is not a directory"
                )
            node = child
        part = path.parts[-1]
        node.children[part] = FileNode(path)

    @staticmethod
    def build_tree_from_paths(paths: list[Path]) -> "DirNode":
        root = DirNode(Path("."))
        for path in paths:
            root.add_file(path)
        return root
