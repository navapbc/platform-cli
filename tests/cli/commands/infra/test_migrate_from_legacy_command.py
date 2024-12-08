import pytest

from nava.platform.cli.commands.infra import migrate_from_legacy_command, update_command
from nava.platform.cli.context import CliContext
from nava.platform.infra_project import InfraProject
from nava.platform.infra_template import InfraTemplate
from tests.lib import FileChange
from tests.lib.changeset import ChangeSet


@pytest.fixture
def legacy_project(infra_template: InfraTemplate, new_project: InfraProject) -> InfraProject:
    """
    Return a project with a clean install of the infra template
    but with the legacy .template-version file
    """
    infra_template.install(new_project, ["foo"])
    convert_project_to_legacy(new_project, infra_template.version)
    new_project.git_project.commit_all("Legacy install")
    return new_project


@pytest.fixture
def legacy_multi_app_project(
    infra_template: InfraTemplate, new_project: InfraProject
) -> InfraProject:
    """
    Return a project with multiple apps
    that has a legacy .template-version file
    """
    infra_template.install(new_project, ["foo"])
    infra_template.add_app(new_project, "bar")
    convert_project_to_legacy(new_project, infra_template.version)
    new_project.git_project.commit_all("Legacy install")
    return new_project


def test_migrate_from_legacy(
    infra_template: InfraTemplate, legacy_project: InfraProject, cli_context: CliContext
):
    project = legacy_project
    migrate_from_legacy_command.migrate_from_legacy(
        cli_context, str(project.project_dir), str(infra_template.template_dir)
    )
    project.git_project.commit_all("Migrate from legacy")

    ChangeSet(
        [
            FileChange("infra/modules/service/main.tf", "", "changed\n"),
            FileChange("infra/{{app_name}}/main.tf", "", "changed\n"),
        ]
    ).apply(infra_template.template_dir)
    infra_template.git_project.commit_all("Change template")

    update_command.update(cli_context, str(infra_template.template_dir), str(project.project_dir))

    assert project.template_version == infra_template.short_version
    assert (project.project_dir / "infra/modules/service/main.tf").read_text() == "changed\n"
    assert (project.project_dir / "infra/foo/main.tf").read_text() == "changed\n"


def test_migrate_from_legacy_with_multi_app_project(
    infra_template: InfraTemplate, legacy_multi_app_project: InfraProject, cli_context: CliContext
):
    project = legacy_multi_app_project
    migrate_from_legacy_command.migrate_from_legacy(
        cli_context, str(project.project_dir), str(infra_template.template_dir)
    )
    project.git_project.commit_all("Migrate from legacy")

    ChangeSet(
        [
            FileChange("infra/modules/service/main.tf", "", "changed\n"),
            FileChange("infra/{{app_name}}/main.tf", "", "changed\n"),
        ]
    ).apply(infra_template.template_dir)
    infra_template.git_project.commit_all("Change template")

    update_command.update(cli_context, str(infra_template.template_dir), str(project.project_dir))

    assert project.template_version == infra_template.short_version
    assert (project.project_dir / "infra/modules/service/main.tf").read_text() == "changed\n"
    assert (project.project_dir / "infra/foo/main.tf").read_text() == "changed\n"
    assert (project.project_dir / "infra/bar/main.tf").read_text() == "changed\n"


def convert_project_to_legacy(project: InfraProject, template_version: str) -> None:
    # Delete .infra-template folder
    for path in (project.project_dir / ".template-infra").iterdir():
        path.unlink()
    (project.project_dir / ".template-infra").rmdir()

    # Write legacy .template-version file
    (project.project_dir / ".template-version").write_text(template_version)
