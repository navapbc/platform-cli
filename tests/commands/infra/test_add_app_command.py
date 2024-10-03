from tests.lib import DirectoryContent, FileChange, RenameChange
from tests.lib.changeset import ChangeSet


def test_add_app(cli, infra_template, new_project, clean_install):
    cli(
        [
            "infra",
            "add-app",
            str(new_project.project_dir),
            "bar",
            "--template-uri",
            str(infra_template.template_dir),
        ]
    )
    new_project.git_project.commit("Add app bar")

    dir_content = DirectoryContent.from_fs(new_project.project_dir, ignore=[".git"])

    assert dir_content.without(".template-infra") == DirectoryContent(
        {
            ".github": {
                "workflows": {
                    "ci-foo-pr-environment-checks.yml": "",
                    "ci-bar-pr-environment-checks.yml": "",
                    "pr-environment-checks.yml": "",
                },
            },
            "bin": {
                "publish-release": "",
            },
            "infra": {
                "foo": {"main.tf": ""},
                "bar": {"main.tf": ""},
                "accounts": {"main.tf": ""},
                "modules": {
                    "database": {"main.tf": ""},
                    "service": {"main.tf": ""},
                },
                "networks": {"main.tf": ""},
                "project-config": {"main.tf": ""},
                "test": {"infra_test.go": ""},
            },
        }
    )

    assert new_project.template_version == infra_template.short_version

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
    assert (new_project.project_dir / "infra/foo/main.tf").read_text() == "changed\n"
    assert (new_project.project_dir / "infra/bar/main.tf").read_text() == "changed\n"


def test_add_app_uses_existing_template_version(
    cli, infra_template, new_project, clean_install
):
    existing_template_version = new_project.template_version

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
            "add-app",
            str(new_project.project_dir),
            "bar",
            "--template-uri",
            str(infra_template.template_dir),
        ]
    )
    new_project.git_project.commit("Add app bar")

    assert new_project.template_version == existing_template_version
    assert (new_project.project_dir / "infra/modules/service/main.tf").read_text() == ""
    assert (new_project.project_dir / "infra/foo/main.tf").read_text() == ""
