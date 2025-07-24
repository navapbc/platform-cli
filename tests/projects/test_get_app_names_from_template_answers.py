from pathlib import Path
from typing import Any

import pytest

from nava.platform.projects.get_app_names_from_template_answers import (
    get_app_names_from_template_answers,
)
from tests.lib import DirectoryContent

get_app_names_test_data: dict[str, tuple[dict[str, dict[str, Any]], list[str]]] = {
    "empty_dir": ({}, []),
    "one_app_infra": (
        {
            ".template-infra": {"app-app.yml": ""},
        },
        ["app"],
    ),
    "one_app_app": (
        {
            ".template-application-foo": {"app.yml": ""},
        },
        ["app"],
    ),
    "multiple_apps": (
        {
            ".template-infra": {"app-app1.yml": ""},
            ".template-application-foo": {"app1.yml": ""},
            ".template-application-bar": {"app2.yml": ""},
        },
        ["app1", "app2"],
    ),
}


@pytest.mark.parametrize(
    ("dir_content", "expected"),
    get_app_names_test_data.values(),
    ids=get_app_names_test_data.keys(),
)
def test_get_app_names(tmp_path: Path, dir_content, expected) -> None:
    DirectoryContent(dir_content).to_fs(str(tmp_path))

    app_names = get_app_names_from_template_answers(tmp_path)

    assert app_names == set(expected)
