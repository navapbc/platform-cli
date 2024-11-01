from pathlib import Path

import click

from nava.platform.infra_template import InfraTemplate
from nava.platform.project import Project


def install(
    template_dir: str,
    project_dir: str,
    version: str | None = None,
    data: dict[str, str] | None = None,
) -> None:
    template = InfraTemplate(Path(template_dir))
    project = Project(Path(project_dir))
    app_names = project.app_names
    if len(app_names) == 0:
        app_name = click.prompt("What is the name of your app?", type=str)
        app_names = [app_name]
    template.install(project, app_names, version=version, data=data)
