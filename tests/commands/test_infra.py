from tests.lib import DirectoryContent, FileChange, RenameChange, git

# Remaining test cases to implement

# test update
# start with a clean install of the template
# make a change to the template
# run update
# check that the change is reflected in the project directory

# test update
# start with a clean install of the template
# make a change to the project
# make a change to the template
# run update
# check that the change to the project is preserved and that the template change is also reflected in the project directory

# test add app
# start with a clean install of the template
# add an app
# check that the new folder was added

# test add app and update
#


def test_install(cli, tmp_template, tmp_project):
    cli(["infra", "install", str(tmp_template), str(tmp_project)], input="foo\n")

    dir_content = DirectoryContent.from_fs(tmp_project)

    assert dir_content.without(".git").without(".template") == DirectoryContent(
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

    assert ".template" in dir_content
    assert ".template-infra-app-foo.yml" in dir_content[".template"]
    assert ".template-infra-base.yml" in dir_content[".template"]

    template_commit_hash = git.commit_hash(tmp_template)
    short_hash = template_commit_hash[:7]
    assert short_hash in dir_content[".template"][".template-infra-app-foo.yml"]
    assert short_hash in dir_content[".template"][".template-infra-base.yml"]


def test_update_no_change(cli, tmp_template, tmp_project, clean_install):
    content_before_update = DirectoryContent.from_fs(tmp_project)

    cli(["infra", "update", str(tmp_template), str(tmp_project)])

    content_after_update = DirectoryContent.from_fs(tmp_project)
    assert content_before_update == content_after_update


# def test_update_with_change(cli, tmp_template, tmp_project, clean_install):
#     content_before_update = DirectoryContent.from_fs(tmp_project)

#     FileChange("infra/modules/service/main.tf", "", "changed").apply(tmp_template)

#     cli(["infra", "update", str(tmp_template), str(tmp_project)])

#     assert (
#         git.diff(tmp_project)
#         == """diff --git a/tests/commands/test_infra.py b/tests/commands/test_infra.py
# index 991c4e3..e788003 100644
# --- a/tests/commands/test_infra.py
# +++ b/tests/commands/test_infra.py
# +        changed
# """
#     )
