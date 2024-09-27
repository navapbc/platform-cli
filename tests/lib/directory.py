from dataclasses import dataclass
import os
from collections import UserDict, UserString
from collections.abc import Mapping, MutableMapping
from typing import cast, Union

DirectoryConfig = Mapping[str, Union["DirectoryConfig", str]]


class File(UserString):

    def to_fs(self, path: str) -> None:
        with open(path, "w") as f:
            f.write(self.data)

    @staticmethod
    def from_fs(path: str) -> "File":
        with open(path) as f:
            contents = f.read()
        return File(contents)


class Directory(UserDict, MutableMapping[str, Union[File, "Directory"]]):

    def __init__(self, *args, **kwargs) -> None:
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
        super().__init__(*args, **kwargs)
        for key, value in self.data.items():
            if isinstance(value, str):
                self.data[key] = File(value)
            else:
                self.data[key] = Directory(value)

    def without(self, item: str) -> "Directory":
        """
        Return a new Directory object with the given item removed.
        """
        new_items = dict(self.data)
        del new_items[item]
        return Directory(new_items)

    def to_fs(self, root_dir: str) -> None:
        """
        Save the directory state to the filesystem within the given root directory.
        For each key in the configuration, if it's a directory, create the directory
        and recursively create its contents. If it's a file, create the file with the
        given contents.
        """
        for key, value in self.data.items():
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
