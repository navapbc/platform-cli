from pathlib import Path

import pytest
from click.testing import CliRunner

from nava.platform.cli.main import cli as nava_cli
from nava.platform.infra_template import InfraTemplate
from nava.platform.project import Project
from nava.platform.util.git import GitProject
from tests.lib import DirectoryContent
from tests.lib.changeset import ChangeSet, FileChange

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
def infra_template(tmp_path: Path, template_directory_content: DirectoryContent) -> InfraTemplate:
    template_dir = tmp_path / "template"
    template_dir.mkdir()
    template_directory_content.to_fs(str(template_dir))

    git_project = GitProject(template_dir)
    git_project.init()
    git_project.commit_all("Initial commit")

    template = InfraTemplate(template_dir)

    # Temporarily rename main to lorenyu/platform-cli since the rollout plan
    # for the Platform CLI will temporarily default the --version option
    # to lorenyu/platform-cli, so we want our tests to reflect that.
    # TODO: Remove this once the rollout plan is complete
    template.git_project.rename_branch("lorenyu/platform-cli")
    return template


@pytest.fixture
def new_project_no_git(tmp_path: Path) -> Project:
    project_dir = tmp_path / "project"
    project_dir.mkdir()
    project = Project(project_dir)
    return project


@pytest.fixture
def new_project(new_project_no_git: Project) -> Project:
    project = new_project_no_git
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
    new_project.git_project.commit_all("Install template")


@pytest.fixture
def merge_conflict(infra_template: InfraTemplate, new_project: Project, clean_install):
    ChangeSet(
        [
            FileChange("infra/{{app_name}}/main.tf", "", "template app\n"),
            FileChange("infra/project-config/main.tf", "", "template project config\n"),
        ]
    ).apply(infra_template.template_dir)
    infra_template.git_project.commit_all("Change template")

    ChangeSet(
        [
            FileChange("infra/foo/main.tf", "", "project app\n"),
            FileChange("infra/project-config/main.tf", "", "project config\n"),
        ]
    ).apply(new_project.project_dir)
    new_project.git_project.commit_all("Change project")


@pytest.fixture
def infra_template_dirty(infra_template: InfraTemplate, new_project: Project) -> InfraTemplate:
    dir_content = {
        ".gitignore": "ignored_file.txt",
        "ignored_file.txt": "foobar",
        "untracked_file.txt": "untracked content",
    }
    DirectoryContent(dir_content).to_fs(str(infra_template.template_dir))
    infra_template.git_project.add(".gitignore")
    infra_template.git_project.commit("Dirty state")

    return infra_template
