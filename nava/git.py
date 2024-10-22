import subprocess
from pathlib import Path
from typing import Self


class GitProject:
    def __init__(self, dir: Path):
        self.dir = Path(dir)

    @classmethod
    def from_existing(cls, dir: Path) -> Self | None:
        if not is_a_git_worktree(dir):
            return None

        return cls(dir)

    def has_merge_conflicts(self) -> bool:
        result = subprocess.run(
            ["git", "diff", "--name-only", "--diff-filter=U"],
            cwd=self.dir,
            capture_output=True,
            text=True,
        )
        return bool(result.stdout)

    def is_git(self) -> bool:
        return is_a_git_worktree(self.dir)

    def init(self) -> None:
        subprocess.run(["git", "init", "--initial-branch=main"], cwd=self.dir)

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

    def is_path_ignored(self, path: str) -> bool:
        result = subprocess.run(["git", "check-ignore", "-q", path], cwd=self.dir)
        if result.returncode not in (0, 1):
            result.check_returncode()

        return result.returncode == 0

    def get_untracked_files(self) -> list[str]:
        result = subprocess.run(
            ["git", "ls-files", "--exclude-standard", "--others"],
            cwd=self.dir,
            capture_output=True,
            text=True,
        )
        return result.stdout.splitlines()


def is_a_git_worktree(dir: Path) -> bool:
    result = subprocess.run(
        ["git", "rev-parse", "--is-inside-work-tree"],
        cwd=dir,
        capture_output=True,
        text=True,
    )

    return result.stdout.strip() == "true"
