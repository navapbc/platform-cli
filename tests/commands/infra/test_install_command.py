from tests.lib import DirectoryContent, FileChange
from tests.lib.changeset import ChangeSet


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
                "test": {"infra_test.go": ""},
            },
        }
    )

    assert new_project.template_version == infra_template.short_version


def test_install_version(cli, infra_template, new_project):
    infra_template.version = "v0.1.0"

    ChangeSet(
        [
            FileChange("infra/modules/service/main.tf", "", "changed\n"),
            FileChange("infra/{{app_name}}/main.tf", "", "changed\n"),
        ]
    ).apply(infra_template.template_dir)
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

    assert new_project.template_version == "v0.1.0"
    assert (new_project.project_dir / "infra/modules/service/main.tf").read_text() == ""
    assert (new_project.project_dir / "infra/foo/main.tf").read_text() == ""
