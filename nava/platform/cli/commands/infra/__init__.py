from pathlib import Path

import click

from nava.platform.cli.context import CliContext, pass_cli_ctx
from nava.platform.infra_template import MergeConflictsDuringUpdateError

from . import (
    add_app_command,
    info_command,
    install_command,
    migrate_from_legacy_command,
    update_command,
)


@click.group()
def infra() -> None:
    pass


opt_template_uri = click.option(
    "--template-uri",
    default="https://github.com/navapbc/template-infra",
    help="Path or URL to infra template. Can be a path to a local clone of template-infra. Defaults to the template-infra repository on GitHub.",
)

opt_version = click.option(
    "--version",
    # Temporarily default to using lorenyu/platform-cli as the version
    # until the rollout plan for the Platform CLI is complete
    # TODO: Set the default back to None once the rollout plan is complete
    default="lorenyu/platform-cli",
    help="Template version to install. Can be a branch, tag, or commit hash. Defaults to the latest tag version.",
)


def _data_to_dict(
    ctx: click.Context, param: click.Option, value: tuple[str, ...]
) -> dict[str, str] | None:
    result = {}
    for val in value:
        k, v = val.split("=")

        if k in result:
            raise click.BadParameter(f"Data {k} is specified twice")

        result[k] = v

    return result if result else None


opt_data = click.option(
    "--data",
    help="Parameters in form VARIABLE=VALUE, will make VARIABLE available as VALUE when rendering the template.",
    multiple=True,
    callback=_data_to_dict,
)


@infra.command()
@click.argument("project_dir")
@opt_template_uri
@opt_version
@opt_data
@pass_cli_ctx
def install(
    ctx: CliContext, project_dir: str, template_uri: str, version: str, data: dict[str, str] | None
) -> None:
    install_command.install(ctx, template_uri, project_dir, version=version, data=data)


@infra.command()
@click.argument("project_dir")
@click.argument("app_name")
@opt_template_uri
@opt_data
@pass_cli_ctx
def add_app(
    ctx: CliContext, project_dir: str, app_name: str, template_uri: str, data: dict[str, str] | None
) -> None:
    add_app_command.add_app(ctx, template_uri, project_dir, app_name, data=data)


@infra.command()
@click.argument("project_dir")
@opt_template_uri
@opt_version
@opt_data
@pass_cli_ctx
def update(
    ctx: CliContext, project_dir: str, template_uri: str, version: str, data: dict[str, str] | None
) -> None:
    try:
        update_command.update(ctx, template_uri, project_dir, version=version, data=data)
    except MergeConflictsDuringUpdateError as error:
        click.echo()
        message = (
            "Merge conflicts found occurred during the update\n"
            "Try running `infra update-base` and `infra update-app` commands separately and resolve conflicts as needed"
        )
        raise click.ClickException(message) from error


@infra.command()
@click.argument("project_dir")
@opt_template_uri
@opt_version
@opt_data
@click.option(
    "--commit/--no-commit", default=False, help="Commit changes with standard message if able."
)
@pass_cli_ctx
def update_base(
    ctx: CliContext,
    project_dir: str,
    template_uri: str,
    version: str,
    data: dict[str, str] | None,
    commit: bool,
) -> None:
    update_command.update_base(
        ctx, template_uri, project_dir, version=version, data=data, commit=commit
    )


@infra.command()
@click.argument("project_dir")
@click.argument("app_name", nargs=-1)
@opt_template_uri
@opt_version
@opt_data
@click.option(
    "--commit/--no-commit", default=False, help="Commit changes with standard message if able."
)
@click.option("--all", is_flag=True, default=False, help="Attempt to update all known apps.")
@pass_cli_ctx
def update_app(
    ctx: CliContext,
    project_dir: str,
    app_name: list[str],
    template_uri: str,
    version: str,
    data: dict[str, str] | None,
    commit: bool,
    all: bool,
) -> None:
    update_command.update_app(
        ctx,
        template_uri,
        project_dir,
        app_names=app_name,
        version=version,
        data=data,
        commit=commit,
        all=all,
    )


@infra.command()
@click.argument("project_dir")
@click.option(
    "--origin-template-uri",
    default="https://github.com/navapbc/template-infra",
    help="Path or URL to the legacy infra template that was used to set up the project. Can be a path to a local clone of template-infra. Defaults to the template-infra repository on GitHub.",
)
@pass_cli_ctx
def migrate_from_legacy(ctx: CliContext, project_dir: str, origin_template_uri: str) -> None:
    migrate_from_legacy_command.migrate_from_legacy(ctx, project_dir, origin_template_uri)


@infra.command()
@click.argument("project_dir", type=click.Path(exists=True, file_okay=False, path_type=Path))
@click.option(
    "--template-uri",
    help="Path or URL to infra template. Can be a path to a local clone of template-infra. Defaults to the template-infra repository on GitHub.",
)
@pass_cli_ctx
def info(ctx: CliContext, project_dir: Path, template_uri: str | None) -> None:
    info_command.info(ctx, project_dir, template_uri)
