from nava import git
from tests.lib import DirectoryContent, FileChange, RenameChange

# Remaining test cases to implement

# test update
# start with a clean install of the template
# make a change to the project
# make a change to the template
# run update
# check that the change to the project is preserved and that the template change is also reflected in the project directory

# test add_app
# make sure app that is added is using the same version as the rest of the app
# install template
# make a change to the template
# add app
# check that the app is using the original version of the template


def test_install(cli, infra_template, new_project):
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

    dir_content = DirectoryContent.from_fs(new_project.project_dir, ignore=[".git"])

    assert dir_content.without(".template-infra") == DirectoryContent(
        {
            ".github": {
                "workflows": {
                    "ci-foo-pr-environment-checks.yml": "",
                    "pr-environment-checks.yml": "",
                },
            },
            "bin": {
                "publish-release": "",
            },
            "infra": {
                "foo": {"main.tf": ""},
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


def test_install_version(cli, infra_template, new_project):
    infra_template.version = "v0.1.0"

    FileChange("infra/modules/service/main.tf", "", "changed\n").apply(
        infra_template.template_dir
    )
    FileChange("infra/{{app_name}}/main.tf", "", "changed\n").apply(
        infra_template.template_dir
    )
    infra_template.git_project.commit("Change template")

    infra_template.version = "v0.2.0"

    cli(
        [
            "infra",
            "install",
            str(new_project.project_dir),
            "--template-uri",
            str(infra_template.template_dir),
            "--version",
            "v0.1.0",
        ],
        input="foo\n",
    )

    assert new_project.template_version == infra_template.short_version
    assert (new_project.project_dir / "infra/modules/service/main.tf").read_text() == ""
    assert (new_project.project_dir / "infra/foo/main.tf").read_text() == ""
