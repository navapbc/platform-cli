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
def new_template_dir_with_git_and_content(new_template_dir_with_git: GitProject) -> GitProject:
    template_git = new_template_dir_with_git

    (template_git.dir / "foo.txt").write_text("bar")
    template_git.commit_all("Initial commit")

    return template_git


@pytest.fixture
def legacy_project_dir_with_git(
    new_project_dir_with_git: GitProject, new_template_dir_with_git_and_content: GitProject
) -> GitProject:
    template_git = new_template_dir_with_git_and_content

    (new_project_dir_with_git.dir / ".template-version").write_text(
        template_git.get_commit_hash_for_head() or "foobar"
    )
    new_project_dir_with_git.commit_all("Legacy install")

    return new_project_dir_with_git


def test_migrate_from_legacy_preserve_legacy_file(
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
    ).migrate_from_legacy(preserve_legacy_file=True)

    # both new and legacy file should exist
    assert (project.dir / ".template" / "foo.yml").exists()
    assert (project.dir / ".template-version").exists()


def test_migrate_from_legacy_no_commit(
    new_template_dir_with_git: GitProject,
    legacy_project_dir_with_git: GitProject,
    cli_context: CliContext,
):
    project = Project(legacy_project_dir_with_git.dir)
    commit_count_before = project.git.get_commit_count()

    MigrateFromLegacyTemplate(
        ctx=cli_context,
        project=project,
        origin_template_uri=str(new_template_dir_with_git.dir),
        new_version_answers_file_name="foo.yml",
    ).migrate_from_legacy(commit=False)

    commit_count_after = project.git.get_commit_count()

    # only new file should exist
    assert (project.dir / ".template" / "foo.yml").exists()
    assert not (project.dir / ".template-version").exists()
    # there should be no additional commits
    assert commit_count_after == commit_count_before


def test_migrate_from_legacy_commit(
    new_template_dir_with_git: GitProject,
    legacy_project_dir_with_git: GitProject,
    cli_context: CliContext,
):
    project = Project(legacy_project_dir_with_git.dir)
    commit_count_before = project.git.get_commit_count() or 0

    MigrateFromLegacyTemplate(
        ctx=cli_context,
        project=project,
        origin_template_uri=str(new_template_dir_with_git.dir),
        new_version_answers_file_name="foo.yml",
    ).migrate_from_legacy(commit=True)

    commit_count_after = project.git.get_commit_count()

    # only new file should exist
    assert (project.dir / ".template" / "foo.yml").exists()
    assert not (project.dir / ".template-version").exists()
    # there should be an additional commits
    assert commit_count_after == commit_count_before + 1
    # with a clean repo
    assert len(project.git.get_untracked_files()) == 0
