from dataclasses import dataclass
import os
from collections.abc import Mapping, MutableMapping
from typing import cast, Union

DirectoryConfig = Mapping[str, Union["DirectoryConfig", str]]


@dataclass
class File:
    contents: str

    def __init__(self, contents: str) -> None:
        self.contents = contents

    def to_fs(self, path: str) -> None:
        with open(path, "w") as f:
            f.write(self.contents)

    @staticmethod
    def from_fs(path: str) -> "File":
        with open(path) as f:
            contents = f.read()
        return File(contents)


@dataclass
class Directory:
    items: MutableMapping[str, Union[File, "Directory"]]

    def __init__(self, config: DirectoryConfig) -> None:
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
        self.items: MutableMapping[str, File | Directory] = {}
        for key, value in config.items():
            if isinstance(value, str):
                self.items[key] = File(value)
            else:
                self.items[key] = Directory(value)

    def to_fs(self, root_dir: str) -> None:
        """
        Save the directory state to the filesystem within the given root directory.
        For each key in the configuration, if it's a directory, create the directory
        and recursively create its contents. If it's a file, create the file with the
        given contents.
        """
        for key, value in self.items.items():
            path = os.path.join(root_dir, key)
            if isinstance(value, File):
                value.to_fs(path)
            else:
                assert isinstance(value, Directory)
                os.makedirs(path)
                value.to_fs(path)

    @staticmethod
    def from_fs(root_dir: str) -> "Directory":
        """
        Given a directory, return a DirectoryState object that represents its contents
        """
        config = cast(DirectoryConfig, Directory.config_from_fs(root_dir))
        return Directory(config)

    @staticmethod
    def config_from_fs(path: str) -> DirectoryConfig | str:
        """
        Given a directory, return a DirectoryState config that can be used to create a
        DirectoryState object that represents the directory's contents
        """
        config = {}
        for name in os.listdir(path):
            subpath = os.path.join(path, name)
            if os.path.isdir(subpath):
                config[name] = Directory.config_from_fs(subpath)
            else:
                with open(subpath) as f:
                    contents = f.read()
                config[name] = contents
        return config
