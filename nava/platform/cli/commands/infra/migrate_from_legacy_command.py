from pathlib import Path

from nava.platform.cli.context import CliContext
from nava.platform.project import Project


def migrate_from_legacy(ctx: CliContext, project_dir: str, origin_template_uri: str) -> None:
    project = Project(Path(project_dir))
    project.migrate_from_legacy(origin_template_uri)
