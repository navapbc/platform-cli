from pathlib import Path

import pytest

from nava.platform.cli.context import CliContext
from nava.platform.projects.migrate_from_legacy_template import MigrateFromLegacyTemplate
from nava.platform.projects.project import Project
from nava.platform.util.git import GitProject
from tests.lib.new_directory import new_dir, new_dir_with_git


@pytest.fixture
def new_project_dir(tmp_path: Path) -> Path:
    return new_dir(tmp_path / "project")


@pytest.fixture
def new_project_dir_with_git(tmp_path: Path) -> GitProject:
    return new_dir_with_git(tmp_path / "project")


@pytest.fixture
def new_template_dir(tmp_path: Path) -> Path:
    return new_dir(tmp_path / "template")


@pytest.fixture
def new_template_dir_with_git(tmp_path: Path) -> GitProject:
    return new_dir_with_git(tmp_path / "template")


@pytest.fixture
def legacy_project_dir_with_git(
    new_project_dir_with_git: GitProject, new_template_dir_with_git: GitProject
) -> GitProject:
    (new_project_dir_with_git.dir / ".template-version").write_text(
        new_template_dir_with_git.get_commit_hash_for_head()
    )
    new_project_dir_with_git.commit_all("Legacy install")
    return new_project_dir_with_git


def test_migrate_from_legacy(
    new_template_dir_with_git: GitProject,
    legacy_project_dir_with_git: GitProject,
    cli_context: CliContext,
):
    project = Project(legacy_project_dir_with_git.dir)
    MigrateFromLegacyTemplate(
        ctx=cli_context,
        project=project,
        origin_template_uri=str(new_template_dir_with_git.dir),
        new_version_answers_file_name="foo.yml",
    ).migrate_from_legacy()
    project.git.commit_all("Migrate from legacy")

    assert (project.dir / ".template" / "foo.yml").exists()
