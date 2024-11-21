from pathlib import Path

from nava.platform.cli.context import CliContext
from nava.platform.infra_template import InfraTemplate
from nava.platform.project import Project


def add_app(
    ctx: CliContext,
    template_dir: str | Path,
    project_dir: str,
    app_name: str,
    data: dict[str, str] | None = None,
) -> None:
    template = InfraTemplate(Path(template_dir))
    project = Project(Path(project_dir))
    template.add_app(project, app_name, data=data)
