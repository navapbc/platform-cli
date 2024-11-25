from pathlib import Path
from typing import Annotated

import typer

import nava.platform.util.collections.dict as dict_util
from nava.platform.cli.commands.infra import opt_data
from nava.platform.cli.context import CliContext
from nava.platform.migrate_from_legacy_template import MigrateFromLegacyTemplate
from nava.platform.project import Project
from nava.platform.template import Template

app = typer.Typer()


@app.command()
def install(
    typer_context: typer.Context,
    project_dir: Annotated[
        Path,
        typer.Argument(
            file_okay=False,
        ),
    ],
    app_name: Annotated[str, typer.Argument(help="What to call the new application")],
    template_uri: Annotated[str, typer.Option()],
    version: Annotated[str | None, typer.Option()] = None,
    data: Annotated[list[str] | None, opt_data] = None,
) -> None:
    """Install application template in project"""

    ctx = typer_context.ensure_object(CliContext)
    template = Template(ctx, template_uri=template_uri)
    project = Project(project_dir)
    template.install(
        project=project, app_name=app_name, version=version, data=dict_util.from_str_values(data)
    )


@app.command()
def update(
    typer_context: typer.Context,
    project_dir: Annotated[
        Path,
        typer.Argument(
            exists=True,
            file_okay=False,
        ),
    ],
    app_name: Annotated[
        str, typer.Argument(help="Name of the application based on given template to update")
    ],
    template_uri: Annotated[str, typer.Option()],
    version: Annotated[str | None, typer.Option()] = None,
    data: Annotated[list[str] | None, opt_data] = None,
) -> None:
    """Update application based on template in project"""

    ctx = typer_context.ensure_object(CliContext)
    template = Template(ctx, template_uri=template_uri)
    project = Project(project_dir)
    template.update(
        project=project, app_name=app_name, version=version, data=dict_util.from_str_values(data)
    )


@app.command()
def migrate_from_legacy(
    typer_context: typer.Context,
    project_dir: str,
    origin_template_uri: Annotated[
        str,
        typer.Option(
            help="Path or URL to the legacy template that was used to set up the project. Can be a path to a local clone of the template.",
        ),
    ],
    app_name: Annotated[
        str, typer.Argument(help="Name of the application based on given template to migrate")
    ],
) -> None:
    """Migrate an older version of the template to platform-cli setup"""
    ctx = typer_context.ensure_object(CliContext)
    project = Project(Path(project_dir))
    MigrateFromLegacyTemplate(
        ctx,
        project,
        origin_template_uri=origin_template_uri,
        new_version_answers_file_name=app_name + ".yml",
    ).migrate_from_legacy()
