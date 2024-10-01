import re
from nava import git
from tests.lib import DirectoryContent, FileChange, RenameChange


def test_update_no_change(cli, tmp_template, tmp_project, clean_install):
    content_before_update = DirectoryContent.from_fs(tmp_project, ignore=[".git"])

    cli(["infra", "update", str(tmp_template), str(tmp_project)])

    content_after_update = DirectoryContent.from_fs(tmp_project, ignore=[".git"])
    assert content_before_update == content_after_update


def test_update_with_change(cli, tmp_template, tmp_project, clean_install):
    content_before_update = DirectoryContent.from_fs(tmp_project, ignore=[".git"])

    FileChange("infra/modules/service/main.tf", "", "changed\n").apply(tmp_template)
    git.commit(tmp_template)

    cli(["infra", "update", str(tmp_template), str(tmp_project)])

    template_commit_hash = git.commit_hash(tmp_template)
    short_hash = template_commit_hash[:7]
    assert (
        f"_commit: {short_hash}"
        in (tmp_project / ".template/.template-infra-base.yml").read_text()
    )
    assert (
        f"_commit: {short_hash}"
        in (tmp_project / ".template/.template-infra-app-foo.yml").read_text()
    )
    assert (tmp_project / "infra/modules/service/main.tf").read_text() == "changed\n"
