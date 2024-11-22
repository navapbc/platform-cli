from pathlib import Path

from nava.platform.cli.context import CliContext
from nava.platform.infra_project import InfraProject
from nava.platform.infra_template import InfraTemplate


def add_app(
    ctx: CliContext,
    template_dir: str | Path,
    project_dir: str,
    app_name: str,
    data: dict[str, str] | None = None,
) -> None:
    template = InfraTemplate(ctx, Path(template_dir))
    project = InfraProject(Path(project_dir))
    template.add_app(project, app_name, data=data)
