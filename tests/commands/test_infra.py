from tests.lib import DirectoryState

# Test cases

# test install
# check that all files and directories in the template directory are copied to the project directory except the excluded ones

# test update
# check that it's a no-op if the template version already matches

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
    cli(["infra", "install", str(tmp_template), str(tmp_project)])
    assert DirectoryState.from_fs(tmp_project) == DirectoryState({})
