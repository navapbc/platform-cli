from pathlib import Path
from typing import cast

import click

from nava.platform.infra_template import InfraTemplate
from nava.platform.project import Project


def update(template_dir: str, project_dir: str, version: str | None = None) -> None:
    template = InfraTemplate(Path(template_dir))
    project = Project(Path(project_dir))
    template.update(project, version=version)


def update_base(template_dir: str, project_dir: str, version: str | None = None) -> None:
    template = InfraTemplate(Path(template_dir))
    project = Project(Path(project_dir))
    template.update_base(project, version=version)


def update_app(
    template_dir: str, project_dir: str, app_name: str | None, version: str | None = None
) -> None:
    template = InfraTemplate(Path(template_dir))
    project = Project(Path(project_dir))

    if not app_name:
        app_name = cast(
            str,
            click.prompt(
                "Which app",
                prompt_suffix="? ",
                type=click.Choice(project.app_names),
                show_choices=True,
            ),
        )

    template.update_app(project, app_name, version=version)
