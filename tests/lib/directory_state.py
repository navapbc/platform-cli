from dataclasses import dataclass
import os
from collections.abc import Mapping, MutableMapping
from typing import cast, Union

DirectoryStateConfig = Mapping[str, Union["DirectoryStateConfig", str]]


@dataclass
class FileState:
    def __init__(self, contents: str) -> None:
        self.contents = contents

    def to_fs(self, path: str) -> None:
        with open(path, "w") as f:
            f.write(self.contents)

    @staticmethod
    def from_fs(path: str) -> "FileState":
        with open(path) as f:
            contents = f.read()
        return FileState(contents)


@dataclass
class DirectoryState:
    def __init__(self, config: DirectoryStateConfig) -> None:
        """
        Given a configuration like the following, initialize the directory state.
        {
            "dir1": {
                "dir2": {
                    "file2": "file2 contents"
                },
                "file3": "file3 contents"
            },
            "file1": "file1 contents"
        }
        """
        self.items: MutableMapping[str, FileState | DirectoryState] = {}
        for key, value in config.items():
            if isinstance(value, str):
                self.items[key] = FileState(value)
            else:
                self.items[key] = DirectoryState(value)

    def to_fs(self, root_dir: str) -> None:
        """
        Save the directory state to the filesystem within the given root directory.
        For each key in the configuration, if it's a directory, create the directory
        and recursively create its contents. If it's a file, create the file with the
        given contents.
        """
        for key, value in self.items.items():
            path = os.path.join(root_dir, key)
            if isinstance(value, FileState):
                value.to_fs(path)
            else:
                assert isinstance(value, DirectoryState)
                os.makedirs(path)
                value.to_fs(path)

    @staticmethod
    def from_fs(root_dir: str) -> "DirectoryState":
        """
        Given a directory, return a DirectoryState object that represents its contents
        """
        config = cast(DirectoryStateConfig, DirectoryState.config_from_fs(root_dir))
        return DirectoryState(config)

    @staticmethod
    def config_from_fs(path: str) -> DirectoryStateConfig | str:
        """
        Given a directory, return a DirectoryState config that can be used to create a
        DirectoryState object that represents the directory's contents
        """
        config = {}
        for name in os.listdir(path):
            subpath = os.path.join(path, name)
            if os.path.isdir(subpath):
                config[name] = DirectoryState.config_from_fs(subpath)
            else:
                with open(subpath) as f:
                    contents = f.read()
                config[name] = contents
        return config
