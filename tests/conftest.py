import pytest
from pathlib import Path
import subprocess


@pytest.fixture
def tmp_template(tmp_path: Path) -> Path:
    template_dir = tmp_path / "template"
    template_dir.mkdir()
    infra_dir = template_dir / "infra"
    infra_dir.mkdir()
    (infra_dir / "app1").mkdir()
    (infra_dir / "app2").mkdir()
    (infra_dir / "accounts").mkdir()
    (infra_dir / "modules").mkdir()
    (infra_dir / "networks").mkdir()
    (infra_dir / "project-config").mkdir()
    subprocess.run(["git", "init"], cwd=template_dir)
    return template_dir


@pytest.fixture
def tmp_project(tmp_path: Path) -> Path:
    project_dir = tmp_path / "project"
    subprocess.run(["git", "init"], cwd=project_dir)
    return project_dir
