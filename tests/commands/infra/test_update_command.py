from tests.lib import DirectoryContent, FileChange, RenameChange, git


def test_update_no_change(cli, tmp_template, tmp_project, clean_install):
    content_before_update = DirectoryContent.from_fs(tmp_project, ignore=[".git"])

    cli(["infra", "update", str(tmp_template), str(tmp_project)])

    content_after_update = DirectoryContent.from_fs(tmp_project, ignore=[".git"])
    assert content_before_update == content_after_update


# def test_update_with_change(cli, tmp_template, tmp_project, clean_install):
#     content_before_update = DirectoryContent.from_fs(tmp_project, ignore=[".git"])

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
