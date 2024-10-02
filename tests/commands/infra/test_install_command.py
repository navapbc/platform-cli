from nava import git
from tests.lib import DirectoryContent, FileChange, RenameChange

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


def test_install(cli, infra_template, new_project):
    cli(
        [
            "infra",
            "install",
            str(infra_template.template_dir),
            str(new_project.project_dir),
        ],
        input="foo\n",
    )

    dir_content = DirectoryContent.from_fs(new_project.project_dir, ignore=[".git"])

    assert dir_content.without(".template") == DirectoryContent(
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

    short_hash = infra_template.short_version
    assert short_hash in dir_content[".template"][".template-infra-app-foo.yml"]
    assert short_hash in dir_content[".template"][".template-infra-base.yml"]
