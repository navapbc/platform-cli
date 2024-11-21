from pathlib import Path

from nava.platform.cli.context import CliContext
from nava.platform.project import Project


def migrate_from_legacy(ctx: CliContext, project_dir: str, origin_template_uri: str) -> None:
    project = Project(Path(project_dir))

    if not project.has_legacy_version_file:
        ctx.console.error.print(
            f"No legacy version file found (looking for {project.legacy_version_file_path()}). Are you sure this is a legacy template?"
        )
        ctx.exit(1)

    project.migrate_from_legacy(ctx, origin_template_uri)
