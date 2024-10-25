import pytest

from nava.git import GitProject
from nava.infra_template import InfraTemplate
from tests.lib import DirectoryContent

test_compute_excludes_data = {
    "empty": (
        {},
        ["*template-only*"],
        ["*template-only*"],
    ),
    "files_only": (
        {
            "{{app_name}}": "",
            "prefix-{{app_name}}-suffix": "",
            "exclude": "",
        },
        ["*template-only*", "{{app_name}}", "prefix-{{app_name}}-suffix"],
        ["*template-only*", "exclude"],
    ),
    "nested_app_name_folders": (
        {
            "{{app_name}}root": {
                "{{app_name}}nested": {
                    "somefile": "",
                }
            },
        },
        ["*template-only*", "{{app_name}}root"],
        ["*template-only*"],
    ),
    "buried_app_name": (
        {
            "one": {
                "two": {
                    "three-{{app_name}}": {
                        "somefile": "",
                    },
                    "three-exclude": {
                        "somefile": "",
                    },
                }
            },
        },
        ["*template-only*", "one/two/three-{{app_name}}"],
        ["*template-only*", "one/two/three-exclude"],
    ),
    "ignore_template_only": (
        {
            "some-template-only-thing": "",
            "template-only": {},
            "template-only-bin": {
                "install-template": "",
                "destroy-account": "",
            },
        },
        ["*template-only*"],
        ["*template-only*"],
    ),
    "infra_template": (
        {
            ".github": {
                "workflows": {
                    "ci-{{app_name}}-pr-environment-checks.yml": "",
                    "pr-environment-checks.yml": "",
                    "template-only-cd.yml": "",
                    "template-only-ci-infra.yml": "",
                },
            },
            ".template-infra": {
                "{{_copier_conf.answers_file}}.jinja": "{{ _copier_answers|to_nice_yaml -}}",
            },
            "bin": {
                "publish-release": "",
            },
            "infra": {
                "{{app_name}}": {"main.tf": ""},
                "accounts": {"main.tf": ""},
                "modules": {
                    "service": {"main.tf": ""},
                    "database": {"main.tf": ""},
                },
                "networks": {"main.tf": ""},
                "project-config": {"main.tf": ""},
            },
            "template-only-bin": {
                "install-template": "",
                "destroy-account": "",
            },
        },
        [
            "*template-only*",
            ".github/workflows/ci-{{app_name}}-pr-environment-checks.yml",
            "infra/{{app_name}}",
        ],
        [
            "*template-only*",
            ".github/workflows/pr-environment-checks.yml",
            "bin",
            "infra/accounts",
            "infra/modules",
            "infra/networks",
            "infra/project-config",
        ],
    ),
}


@pytest.mark.parametrize(
    "dir_content,expected_base_excludes,expected_app_excludes",
    test_compute_excludes_data.values(),
    ids=test_compute_excludes_data.keys(),
)
def test_compute_excludes(tmp_path, dir_content, expected_base_excludes, expected_app_excludes):
    DirectoryContent(dir_content).to_fs(tmp_path)

    git_project = GitProject(tmp_path)
    git_project.init()
    git_project.commit_all("Initial commit")

    infra_template = InfraTemplate(tmp_path)
    infra_template._compute_excludes()
    assert set(infra_template._base_excludes) == set(expected_base_excludes)
    assert set(infra_template._app_excludes) == set(expected_app_excludes)


def test_compute_excludes_from_dirty_repo(tmp_path):
    dir_content = {
        ".gitignore": "ignored_file.txt",
        "ignored_file.txt": "foobar",
        "untracked_file.txt": "untracked content",
    }
    expected_base_excludes = [
        "*template-only*",
    ]
    expected_app_excludes = [
        "*template-only*",
    ]
    DirectoryContent(dir_content).to_fs(tmp_path)

    git_project = GitProject(tmp_path)
    git_project.init()
    git_project.add(".gitignore")
    git_project.commit("Initial commit")

    infra_template = InfraTemplate(tmp_path)
    infra_template._compute_excludes()
    assert set(infra_template._base_excludes) == set(expected_base_excludes)
    assert set(infra_template._app_excludes) == set(expected_app_excludes)
