from pathlib import Path
from typing import List


def get_app_names(template_dir: Path) -> List[str]:
    excluded_dirs = [
        "accounts",
        "modules",
        "networks",
        "project-config",
        "test",
    ]
    infra_dir = template_dir / "infra"
    if not infra_dir.exists():
        return []
    if not infra_dir.is_dir():
        return []

    return [
        dir.name for dir in infra_dir.iterdir() if dir.is_dir() and dir.name not in excluded_dirs
    ]
