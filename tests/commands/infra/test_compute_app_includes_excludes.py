import pytest

from nava.commands.infra.compute_app_includes_excludes import (
    compute_app_includes_excludes,
)
from nava.git import GitProject
from tests.lib import DirectoryContent

test_compute_app_includes_excludes_data = {
    "empty": (
        {},
        [],
        ["*template-only*"],
    ),
    "files_only": (
        {
            "{{app_name}}": "",
            "prefix-{{app_name}}-suffix": "",
            "exclude": "",
        },
        ["{{app_name}}", "prefix-{{app_name}}-suffix"],
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
        ["{{app_name}}root"],
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
        ["one/two/three-{{app_name}}"],
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
        [],
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
    "dir_content,expected_includes,expected_excludes",
    test_compute_app_includes_excludes_data.values(),
    ids=test_compute_app_includes_excludes_data.keys(),
)
def test_compute_app_includes_excludes(tmp_path, dir_content, expected_includes, expected_excludes):
    DirectoryContent(dir_content).to_fs(tmp_path)

    git_project = GitProject(tmp_path)
    git_project.init()
    git_project.add_all_and_commit("Initial commit")

    app_includes, app_excludes = compute_app_includes_excludes(tmp_path, git_project)
    assert app_includes == set(expected_includes)
    assert app_excludes == set(expected_excludes)
