from pathlib import Path


def get_app_names_from_infra_dir(dir: Path) -> frozenset[str]:
    """Get apps based on names in infra/.

    Args:
        dir: Should be a location of `template-infra` or an instance of it
    """
    excluded_dirs = [
        "accounts",
        "modules",
        "networks",
        "project-config",
        "test",
    ]
    infra_dir = dir / "infra"
    if not infra_dir.exists():
        return frozenset()
    if not infra_dir.is_dir():
        return frozenset()

    return frozenset(
        [dir.name for dir in infra_dir.iterdir() if dir.is_dir() and dir.name not in excluded_dirs]
    )
