import os
import pytest

from nava.commands.infra.get_app_names import get_app_names


@pytest.fixture
def tmp_template(tmp_path):
    infra_dir = tmp_path / "infra"
    infra_dir.mkdir()
    (infra_dir / "app1").mkdir()
    (infra_dir / "app2").mkdir()
    (infra_dir / "accounts").mkdir()
    (infra_dir / "modules").mkdir()
    (infra_dir / "networks").mkdir()
    (infra_dir / "project-config").mkdir()
    return tmp_path


def test_get_app_names(tmp_template):
    # Call the function with the temporary directory
    app_names = get_app_names(tmp_template)
    assert set(app_names) == set(["app1", "app2"])
