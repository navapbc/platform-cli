import pytest
from pathlib import Path


@pytest.fixture
def tmp_template(tmp_path: Path) -> Path:
    infra_dir = tmp_path / "infra"
    infra_dir.mkdir()
    (infra_dir / "app1").mkdir()
    (infra_dir / "app2").mkdir()
    (infra_dir / "accounts").mkdir()
    (infra_dir / "modules").mkdir()
    (infra_dir / "networks").mkdir()
    (infra_dir / "project-config").mkdir()
    return tmp_path
