import subprocess
from pathlib import Path

import pytest
from click.testing import CliRunner

from nava.cli import cli as nava_cli
from tests.lib import DirectoryContent
from nava import git

pytest.register_assert_rewrite("tests.lib.asserts")


@pytest.fixture
def template_directory_content() -> DirectoryContent:
    return DirectoryContent(
        {
            ".github": {
                "workflows": {
                    "ci-{{app_name}}-pr-environment-checks.yml": "",
                    "pr-environment-checks.yml": "",
                    "template-only-cd.yml": "",
                    "template-only-ci-infra.yml": "",
                },
            },
            ".template": {
                "{{_copier_conf.answers_file}}.jinja": "{{ _copier_answers|to_nice_yaml -}}",
            },
            "bin": {
                "publish-release": "",
            },
            "infra": {
                "{{app_name}}": {"main.tf": ""},
                "accounts": {"main.tf": ""},
                "modules": {
                    "database": {"main.tf": ""},
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
    )


@pytest.fixture
def tmp_template(tmp_path: Path, template_directory_content: DirectoryContent) -> Path:
    template_dir = tmp_path / "template"
    template_dir.mkdir()
    git.init(template_dir)

    template_directory_content.to_fs(str(template_dir))

    git.commit(template_dir)
    return template_dir


@pytest.fixture
def tmp_project(tmp_path: Path) -> Path:
    project_dir = tmp_path / "project"
    project_dir.mkdir()
    git.init(project_dir)
    return project_dir


@pytest.fixture
def cli():
    def fn(*args, **kwargs):
        runner = CliRunner()
        result = runner.invoke(nava_cli, *args, **kwargs)
        print(result.output)
        assert result.exit_code == 0
        return result

    return fn


@pytest.fixture
def clean_install(tmp_template, tmp_project, cli):
    cli(["infra", "install", str(tmp_template), str(tmp_project)])
    git.commit(tmp_project)
