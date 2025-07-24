from itertools import chain
from pathlib import Path


def get_app_names_from_template_answers(dir: Path) -> frozenset[str]:
    """Get apps based on names in .template-*/ directories.

    Args:
        dir: Should be a location of a project root with templates installed
    """
    infra_template_app_state_files = filter(
        lambda f: f.is_file(), dir.glob(".template-infra*/app-*")
    )
    app_template_app_state_files = filter(
        lambda f: f.is_file(), dir.glob(".template-application-*/*")
    )

    return frozenset(
        chain(
            map(
                lambda f: f.name.removeprefix("app-").removesuffix(".yml"),
                infra_template_app_state_files,
            ),
            map(lambda f: f.name.removesuffix(".yml"), app_template_app_state_files),
        )
    )
