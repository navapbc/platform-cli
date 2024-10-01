from nava import git
from tests.lib import DirectoryContent, FileChange, RenameChange


def test_add_app(cli, tmp_template, tmp_project, clean_install):
    cli(["infra", "add-app", str(tmp_template), str(tmp_project), "bar"])
    git.commit(tmp_project)

    dir_content = DirectoryContent.from_fs(tmp_project, ignore=[".git"])

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

    assert ".template" in dir_content
    assert ".template-infra-app-foo.yml" in dir_content[".template"]
    assert ".template-infra-app-bar.yml" in dir_content[".template"]
    assert ".template-infra-base.yml" in dir_content[".template"]

    template_commit_hash = git.commit_hash(tmp_template)
    short_hash = template_commit_hash[:7]
    assert short_hash in dir_content[".template"][".template-infra-app-foo.yml"]
    assert short_hash in dir_content[".template"][".template-infra-app-bar.yml"]
    assert short_hash in dir_content[".template"][".template-infra-base.yml"]

    FileChange("infra/modules/service/main.tf", "", "changed\n").apply(tmp_template)
    FileChange("infra/{{app_name}}/main.tf", "", "changed\n").apply(tmp_template)
    git.commit(tmp_template)

    cli(["infra", "update", str(tmp_template), str(tmp_project)])

    dir_content = DirectoryContent.from_fs(tmp_project, ignore=[".git"])

    template_commit_hash = git.commit_hash(tmp_template)
    short_hash = template_commit_hash[:7]
    assert short_hash in dir_content[".template"][".template-infra-app-foo.yml"]
    assert short_hash in dir_content[".template"][".template-infra-app-bar.yml"]
    assert short_hash in dir_content[".template"][".template-infra-base.yml"]
    assert dir_content["infra"]["foo"]["main.tf"] == "changed\n"
    assert dir_content["infra"]["bar"]["main.tf"] == "changed\n"
