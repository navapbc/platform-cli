from pathlib import Path
from typing import Annotated

import typer

import nava.platform.util.collections.dict as dict_util
from nava.platform.cli.commands.common import (
    opt_answers_only,
    opt_commit,
    opt_data,
    opt_force_update,
    opt_version,
)
from nava.platform.cli.context import CliContext
from nava.platform.templates.errors import MergeConflictsDuringUpdateError

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


@app.command()
def install(
    typer_context: typer.Context,
    project_dir: str,
    template_uri: Annotated[str, opt_template_uri] = DEFAULT_TEMPLATE_URI,
    version: Annotated[str | None, opt_version] = DEFAULT_VERSION,
    data: Annotated[list[str] | None, opt_data] = None,
    commit: Annotated[bool, opt_commit] = False,
) -> None:
    """Install template-infra in project."""
    ctx = typer_context.ensure_object(CliContext)

    with ctx.handle_exceptions():
        install_command.install(
            ctx,
            template_uri,
            project_dir,
            version=version,
            data=dict_util.from_str_values(data),
            commit=commit,
        )


@app.command()
def add_app(
    typer_context: typer.Context,
    project_dir: str,
    app_name: str,
    template_uri: Annotated[str, opt_template_uri] = DEFAULT_TEMPLATE_URI,
    data: Annotated[list[str] | None, opt_data] = None,
    commit: Annotated[bool, opt_commit] = True,
) -> None:
    """Add infra for APP_NAME."""
    ctx = typer_context.ensure_object(CliContext)

    with ctx.handle_exceptions():
        add_app_command.add_app(
            ctx,
            template_uri,
            project_dir,
            app_name,
            data=dict_util.from_str_values(data),
            commit=commit,
        )


@app.command()
def update(
    typer_context: typer.Context,
    project_dir: str,
    template_uri: Annotated[str, opt_template_uri] = DEFAULT_TEMPLATE_URI,
    version: Annotated[str | None, opt_version] = DEFAULT_VERSION,
    data: Annotated[list[str] | None, opt_data] = None,
    answers_only: Annotated[bool, opt_answers_only] = False,
    force: Annotated[bool, opt_force_update] = False,
) -> None:
    """Update base and application infrastructure.

    This effectively just runs `update-base` followed by `update-app --all`.
    This automatically commits each phase of the update that is successful to
    save progress. You can merge all these commits together after if you would
    like.
    """
    ctx = typer_context.ensure_object(CliContext)

    with ctx.handle_exceptions():
        try:
            update_command.update(
                ctx,
                template_uri,
                project_dir,
                version=version if not answers_only else None,
                data=dict_util.from_str_values(data),
                answers_only=answers_only,
                force=force,
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
    version: Annotated[str | None, opt_version] = DEFAULT_VERSION,
    data: Annotated[list[str] | None, opt_data] = None,
    commit: Annotated[bool, opt_commit] = True,
    answers_only: Annotated[bool, opt_answers_only] = False,
    force: Annotated[bool, opt_force_update] = False,
) -> None:
    """Update base infrastructure."""
    ctx = typer_context.ensure_object(CliContext)

    with ctx.handle_exceptions():
        update_command.update_base(
            ctx,
            template_uri,
            project_dir,
            version=version if not answers_only else None,
            data=dict_util.from_str_values(data),
            commit=commit,
            answers_only=answers_only,
            force=force,
        )


@app.command()
def update_app(
    typer_context: typer.Context,
    project_dir: str,
    app_name: Annotated[list[str] | None, typer.Argument()] = None,
    template_uri: Annotated[str, opt_template_uri] = DEFAULT_TEMPLATE_URI,
    version: Annotated[str | None, opt_version] = DEFAULT_VERSION,
    data: Annotated[list[str] | None, opt_data] = None,
    commit: Annotated[bool, opt_commit] = True,
    all: Annotated[bool, typer.Option("--all", help="Attempt to update all known apps")] = False,
    answers_only: Annotated[bool, opt_answers_only] = False,
    force: Annotated[bool, opt_force_update] = False,
) -> None:
    """Update application(s) infrastructure."""
    ctx = typer_context.ensure_object(CliContext)

    with ctx.handle_exceptions():
        update_command.update_app(
            ctx,
            template_uri,
            project_dir,
            app_names=app_name,
            version=version if not answers_only else None,
            data=dict_util.from_str_values(data),
            commit=commit,
            all=all,
            answers_only=answers_only,
            force=force,
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
    commit: Annotated[bool, opt_commit] = False,
) -> None:
    """Migrate an older version of the template to platform-cli setup."""
    ctx = typer_context.ensure_object(CliContext)

    with ctx.handle_exceptions():
        migrate_from_legacy_command.migrate_from_legacy(
            ctx, project_dir, origin_template_uri, commit=commit
        )


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
    template_uri: Annotated[str | None, opt_template_uri] = None,
) -> None:
    """Display some information about the state of template-infra in the project."""
    ctx = typer_context.ensure_object(CliContext)

    with ctx.handle_exceptions():
        info_command.info(ctx, project_dir, template_uri)
