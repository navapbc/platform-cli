import subprocess
from pathlib import Path


class GitProject:
    def __init__(self, dir: Path):
        self.dir = Path(dir)

    def init(self) -> None:
        subprocess.run(["git", "init"], cwd=self.dir)

    def commit(self, msg: str) -> None:
        subprocess.run(["git", "commit", "-m", msg], cwd=self.dir)

    def commit_all(self, msg: str) -> None:
        subprocess.run(["git", "add", "."], cwd=self.dir)
        self.commit(msg)

    def stash(self) -> None:
        subprocess.run(["git", "stash"], cwd=self.dir)

    def pop(self) -> None:
        subprocess.run(["git", "stash", "pop"], cwd=self.dir)

    def tag(self, tag: str) -> None:
        subprocess.run(["git", "tag", tag], cwd=self.dir)

    def rename_branch(self, new_branch_name: str) -> None:
        subprocess.run(["git", "branch", "-m", new_branch_name], cwd=self.dir)

    def get_commit_hash_for_head(self) -> str:
        return subprocess.run(
            ["git", "rev-parse", "HEAD"], cwd=self.dir, capture_output=True, text=True
        ).stdout.strip()
