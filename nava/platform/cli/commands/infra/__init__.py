from pathlib import Path
from typing import Annotated

import typer

import nava.platform.util.collections.dict as dict_util
from nava.platform.cli.context import CliContext
from nava.platform.infra_template import MergeConflictsDuringUpdateError

from . import (
    add_app_command,
    info_command,
    install_command,
    migrate_from_legacy_command,
    update_command,
)

app = typer.Typer(
    help="""Manage template-infra usage

    `template-infra` provides basically two parts, a 'base' that is shared
    account infra, and a re-usable 'app' part that provides a generic infra
    shell for running applications.
    """
)


DEFAULT_TEMPLATE_URI = "https://github.com/navapbc/template-infra"

opt_template_uri = typer.Option(
    help="Path or URL to infra template. Can be a path to a local clone of template-infra. Defaults to the template-infra repository on GitHub.",
)

# Temporarily default to using lorenyu/platform-cli as the version
# until the rollout plan for the Platform CLI is complete
# TODO: Set the default back to None once the rollout plan is complete
DEFAULT_VERSION = "lorenyu/platform-cli"

opt_version = typer.Option(
    help="Template version to install. Can be a branch, tag, or commit hash. Defaults to the latest tag version.",
)


# Unfortunately typer doesn't handle args annotated as dictionaries[1], even
# when the dictionary parsing is happening via a `callback`. So we annotate
# `data` as a list of strings, and do the parsing we'd normally do in `callback`
# in the body of the command.
#
# https://github.com/fastapi/typer/issues/130
opt_data = typer.Option(
    help="Parameters in form VARIABLE=VALUE, will make VARIABLE available as VALUE when rendering the template.",
)


@app.command()
def install(
    typer_context: typer.Context,
    project_dir: str,
    template_uri: Annotated[str, opt_template_uri] = DEFAULT_TEMPLATE_URI,
    version: Annotated[str, opt_version] = DEFAULT_VERSION,
    data: Annotated[list[str] | None, opt_data] = None,
) -> None:
    """Install template-infra in project"""

    ctx = typer_context.ensure_object(CliContext)
    install_command.install(
        ctx, template_uri, project_dir, version=version, data=dict_util.from_str_values(data)
    )


@app.command()
def add_app(
    typer_context: typer.Context,
    project_dir: str,
    app_name: str,
    template_uri: Annotated[str, opt_template_uri] = DEFAULT_TEMPLATE_URI,
    data: Annotated[list[str] | None, opt_data] = None,
) -> None:
    """Add infra for APP_NAME"""

    ctx = typer_context.ensure_object(CliContext)
    add_app_command.add_app(
        ctx, template_uri, project_dir, app_name, data=dict_util.from_str_values(data)
    )


@app.command()
def update(
    typer_context: typer.Context,
    project_dir: str,
    template_uri: Annotated[str, opt_template_uri] = DEFAULT_TEMPLATE_URI,
    version: Annotated[str, opt_version] = DEFAULT_VERSION,
    data: Annotated[list[str] | None, opt_data] = None,
) -> None:
    """Update base and application infrastructure"""

    ctx = typer_context.ensure_object(CliContext)
    try:
        update_command.update(
            ctx, template_uri, project_dir, version=version, data=dict_util.from_str_values(data)
        )
    except MergeConflictsDuringUpdateError:
        message = (
            "Merge conflicts found occurred during the update\n"
            "Try running `infra update-base` and `infra update-app` commands separately and resolve conflicts as needed"
        )
        ctx.fail(message)


@app.command()
def update_base(
    typer_context: typer.Context,
    project_dir: str,
    template_uri: Annotated[str, opt_template_uri] = DEFAULT_TEMPLATE_URI,
    version: Annotated[str, opt_version] = DEFAULT_VERSION,
    data: Annotated[list[str] | None, opt_data] = None,
    commit: Annotated[
        bool, typer.Option(help="Commit changes with standard message if able.")
    ] = False,
) -> None:
    """Update base infrastructure"""

    ctx = typer_context.ensure_object(CliContext)
    update_command.update_base(
        ctx,
        template_uri,
        project_dir,
        version=version,
        data=dict_util.from_str_values(data),
        commit=commit,
    )


@app.command()
def update_app(
    typer_context: typer.Context,
    project_dir: str,
    app_name: list[str],
    template_uri: Annotated[str, opt_template_uri] = DEFAULT_TEMPLATE_URI,
    version: Annotated[str, opt_version] = DEFAULT_VERSION,
    data: Annotated[list[str] | None, opt_data] = None,
    commit: Annotated[
        bool, typer.Option(help="Commit changes with standard message if able.")
    ] = False,
    all: Annotated[bool, typer.Option("--all", help="Attempt to update all known apps")] = False,
) -> None:
    """Update application(s) infrastructure"""

    ctx = typer_context.ensure_object(CliContext)
    update_command.update_app(
        ctx,
        template_uri,
        project_dir,
        app_names=app_name,
        version=version,
        data=dict_util.from_str_values(data),
        commit=commit,
        all=all,
    )


@app.command()
def migrate_from_legacy(
    typer_context: typer.Context,
    project_dir: str,
    origin_template_uri: Annotated[
        str,
        typer.Option(
            help="Path or URL to the legacy infra template that was used to set up the project. Can be a path to a local clone of template-infra. Defaults to the template-infra repository on GitHub.",
        ),
    ] = "https://github.com/navapbc/template-infra",
) -> None:
    """Migrate an older version of the template to platform-cli setup"""

    ctx = typer_context.ensure_object(CliContext)
    migrate_from_legacy_command.migrate_from_legacy(ctx, project_dir, origin_template_uri)


@app.command()
def info(
    typer_context: typer.Context,
    project_dir: Annotated[
        Path,
        typer.Argument(
            exists=True,
            file_okay=False,
        ),
    ],
    template_uri: Annotated[
        str | None,
        typer.Option(
            help="Path or URL to infra template. Can be a path to a local clone of template-infra. Defaults to the template-infra repository on GitHub."
        ),
    ] = None,
) -> None:
    """Display some information about the state of template-infra in the project"""

    ctx = typer_context.ensure_object(CliContext)
    info_command.info(ctx, project_dir, template_uri)
