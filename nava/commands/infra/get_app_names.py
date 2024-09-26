import os.path
from typing import List


def get_app_names(template_dir: str) -> List[str]:
    excluded_dirs = [
        "accounts",
        "modules",
        "networks",
        "project-config",
    ]
    infra_path = os.path.join(template_dir, "infra")
    with os.scandir(infra_path) as entries:
        folders = [
            entry.name
            for entry in entries
            if entry.is_dir() and entry.name not in excluded_dirs
        ]
    return folders
