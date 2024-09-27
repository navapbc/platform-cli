import subprocess
from pathlib import Path

import pytest
from click.testing import CliRunner

from nava.cli import cli as nava_cli
from tests.lib import DirectoryContent
from tests.lib import git

pytest.register_assert_rewrite("tests.lib.asserts")


@pytest.fixture
def tmp_template(tmp_path: Path) -> Path:
    template_dir = tmp_path / "template"
    template_dir.mkdir()
    git.init(template_dir)

    DirectoryContent(
        {
            ".github": {
                "workflows": {
                    "ci-app-pr-environment-checks.yml": "",
                    "pr-environment-checks.yml": "",
                    "template-only-cd.yml": "",
                    "template-only-ci-infra.yml": "",
                },
            },
            "bin": {
                "publish-release": "",
            },
            "infra": {
                "app1": {"main.tf": ""},
                "app2": {"main.tf": ""},
                "accounts": {"main.tf": ""},
                "modules": {
                    "service": {"main.tf": ""},
                },
                "networks": {"main.tf": ""},
                "project-config": {"main.tf": ""},
            },
            "template-only-bin": {
                "install-template": "",
                "destroy-account": "",
            },
        }
    ).to_fs(str(template_dir))

    return template_dir


@pytest.fixture
def tmp_project(tmp_path: Path) -> Path:
    project_dir = tmp_path / "project"
    project_dir.mkdir()
    git.init(project_dir)
    return project_dir


@pytest.fixture
def cli():
    def fn(*args):
        runner = CliRunner()
        return runner.invoke(nava_cli, *args)

    return fn
