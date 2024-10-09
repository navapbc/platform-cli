from tests.lib import DirectoryContent, FileChange
from tests.lib.changeset import ChangeSet


def test_update_no_change(cli, infra_template, new_project, clean_install):
    content_before_update = DirectoryContent.from_fs(new_project.project_dir, ignore=[".git"])

    cli(
        [
            "infra",
            "update",
            str(new_project.project_dir),
            "--template-uri",
            str(infra_template.template_dir),
        ]
    )

    content_after_update = DirectoryContent.from_fs(new_project.project_dir, ignore=[".git"])
    assert content_before_update == content_after_update


def test_update_with_template_change(cli, infra_template, new_project, clean_install):
    ChangeSet(
        [
            FileChange("infra/modules/service/main.tf", "", "changed\n"),
            FileChange("infra/{{app_name}}/main.tf", "", "changed\n"),
        ]
    ).apply(infra_template.template_dir)
    infra_template.git_project.commit("Change template")

    cli(
        [
            "infra",
            "update",
            str(new_project.project_dir),
            "--template-uri",
            str(infra_template.template_dir),
        ]
    )

    assert new_project.template_version == infra_template.short_version
    assert (new_project.project_dir / "infra/modules/service/main.tf").read_text() == "changed\n"
    assert (new_project.project_dir / "infra/foo/main.tf").read_text() == "changed\n"


def test_update_with_project_change(cli, infra_template, new_project, clean_install):
    ChangeSet([FileChange("infra/foo/main.tf", "", "project change\n")]).apply(
        new_project.project_dir
    )
    new_project.git_project.commit("Change project")

    ChangeSet([FileChange("infra/modules/service/main.tf", "", "template change\n")]).apply(
        infra_template.template_dir
    )
    infra_template.git_project.commit("Change template")

    cli(
        [
            "infra",
            "update",
            str(new_project.project_dir),
            "--template-uri",
            str(infra_template.template_dir),
        ]
    )

    assert new_project.template_version == infra_template.short_version
    assert (new_project.project_dir / "infra/foo/main.tf").read_text() == "project change\n"
    assert (
        new_project.project_dir / "infra/modules/service/main.tf"
    ).read_text() == "template change\n"
