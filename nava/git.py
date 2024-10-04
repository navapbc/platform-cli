from pathlib import Path
import subprocess


class GitProject:
    def __init__(self, dir: Path):
        self.dir = Path(dir)

    def init(self) -> None:
        subprocess.run(["git", "init"], cwd=self.dir)

    def commit(self, msg: str) -> None:
        subprocess.run(["git", "add", "."], cwd=self.dir)
        subprocess.run(["git", "commit", "-m", msg], cwd=self.dir)

    def commit_hash(self) -> str:
        return subprocess.run(
            ["git", "rev-parse", "HEAD"], cwd=self.dir, capture_output=True, text=True
        ).stdout.strip()

    def stash(self) -> None:
        subprocess.run(["git", "stash"], cwd=self.dir)

    def pop(self) -> None:
        subprocess.run(["git", "stash", "pop"], cwd=self.dir)

    def tag(self, tag: str) -> None:
        subprocess.run(["git", "tag", tag], cwd=self.dir)


def init(dir: str | Path) -> None:
    subprocess.run(["git", "init"], cwd=dir)


def commit(dir: str | Path) -> None:
    subprocess.run(["git", "add", "."], cwd=dir)
    subprocess.run(["git", "commit", "-m", "commit msg"], cwd=dir)


def diff(dir: str | Path, path: str) -> str:
    return subprocess.run(
        ["git", "diff", "--", path], cwd=dir, capture_output=True, text=True
    ).stdout


def commit_hash(dir: str | Path) -> str:
    return subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=dir, capture_output=True, text=True
    ).stdout.strip()


def stash(dir: str | Path) -> None:
    subprocess.run(["git", "stash"], cwd=dir)


def pop(dir: str | Path) -> None:
    subprocess.run(["git", "stash", "pop"], cwd=dir)
