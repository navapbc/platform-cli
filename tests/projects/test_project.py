from typing import Any

import pytest

from nava.platform.projects.project import Project
from tests.lib import DirectoryContent

DirContentArg = dict[str, Any]

installed_template_scenarios: dict[str, DirContentArg] = {
    "empty": {},
    "just-infra-base": {
        ".template-infra": {
            "base.yml": """
            template: base
            """,
        },
    },
    "just-infra": {
        ".template-infra": {
            "base.yml": """
            template: base
            """,
            "app-foo.yml": """
            template: app
            """,
        },
    },
    "just-app": {
        ".template-application-magic": {
            "foo.yml": "blah",
        },
    },
    "infra-and-app": {
        ".template-infra": {
            "base.yml": """
            template: base
            """,
            "app-foo.yml": """
            template: app
            """,
        },
        ".template-application-magic": {
            "foo.yml": "blah",
        },
    },
    "infra-and-muliple-apps": {
        ".template-infra": {
            "base.yml": """
            template: base
            """,
            "app-foo.yml": """
            template: app
            """,
            "app-bar.yml": """
            template: app
            """,
        },
        ".template-application-magic": {
            "foo.yml": "blah",
        },
        ".template-whoa": {
            "bar.yml": "blah",
        },
    },
    "infra-and-muliple-apps-for-same-application": {
        ".template-infra": {
            "base.yml": """
            template: base
            """,
            "app-foo.yml": """
            template: app
            """,
            "app-bar.yml": """
            template: app
            """,
        },
        ".template-application-magic": {
            "foo.yml": "blah",
        },
        ".template-whoa": {
            "foo.yml": "blah",
        },
    },
}


def map_scenarios(mapping: dict[str, list[str]]) -> dict[str, tuple[DirContentArg, list[str]]]:
    # TODO: could fail nicer if one of the mappings hasn't been updated for a new scenario?
    return {k: (v, mapping[k]) for k, v in installed_template_scenarios.items()}


installed_template_repo_names_test_data = map_scenarios(
    {
        "empty": [],
        "just-infra-base": ["template-infra"],
        "just-infra": ["template-infra"],
        "just-app": ["template-application-magic"],
        "infra-and-app": ["template-infra", "template-application-magic"],
        "infra-and-muliple-apps": ["template-infra", "template-application-magic", "template-whoa"],
        "infra-and-muliple-apps-for-same-application": [
            "template-infra",
            "template-application-magic",
            "template-whoa",
        ],
    }
)


@pytest.mark.parametrize(
    ("dir_content", "expected"),
    installed_template_repo_names_test_data.values(),
    ids=installed_template_repo_names_test_data.keys(),
)
def test_installed_template_repo_names(tmp_path, dir_content, expected):
    DirectoryContent(dir_content).to_fs(str(tmp_path))
    project = Project(tmp_path)

    assert set(project.installed_template_repo_names()) == set(expected)


installed_template_names_test_data = map_scenarios(
    {
        "empty": [],
        "just-infra-base": ["template-infra:base"],
        "just-infra": ["template-infra:base", "template-infra:app"],
        "just-app": ["template-application-magic"],
        "infra-and-app": [
            "template-infra:base",
            "template-infra:app",
            "template-application-magic",
        ],
        "infra-and-muliple-apps": [
            "template-infra:base",
            "template-infra:app",
            "template-application-magic",
            "template-whoa",
        ],
        "infra-and-muliple-apps-for-same-application": [
            "template-infra:base",
            "template-infra:app",
            "template-application-magic",
            "template-whoa",
        ],
    }
)


@pytest.mark.parametrize(
    ("dir_content", "expected"),
    installed_template_names_test_data.values(),
    ids=installed_template_names_test_data.keys(),
)
def test_installed_template_names(tmp_path, dir_content, expected):
    DirectoryContent(dir_content).to_fs(str(tmp_path))
    project = Project(tmp_path)

    assert set(map(lambda tn: tn.id, project.installed_template_names())) == set(expected)


installed_template_names_for_app_foo_test_data = map_scenarios(
    {
        "empty": [],
        "just-infra-base": [],
        "just-infra": ["template-infra:app"],
        "just-app": ["template-application-magic"],
        "infra-and-app": ["template-infra:app", "template-application-magic"],
        "infra-and-muliple-apps": ["template-infra:app", "template-application-magic"],
        "infra-and-muliple-apps-for-same-application": [
            "template-infra:app",
            "template-application-magic",
            "template-whoa",
        ],
    }
)


@pytest.mark.parametrize(
    ("dir_content", "expected"),
    installed_template_names_for_app_foo_test_data.values(),
    ids=installed_template_names_for_app_foo_test_data.keys(),
)
def test_installed_template_names_for_app(tmp_path, dir_content, expected):
    DirectoryContent(dir_content).to_fs(str(tmp_path))
    project = Project(tmp_path)

    assert set(map(lambda tn: tn.id, project.installed_template_names_for_app("foo"))) == set(
        expected
    )
