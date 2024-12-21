from typing import Any

import pytest

from nava.platform.projects.project import Project
from tests.lib import DirectoryContent

DirContentArg = dict[str, Any]

installed_template_scenarios: dict[str, DirContentArg] = {
    "empty": {},
    "just-infra-base": {
        ".template-infra": {
            "base.yml": "blah",
        },
    },
    "just-infra": {
        ".template-infra": {
            "base.yml": "blah",
            "app-foo.yml": "blah",
        },
    },
    "just-app": {
        ".template-application-magic": {
            "foo.yml": "blah",
        },
    },
    "infra-and-app": {
        ".template-infra": {
            "base.yml": "blah",
            "app-foo.yml": "blah",
        },
        ".template-application-magic": {
            "foo.yml": "blah",
        },
    },
    "infra-and-muliple-apps": {
        ".template-infra": {
            "base.yml": "blah",
            "app-foo.yml": "blah",
            "app-bar.yml": "blah",
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
            "base.yml": "blah",
            "app-foo.yml": "blah",
            "app-bar.yml": "blah",
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


installed_template_names_test_data = map_scenarios(
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
    installed_template_names_test_data.values(),
    ids=installed_template_names_test_data.keys(),
)
def test_installed_template_names(tmp_path, dir_content, expected):
    DirectoryContent(dir_content).to_fs(str(tmp_path))
    project = Project(tmp_path)

    assert set(project.installed_template_names()) == set(expected)


installed_template_names_for_app_foo_test_data = map_scenarios(
    {
        "empty": [],
        "just-infra-base": [],
        "just-infra": ["template-infra"],
        "just-app": ["template-application-magic"],
        "infra-and-app": ["template-infra", "template-application-magic"],
        "infra-and-muliple-apps": ["template-infra", "template-application-magic"],
        "infra-and-muliple-apps-for-same-application": [
            "template-infra",
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

    assert set(project.installed_template_names_for_app("foo")) == set(expected)
