from dataclasses import dataclass
import os
from collections import UserDict, UserString
from collections.abc import Mapping, MutableMapping
from typing import cast, Union


class FileContent(UserString):

    def to_fs(self, path: str) -> None:
        with open(path, "w") as f:
            f.write(self.data)

    @staticmethod
    def from_fs(path: str) -> "FileContent":
        with open(path) as f:
            contents = f.read()
        return FileContent(contents)


class DirectoryContent(
    UserDict, MutableMapping[str, Union[FileContent, "DirectoryContent"]]
):

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
                self.data[key] = FileContent(value)
            else:
                self.data[key] = DirectoryContent(value)

    def without(self, item: str) -> "DirectoryContent":
        """
        Return a new Directory object with the given item removed.
        """
        new_items = dict(self.data)
        del new_items[item]
        return DirectoryContent(new_items)

    def to_fs(self, root_dir: str) -> None:
        """
        Save the directory state to the filesystem within the given root directory.
        For each key in the configuration, if it's a directory, create the directory
        and recursively create its contents. If it's a file, create the file with the
        given contents.
        """
        for key, value in self.data.items():
            path = os.path.join(root_dir, key)
            if isinstance(value, FileContent):
                value.to_fs(path)
            else:
                assert isinstance(value, DirectoryContent)
                os.makedirs(path)
                value.to_fs(path)

    @staticmethod
    def from_fs(path: str) -> "DirectoryContent":
        """
        Given a directory, return a DirectoryState object that represents its contents
        """
        config = DirectoryContent({})
        for name in os.listdir(path):
            subpath = os.path.join(path, name)
            if os.path.isdir(subpath):
                config[name] = DirectoryContent.from_fs(subpath)
            else:
                config[name] = FileContent.from_fs(subpath)
        return config
