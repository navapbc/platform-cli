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

    template_short_commit_hash = git.commit_hash(tmp_template)[:7]
    assert (
        template_short_commit_hash
        in (tmp_project / ".template/.template-infra-base.yml").read_text()
    )
    assert (
        template_short_commit_hash
        in (tmp_project / ".template/.template-infra-app-foo.yml").read_text()
    )

    diff = git.diff(tmp_project, "infra/modules/service/main.tf")
    expected_diff_regex = (
        r"diff --git a/infra/modules/service/main\.tf b/infra/modules/service/main\.tf"
        "\n"
        r".*"
        "\n"
        r"--- a/infra/modules/service/main\.tf"
        "\n"
        r"\+\+\+ b/infra/modules/service/main\.tf"
        "\n"
        r"@@ -0,0 \+1 @@"
        "\n"
        r"\+changed"
        "\n"
    )

    assert re.fullmatch(expected_diff_regex, diff) is not None
