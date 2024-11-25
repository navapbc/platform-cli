from pathlib import Path

from nava.platform.util.git import GitProject


def new_dir(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    return path


def new_dir_with_git(path: Path) -> GitProject:
    git = GitProject(new_dir(path))
    git.init()
    return git
