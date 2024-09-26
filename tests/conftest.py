import pytest
from pathlib import Path
import subprocess


@pytest.fixture
def tmp_template(tmp_path: Path) -> Path:
    infra_dir = tmp_path / "infra"
    infra_dir.mkdir()
    (infra_dir / "app1").mkdir()
    (infra_dir / "app2").mkdir()
    (infra_dir / "accounts").mkdir()
    (infra_dir / "modules").mkdir()
    (infra_dir / "networks").mkdir()
    (infra_dir / "project-config").mkdir()
    subprocess.run(["git", "init"], cwd=tmp_path)
    return tmp_path


@pytest.fixture
def tmp_project(tmp_path: Path) -> Path:
    subprocess.run(["git", "init"], cwd=tmp_path)
    return tmp_path
