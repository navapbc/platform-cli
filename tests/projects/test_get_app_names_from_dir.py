from pathlib import Path
from typing import Any

import pytest

from nava.platform.projects.get_app_names_from_infra_dir import get_app_names_from_infra_dir
from tests.lib import DirectoryContent

get_app_names_test_data: dict[str, tuple[dict[str, dict[str, Any]], list[str]]] = {
    "empty_dir": ({}, []),
    "one_app": (
        {
            "infra": {
                "app": {},
                "accounts": {},
                "modules": {
                    "service": {},
                },
                "networks": {},
                "project-config": {},
                "test": {},
            }
        },
        ["app"],
    ),
    "multiple_apps": (
        {
            "infra": {
                "app1": {},
                "app2": {},
                "accounts": {},
                "modules": {
                    "service": {},
                },
                "networks": {},
                "project-config": {},
                "test": {},
            }
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

    app_names = get_app_names_from_infra_dir(tmp_path)

    assert set(app_names) == set(expected)
