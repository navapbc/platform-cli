from pathlib import Path
import subprocess


def init(dir: str | Path) -> None:
    subprocess.run(["git", "init"], cwd=dir)


def commit(dir: str | Path) -> None:
    subprocess.run(["git", "add", "."], cwd=dir)
    subprocess.run(["git", "commit", "-m", "commit msg"], cwd=dir)
