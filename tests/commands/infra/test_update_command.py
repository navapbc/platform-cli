import re
from nava import git
from tests.lib import DirectoryContent, FileChange, RenameChange


def test_update_no_change(cli, infra_template, new_project, clean_install):
    content_before_update = DirectoryContent.from_fs(
        new_project.project_dir, ignore=[".git"]
    )

    cli(
        [
            "infra",
            "update",
            str(infra_template.template_dir),
            str(new_project.project_dir),
        ]
    )

    content_after_update = DirectoryContent.from_fs(
        new_project.project_dir, ignore=[".git"]
    )
    assert content_before_update == content_after_update


def test_update_with_change(cli, infra_template, new_project, clean_install):
    content_before_update = DirectoryContent.from_fs(
        new_project.project_dir, ignore=[".git"]
    )

    FileChange("infra/modules/service/main.tf", "", "changed\n").apply(
        infra_template.template_dir
    )
    infra_template.git_project.commit("Change template")

    cli(
        [
            "infra",
            "update",
            str(infra_template.template_dir),
            str(new_project.project_dir),
        ]
    )

    dir_content = DirectoryContent.from_fs(new_project.project_dir, ignore=[".git"])

    short_hash = infra_template.short_version
    assert short_hash in dir_content[".template"][".template-infra-app-foo.yml"]
    assert short_hash in dir_content[".template"][".template-infra-base.yml"]
    assert dir_content["infra"]["modules"]["service"]["main.tf"] == "changed\n"
