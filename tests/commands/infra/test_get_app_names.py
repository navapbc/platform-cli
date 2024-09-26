from pathlib import Path
from typing import List

from nava.commands.infra.get_app_names import get_app_names


def test_get_app_names(tmp_template: Path) -> None:
    app_names: List[str] = get_app_names(str(tmp_template))
    assert set(app_names) == set(["app1", "app2"])
