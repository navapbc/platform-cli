import logging
from collections.abc import Callable
from pathlib import Path
from typing import ParamSpec, TypeVar
from unittest.mock import create_autospec

import pytest
from typer.testing import CliRunner

from nava.platform.cli.context import CliContext
from nava.platform.cli.main import app as nava_cli
from nava.platform.projects.infra_project import InfraProject
from nava.platform.util.git import GitProject
from tests.lib import DirectoryContent
from tests.lib.changeset import ChangeSet, FileChange
from tests.lib.infra_template_writable import InfraTemplateWritable

pytest.register_assert_rewrite("tests.lib.asserts")

P = ParamSpec("P")
R = TypeVar("R")


def retain_pytest_handlers(f: Callable[P, R]) -> Callable[P, R]:
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
        pytest_handlers = [
            handler for handler in logging.root.handlers if handler.__module__ == "_pytest.logging"
        ]
        ret = f(*args, **kwargs)
        for handler in pytest_handlers:
            if handler not in logging.root.handlers:
                logging.root.addHandler(handler)
        return ret

    return wrapper


# borrowed from https://github.com/pytest-dev/pytest/discussions/11618#discussioncomment-9699934
@pytest.fixture(autouse=True)
def keep_pytest_handlers_during_dict_config(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(
        logging.config, "dictConfig", retain_pytest_handlers(logging.config.dictConfig)
    )


@pytest.fixture(autouse=True)
def disable_file_logging(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("LOG_TO_FILE", "false")


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
def infra_template_no_tags(
    tmp_path: Path,
    template_directory_content: DirectoryContent,
    cli_context: CliContext,
) -> InfraTemplateWritable:
    template_dir = tmp_path / "template"
    template_dir.mkdir()
    template_directory_content.to_fs(str(template_dir))

    git_project = GitProject(template_dir)
    git_project.init()
    git_project.commit_all("Initial commit")

    template = InfraTemplateWritable(cli_context, template_dir)

    return template


@pytest.fixture
def infra_template(infra_template_no_tags: InfraTemplateWritable) -> InfraTemplateWritable:
    template = infra_template_no_tags
    template.git_project.tag("v0.0.0")

    template.git_project.checkout("-b", "migration-tag")
    (template.template_dir / "migration-test.txt").write_text("foo")
    template.git_project.commit_all("Migration checkpoint")
    template.git_project.tag("platform-cli-migration/v0.0.0")
    template.git_project.checkout("main")

    return template


@pytest.fixture
def new_project_no_git(tmp_path: Path) -> InfraProject:
    project_dir = tmp_path / "project"
    project_dir.mkdir()
    project = InfraProject(project_dir)
    return project


@pytest.fixture
def new_project(new_project_no_git: InfraProject) -> InfraProject:
    project = new_project_no_git
    project.git.init()
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
            "--commit",
            "--template-uri",
            str(infra_template.template_dir),
            str(new_project.dir),
        ],
        input="foo\n",
    )


@pytest.fixture
def merge_conflict(infra_template: InfraTemplateWritable, new_project: InfraProject, clean_install):
    ChangeSet(
        [
            FileChange("infra/{{app_name}}/main.tf", "", "template app\n"),
            FileChange("infra/project-config/main.tf", "", "template project config\n"),
        ]
    ).apply(infra_template.template_dir)
    infra_template.git_project.commit_all("Change template")
    infra_template.git_project.tag("v0.1.0")

    ChangeSet(
        [
            FileChange("infra/foo/main.tf", "", "project app\n"),
            FileChange("infra/project-config/main.tf", "", "project config\n"),
        ]
    ).apply(new_project.dir)
    new_project.git.commit_all("Change project")


@pytest.fixture
def infra_template_dirty(
    infra_template: InfraTemplateWritable, new_project: InfraProject
) -> InfraTemplateWritable:
    dir_content = {
        ".gitignore": "ignored_file.txt",
        "ignored_file.txt": "foobar",
        "untracked_file.txt": "untracked content",
    }
    DirectoryContent(dir_content).to_fs(str(infra_template.template_dir))
    infra_template.git_project.add(".gitignore")
    infra_template.git_project.commit("Dirty state")

    return infra_template


@pytest.fixture
def cli_context(mocker) -> CliContext:
    # in Python 3.14 this could just be:
    #
    #   return create_autospec(CliContext, instance=True)  # type: ignore[no-any-return]
    #
    # see https://github.com/python/cpython/issues/124176

    import dataclasses

    fields = dataclasses.fields(CliContext)

    mock: CliContext = create_autospec(CliContext, instance=True)

    for f in fields:
        setattr(mock, f.name, create_autospec(f.type))

    return mock
