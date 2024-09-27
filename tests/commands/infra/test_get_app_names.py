from pathlib import Path
from typing import List

from nava.commands.infra.get_app_names import get_app_names
from tests.lib import DirectoryContent


def test_get_app_names(tmp_path: Path) -> None:
    DirectoryContent(
        {
            "infra": {
                "accounts": {},
                "app1": {},
                "app2": {},
                "modules": {
                    "service": {},
                },
                "networks": {},
                "project-config": {},
            }
        }
    ).to_fs(str(tmp_path))
    app_names = get_app_names(str(tmp_path))
    assert set(app_names) == set(["app1", "app2"])
