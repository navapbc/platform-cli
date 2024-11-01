from pathlib import Path


def get_app_names(template_dir: Path) -> list[str]:
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

    return sorted(
        [dir.name for dir in infra_dir.iterdir() if dir.is_dir() and dir.name not in excluded_dirs]
    )
