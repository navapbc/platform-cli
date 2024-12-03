from tests.lib import DirectoryContent, FileChange
from tests.lib.changeset import ChangeSet

INFRA_TEMPLATE_EXPECTED_CONTENT_FOR_APP_FOO = DirectoryContent(
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


def test_install_with_app_name_as_arg(cli, infra_template, new_project):
    cli(
        [
            "infra",
            "install",
            str(new_project.dir),
            "--template-uri",
            str(infra_template.template_dir),
        ],
        input="foo\n",
    )

    dir_content = DirectoryContent.from_fs(new_project.dir, ignore=[".git"])

    assert dir_content.without(".template-infra") == INFRA_TEMPLATE_EXPECTED_CONTENT_FOR_APP_FOO
    assert new_project.template_version == infra_template.commit


def test_install_with_data_app_name(cli, infra_template, new_project):
    cli(
        [
            "infra",
            "install",
            str(new_project.dir),
            "--template-uri",
            str(infra_template.template_dir),
            "--data",
            "app_name=foo",
        ],
    )

    dir_content = DirectoryContent.from_fs(new_project.dir, ignore=[".git"])

    assert dir_content.without(".template-infra") == INFRA_TEMPLATE_EXPECTED_CONTENT_FOR_APP_FOO
    assert new_project.template_version == infra_template.commit


def test_install_with_data_app_name_non_git_project(cli, infra_template, new_project_no_git):
    cli(
        [
            "infra",
            "install",
            str(new_project_no_git.dir),
            "--template-uri",
            str(infra_template.template_dir),
            "--data",
            "app_name=foo",
        ],
    )

    dir_content = DirectoryContent.from_fs(new_project_no_git.dir, ignore=[".git"])

    assert dir_content.without(".template-infra") == INFRA_TEMPLATE_EXPECTED_CONTENT_FOR_APP_FOO
    assert new_project_no_git.template_version == infra_template.commit


def test_install_with_data_app_name_same_as_existing_dir_non_git_project(
    cli, infra_template, new_project_no_git
):
    cli(
        [
            "infra",
            "install",
            str(new_project_no_git.dir),
            "--template-uri",
            str(infra_template.template_dir),
            "--data",
            "app_name=bin",
        ],
    )

    dir_content = DirectoryContent.from_fs(new_project_no_git.dir)

    assert dir_content.without(".template-infra") == DirectoryContent(
        {
            ".github": {
                "workflows": {
                    "ci-bin-pr-environment-checks.yml": "",
                    "pr-environment-checks.yml": "",
                },
            },
            "bin": {
                "publish-release": "",
            },
            "infra": {
                "bin": {"main.tf": ""},
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

    assert new_project_no_git.template_version == infra_template.commit


def test_install_infra_template_dirty(cli, infra_template_dirty, new_project):
    cli(
        [
            "infra",
            "install",
            str(new_project.dir),
            "--template-uri",
            str(infra_template_dirty.template_dir),
        ],
        input="foo\n",
    )

    dir_content = DirectoryContent.from_fs(new_project.dir, ignore=[".git"])

    assert "ignored_file.txt" not in dir_content
    assert "untracked_file.txt" not in dir_content

    assert new_project.template_version == infra_template_dirty.commit


def test_install_version(cli, infra_template, new_project):
    infra_template.git_project.tag("v0.1.0")

    ChangeSet(
        [
            FileChange("infra/modules/service/main.tf", "", "changed\n"),
            FileChange("infra/{{app_name}}/main.tf", "", "changed\n"),
        ]
    ).apply(infra_template.template_dir)
    infra_template.git_project.commit_all("Change template")

    infra_template.git_project.tag("v0.2.0")

    cli(
        [
            "infra",
            "install",
            str(new_project.dir),
            "--template-uri",
            str(infra_template.template_dir),
            "--version",
            "v0.1.0",
        ],
        input="foo\n",
    )

    assert new_project.template_version == "v0.1.0"
    assert (new_project.dir / "infra/modules/service/main.tf").read_text() == ""
    assert (new_project.dir / "infra/foo/main.tf").read_text() == ""


def test_install_with_other_data(cli, infra_template, new_project):
    ChangeSet(
        [
            FileChange("{{foo}}.txt", "", "new file\n"),
        ]
    ).apply(infra_template.template_dir)
    infra_template.git_project.commit_all("Change template")

    cli(
        [
            "infra",
            "install",
            str(new_project.dir),
            "--template-uri",
            str(infra_template.template_dir),
            "--data",
            "foo=bar",
        ],
        input="foo\n",
    )

    assert (new_project.dir / "bar.txt").read_text() == "new file\n"
