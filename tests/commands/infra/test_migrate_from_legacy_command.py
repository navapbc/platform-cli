from nava.commands.infra import migrate_from_legacy_command, update_command
from nava.infra_template import InfraTemplate
from nava.project import Project
from tests.lib import FileChange
from tests.lib.changeset import ChangeSet


def test_migrate_from_legacy(cli, infra_template: InfraTemplate, legacy_project: Project):
    migrate_from_legacy_command.migrate_from_legacy(
        str(legacy_project.project_dir), str(infra_template.template_dir)
    )
    legacy_project.git_project.commit("Migrate from legacy")

    print("infra_template.version")
    print(infra_template.version)

    ChangeSet(
        [
            FileChange("infra/modules/service/main.tf", "", "changed\n"),
            FileChange("infra/{{app_name}}/main.tf", "", "changed\n"),
        ]
    ).apply(infra_template.template_dir)
    infra_template.git_project.commit("Change template")

    update_command.update(str(infra_template.template_dir), str(legacy_project.project_dir))

    assert legacy_project.template_version == infra_template.short_version
    assert (legacy_project.project_dir / "infra/modules/service/main.tf").read_text() == "changed\n"
    assert (legacy_project.project_dir / "infra/foo/main.tf").read_text() == "changed\n"


# def test_update_multiapp_project_with_legacy_version_file(cli, infra_template: InfraTemplate, legacy_project: Project):
#     ChangeSet(
#         [
#             FileChange("infra/modules/service/main.tf", "", "changed\n"),
#             FileChange("infra/{{app_name}}/main.tf", "", "changed\n"),
#         ]
#     ).apply(infra_template.template_dir)
#     infra_template.git_project.commit("Change template")

#     cli(
#         [
#             "infra",
#             "update",
#             str(legacy_project.project_dir),
#             "--template-uri",
#             str(infra_template.template_dir),
#         ]
#     )

#     assert legacy_project.template_version == infra_template.short_version
#     assert (legacy_project.project_dir / "infra/modules/service/main.tf").read_text() == "changed\n"
#     assert (legacy_project.project_dir / "infra/foo/main.tf").read_text() == "changed\n"
