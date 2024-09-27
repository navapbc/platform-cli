from pathlib import Path
import subprocess


def init(dir: str | Path) -> None:
    subprocess.run(["git", "init"], cwd=dir)
