from pathlib import Path

from nava.platform.cli.context import CliContext
from nava.platform.infra_project import InfraProject
from nava.platform.templates.infra_template import InfraTemplate


def add_app(
    ctx: CliContext,
    template_uri: str | Path,
    project_dir: str,
    app_name: str,
    data: dict[str, str] | None = None,
    commit: bool = False,
) -> None:
    template = InfraTemplate(ctx, template_uri)
    project = InfraProject(Path(project_dir))
    template.add_app(project, app_name, data=data, commit=commit)
