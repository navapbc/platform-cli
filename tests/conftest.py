import subprocess
from pathlib import Path

import pytest
from click.testing import CliRunner

from nava.cli import cli as nava_cli
from nava.infra_template import InfraTemplate
from nava.project import Project
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
            ".template-infra": {
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
                "test": {"infra_test.go": ""},
            },
            "template-only-bin": {
                "install-template": "",
                "destroy-account": "",
            },
        }
    )


@pytest.fixture
def infra_template(
    tmp_path: Path, template_directory_content: DirectoryContent
) -> InfraTemplate:
    template_dir = tmp_path / "template"
    template_dir.mkdir()
    template_directory_content.to_fs(str(template_dir))

    template = InfraTemplate(template_dir)
    template.git_project.init()
    template.git_project.commit("Initial commit")
    return template


@pytest.fixture
def new_project(tmp_path: Path) -> Project:
    project_dir = tmp_path / "project"
    project_dir.mkdir()
    project = Project(project_dir)
    project.git_project.init()
    return project


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
def clean_install(infra_template, new_project, cli):
    cli(
        [
            "infra",
            "install",
            str(new_project.project_dir),
            "--template-uri",
            str(infra_template.template_dir),
        ],
        input="foo\n",
    )
    new_project.git_project.commit("Install template")
