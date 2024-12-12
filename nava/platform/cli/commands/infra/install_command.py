from pathlib import Path

import typer

from nava.platform.cli.context import CliContext
from nava.platform.infra_project import InfraProject
from nava.platform.templates.infra_template import InfraTemplate


def install(
    ctx: CliContext,
    template_uri: str,
    project_dir: str,
    version: str | None = None,
    data: dict[str, str] | None = None,
    commit: bool = False,
) -> None:
    template = InfraTemplate(ctx, template_uri)
    project = InfraProject(Path(project_dir))
    app_names = project.app_names_possible

    if len(app_names) == 0:
        if data and "app_name" in data:
            app_names = [data["app_name"]]
        else:
            app_name = typer.prompt("What is the name of your app?")
            app_names = [app_name]

    template.install(project, app_names, version=version, data=data, commit=commit)
