import subprocess
from pathlib import Path

import pytest
from click.testing import CliRunner

from nava.cli import cli as nava_cli


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
    project_dir.mkdir()
    subprocess.run(["git", "init"], cwd=project_dir)
    return project_dir


@pytest.fixture
def cli():
    def fn(*args):
        runner = CliRunner()
        return runner.invoke(nava_cli, *args)

    return fn
