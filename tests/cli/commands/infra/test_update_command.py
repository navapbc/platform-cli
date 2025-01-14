import pytest
from copier.errors import DirtyLocalWarning
from typer.testing import CliRunner

from nava.platform.cli.main import app as nava_cli
from nava.platform.projects.infra_project import InfraProject
from tests.lib import DirectoryContent, FileChange
from tests.lib.changeset import ChangeSet
from tests.lib.infra_template_writable import InfraTemplateWritable


def test_update_no_change(cli, infra_template, new_project, clean_install):
    content_before_update = DirectoryContent.from_fs(new_project.dir, ignore=[".git"])

    cli(
        [
            "infra",
            "update",
            str(new_project.dir),
            "--template-uri",
            str(infra_template.template_dir),
        ]
    )

    content_after_update = DirectoryContent.from_fs(new_project.dir, ignore=[".git"])
    assert content_before_update == content_after_update


def test_update_with_template_change(cli, infra_template, new_project, clean_install):
    ChangeSet(
        [
            FileChange("infra/modules/service/main.tf", "", "changed\n"),
            FileChange("infra/{{app_name}}/main.tf", "", "changed\n"),
        ]
    ).apply(infra_template.template_dir)
    infra_template.git_project.commit_all("Change template")
    infra_template.git_project.tag("v0.1.0")

    cli(
        [
            "infra",
            "update",
            str(new_project.dir),
            "--template-uri",
            str(infra_template.template_dir),
        ]
    )

    assert new_project.template_version == infra_template.commit
    assert (new_project.dir / "infra/modules/service/main.tf").read_text() == "changed\n"
    assert (new_project.dir / "infra/foo/main.tf").read_text() == "changed\n"


@pytest.mark.skip(reason="is flaky")
def test_update_with_dirty_template(cli, clean_install, infra_template_dirty, new_project):
    cli(
        [
            "infra",
            "update",
            str(new_project.dir),
            "--template-uri",
            str(infra_template_dirty.template_dir),
        ],
        input="foo\n",
    )

    dir_content = DirectoryContent.from_fs(new_project.dir, ignore=[".git"])

    assert "ignored_file.txt" not in dir_content
    # if repo doesn't have a tag/no version is specified, copier defaults to
    # HEAD, for which it includes dirty changes
    assert "untracked_file.txt" in dir_content

    # TODO: this inconsistently fails running `new_project.template_version` as
    # the base and app versions in the answer file ends up different somehow,
    # but not always
    assert new_project.template_version == infra_template_dirty.commit


def test_update_with_dirty_template_with_version(
    cli, clean_install, infra_template_dirty, new_project
):
    tag_name = "dirty-version"
    infra_template_dirty.git_project.tag(tag_name)

    with pytest.warns(DirtyLocalWarning):
        cli(
            [
                "infra",
                "update",
                str(new_project.dir),
                "--template-uri",
                str(infra_template_dirty.template_dir),
                "--version",
                tag_name,
            ],
            input="foo\n",
        )

    dir_content = DirectoryContent.from_fs(new_project.dir, ignore=[".git"])

    assert "ignored_file.txt" not in dir_content
    # when specifying a version, copier does not include untracked changes
    assert "untracked_file.txt" not in dir_content

    assert new_project.template_version == tag_name


def test_update_with_project_change(
    cli, infra_template: InfraTemplateWritable, new_project: InfraProject, clean_install
):
    ChangeSet([FileChange("infra/foo/main.tf", "", "project change\n")]).apply(new_project.dir)
    new_project.git.commit_all("Change project")

    ChangeSet([FileChange("infra/modules/service/main.tf", "", "template change\n")]).apply(
        infra_template.template_dir
    )
    infra_template.git_project.commit_all("Change template")
    infra_template.git_project.tag("v0.1.0")

    cli(
        [
            "infra",
            "update",
            str(new_project.dir),
            "--template-uri",
            str(infra_template.template_dir),
        ]
    )

    assert new_project.template_version == infra_template.commit
    assert (new_project.dir / "infra/foo/main.tf").read_text() == "project change\n"
    assert (new_project.dir / "infra/modules/service/main.tf").read_text() == "template change\n"


def test_update_with_merge_conflict(
    cli, infra_template: InfraTemplateWritable, new_project: InfraProject, merge_conflict
):
    runner = CliRunner()
    result = runner.invoke(
        nava_cli,
        [
            "infra",
            "update",
            str(new_project.dir),
            "--template-uri",
            str(infra_template.template_dir),
        ],
    )
    assert result.exit_code == 1
    assert "Try running" in result.output


def test_update_with_data(
    cli, infra_template: InfraTemplateWritable, new_project: InfraProject, clean_install
):
    ChangeSet([FileChange("{{foo}}.txt", "", "new file\n")]).apply(infra_template.template_dir)
    infra_template.git_project.commit_all("Change template")
    infra_template.git_project.tag("v0.1.0")

    cli(
        [
            "infra",
            "update",
            str(new_project.dir),
            "--template-uri",
            str(infra_template.template_dir),
            "--data",
            "foo=bar",
        ]
    )

    assert (new_project.dir / "bar.txt").read_text() == "new file\n"
