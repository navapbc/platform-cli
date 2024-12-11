import subprocess
from contextlib import contextmanager
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Any, Generator, Self


class GitProject:
    def __init__(self, dir: Path):
        self.dir = Path(dir)

    @classmethod
    def from_existing(cls, dir: Path) -> Self | None:
        if not is_a_git_worktree(dir):
            return None

        return cls(dir)

    @classmethod
    @contextmanager
    def clone_if_necessary(cls, repo_uri: str) -> Generator[Self, None, None]:
        """Construct an instance, cloning given repo first if necessary.

        If ``repo_uri`` is remote, it will be cloned to a temporary directory
        that this removed on exit of the context.

        If ``repo_uri`` is a local path, it is not deleted on exit.
        """
        if Path(repo_uri).exists():
            yield cls(Path(repo_uri))
        else:
            with TemporaryDirectory() as dir:
                dir_path = Path(dir)
                clone_result = clone_to(repo_uri, dir_path)
                clone_result.check_returncode()

                yield cls(dir_path)

    def _run_cmd(self, *args: Any, **kwargs: Any) -> subprocess.CompletedProcess[str]:
        return run_text(*args, **kwargs, cwd=self.dir)

    def has_merge_conflicts(self) -> bool:
        result = self._run_cmd(
            [
                "git",
                "-c",
                "core.whitespace=-trailing-space,-space-before-tab,-indent-with-non-tab,-tab-in-indent,-cr-at-eol",
                "diff",
                "--check",
            ]
        )
        return result.returncode != 0

    def is_git(self) -> bool:
        return is_a_git_worktree(self.dir)

    def init(self) -> None:
        self._run_cmd(["git", "init", "--initial-branch=main"])

    def checkout(self, *args: str) -> subprocess.CompletedProcess[str]:
        return self._run_cmd(["git", "checkout"] + list(args))

    def add(self, *args: str) -> subprocess.CompletedProcess[str]:
        return self._run_cmd(["git", "add"] + list(args))

    def commit(self, msg: str) -> subprocess.CompletedProcess[str]:
        return self._run_cmd(["git", "commit", "-m", msg])

    def commit_all(self, msg: str) -> subprocess.CompletedProcess[str]:
        result = self.add(".")
        if result.returncode != 0:
            return result

        return self.commit(msg)

    def log(self, *args: str) -> subprocess.CompletedProcess[str]:
        return self._run_cmd(["git", "log"] + list(args))

    def reset(self, *args: str) -> subprocess.CompletedProcess[str]:
        return self._run_cmd(["git", "reset"] + list(args))

    def stash(self) -> None:
        self._run_cmd(["git", "stash"])

    def pop(self) -> None:
        self._run_cmd(["git", "stash", "pop"])

    def tag(self, tag: str) -> None:
        self._run_cmd(["git", "tag", tag])

    def rename_branch(self, new_branch_name: str) -> None:
        self._run_cmd(["git", "branch", "-m", new_branch_name])

    def get_commit_hash_for_head(self) -> str:
        return self._run_cmd(["git", "rev-parse", "HEAD"]).stdout.strip()

    def is_path_ignored(self, path: str) -> bool:
        result = self._run_cmd(["git", "check-ignore", "-q", path])
        if result.returncode not in (0, 1):
            result.check_returncode()

        return result.returncode == 0

    def get_tracked_files(self) -> list[Path]:
        tracked_files = [
            Path(file) for file in self._run_cmd(["git", "ls-files"]).stdout.splitlines()
        ]
        return tracked_files

    def get_untracked_files(self) -> list[str]:
        result = self._run_cmd(["git", "ls-files", "--exclude-standard", "--others"])
        return result.stdout.splitlines()

    def get_tags(self, *args: str) -> list[str]:
        result = self._run_cmd(["git", "tag"] + list(args))
        return result.stdout.splitlines()

    def get_closest_tag(self, commit_hash: str) -> str | None:
        result = self._run_cmd(
            ["git", "describe", "--exclude", commit_hash, "--contains", commit_hash]
        )

        if result.returncode != 0:
            return None

        first_tag = result.stdout.partition("~")[0]
        return first_tag

    def get_commit_description(self, commit_ish: str = "HEAD") -> str | None:
        result = self._run_cmd(["git", "describe", "--tags", "--always", commit_ish])

        if result.returncode != 0:
            return None

        return result.stdout.strip()


def is_a_git_worktree(dir: Path) -> bool:
    result = run_text(
        ["git", "rev-parse", "--is-inside-work-tree"],
        cwd=dir,
    )

    return result.stdout.strip() == "true"


# TODO: could use copier.vcs.clone?
def clone_to(url: str, dest: Path, ref: str | None = None) -> subprocess.CompletedProcess[str]:
    clone_result = run_text(["git", "clone", "--filter=blob:none", url, dest])

    if clone_result.returncode == 0:
        checkout_result = run_text(["git", "checkout", ref or "HEAD"], cwd=dest)
        return checkout_result

    return clone_result


def run_text(*args: Any, **kwargs: Any) -> subprocess.CompletedProcess[str]:
    return subprocess.run(*args, **kwargs, capture_output=True, text=True)
