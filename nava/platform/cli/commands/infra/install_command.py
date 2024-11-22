from pathlib import Path

import typer

from nava.platform.cli.context import CliContext
from nava.platform.infra_template import InfraTemplate
from nava.platform.project import Project


def install(
    ctx: CliContext,
    template_dir: str,
    project_dir: str,
    version: str | None = None,
    data: dict[str, str] | None = None,
) -> None:
    template = InfraTemplate(ctx, Path(template_dir))
    project = Project(Path(project_dir))
    app_names = project.app_names

    if len(app_names) == 0:
        if data and "app_name" in data:
            app_names = [data["app_name"]]
        else:
            app_name = typer.prompt("What is the name of your app?")
            app_names = [app_name]

    template.install(project, app_names, version=version, data=data)
