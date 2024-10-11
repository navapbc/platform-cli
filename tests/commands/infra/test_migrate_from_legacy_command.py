import pytest

from nava.commands.infra import migrate_from_legacy_command, update_command
from nava.infra_template import InfraTemplate
from nava.project import Project
from tests.lib import FileChange
from tests.lib.changeset import ChangeSet


@pytest.fixture
def legacy_project(infra_template: InfraTemplate, new_project: Project, cli) -> Project:
    """
    Return a project with a clean install of the infra template
    but with the legacy .template-version file
    """
    infra_template.install(new_project, ["foo"])
    convert_project_to_legacy(new_project, infra_template.version)
    new_project.git_project.commit_all("Legacy install")
    return new_project


@pytest.fixture
def legacy_multi_app_project(infra_template: InfraTemplate, new_project: Project, cli) -> Project:
    """
    Return a project with multiple apps
    that has a legacy .template-version file
    """
    infra_template.install(new_project, ["foo"])
    infra_template.add_app(new_project, "bar")
    convert_project_to_legacy(new_project, infra_template.version)
    new_project.git_project.commit_all("Legacy install")
    return new_project


def test_migrate_from_legacy(cli, infra_template: InfraTemplate, legacy_project: Project):
    project = legacy_project
    migrate_from_legacy_command.migrate_from_legacy(
        str(project.project_dir), str(infra_template.template_dir)
    )
    project.git_project.commit_all("Migrate from legacy")

    ChangeSet(
        [
            FileChange("infra/modules/service/main.tf", "", "changed\n"),
            FileChange("infra/{{app_name}}/main.tf", "", "changed\n"),
        ]
    ).apply(infra_template.template_dir)
    infra_template.git_project.commit_all("Change template")

    update_command.update(str(infra_template.template_dir), str(project.project_dir))

    assert project.template_version == infra_template.short_version
    assert (project.project_dir / "infra/modules/service/main.tf").read_text() == "changed\n"
    assert (project.project_dir / "infra/foo/main.tf").read_text() == "changed\n"


def test_migrate_from_legacy_with_multi_app_project(
    cli, infra_template: InfraTemplate, legacy_multi_app_project: Project
):
    project = legacy_multi_app_project
    migrate_from_legacy_command.migrate_from_legacy(
        str(project.project_dir), str(infra_template.template_dir)
    )
    project.git_project.commit_all("Migrate from legacy")

    ChangeSet(
        [
            FileChange("infra/modules/service/main.tf", "", "changed\n"),
            FileChange("infra/{{app_name}}/main.tf", "", "changed\n"),
        ]
    ).apply(infra_template.template_dir)
    infra_template.git_project.commit_all("Change template")

    update_command.update(str(infra_template.template_dir), str(project.project_dir))

    assert project.template_version == infra_template.short_version
    assert (project.project_dir / "infra/modules/service/main.tf").read_text() == "changed\n"
    assert (project.project_dir / "infra/foo/main.tf").read_text() == "changed\n"
    assert (project.project_dir / "infra/bar/main.tf").read_text() == "changed\n"


def convert_project_to_legacy(project: Project, template_version: str) -> None:
    # Delete .infra-template folder
    for path in (project.project_dir / ".template-infra").iterdir():
        path.unlink()
    (project.project_dir / ".template-infra").rmdir()

    # Write legacy .template-version file
    (project.project_dir / ".template-version").write_text(template_version)
