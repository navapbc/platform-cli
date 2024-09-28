from pathlib import Path
import subprocess


def init(dir: str | Path) -> None:
    subprocess.run(["git", "init"], cwd=dir)


def commit(dir: str | Path) -> None:
    subprocess.run(["git", "add", "."], cwd=dir)
    subprocess.run(["git", "commit", "-m", "commit msg"], cwd=dir)


def diff(dir: str | Path) -> str:
    return subprocess.run(
        ["git", "diff"], cwd=dir, capture_output=True, text=True
    ).stdout


def commit_hash(dir: str | Path) -> str:
    return subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=dir, capture_output=True, text=True
    ).stdout.strip()
