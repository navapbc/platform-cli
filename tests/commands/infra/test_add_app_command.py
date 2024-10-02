from tests.lib import DirectoryContent, FileChange, RenameChange


def test_add_app(cli, infra_template, new_project, clean_install):
    cli(
        [
            "infra",
            "add-app",
            str(infra_template.template_dir),
            str(new_project.project_dir),
            "bar",
        ]
    )
    new_project.git_project.commit("Add app bar")

    dir_content = DirectoryContent.from_fs(new_project.project_dir, ignore=[".git"])

    assert dir_content.without(".template") == DirectoryContent(
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
            },
        }
    )

    assert new_project.template_version == infra_template.short_version

    FileChange("infra/modules/service/main.tf", "", "changed\n").apply(
        infra_template.template_dir
    )
    FileChange("infra/{{app_name}}/main.tf", "", "changed\n").apply(
        infra_template.template_dir
    )
    infra_template.git_project.commit("Change template")

    cli(
        [
            "infra",
            "update",
            str(infra_template.template_dir),
            str(new_project.project_dir),
        ]
    )

    dir_content = DirectoryContent.from_fs(new_project.project_dir, ignore=[".git"])

    assert new_project.template_version == infra_template.short_version
    assert dir_content["infra"]["foo"]["main.tf"] == "changed\n"
    assert dir_content["infra"]["bar"]["main.tf"] == "changed\n"
