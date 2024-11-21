import click

from nava.platform.cli.context import CliContext, pass_cli_ctx
from nava.platform.infra_template import MergeConflictsDuringUpdateError

from . import add_app_command, install_command, migrate_from_legacy_command, update_command


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
def install(project_dir: str, template_uri: str, version: str, data: dict[str, str] | None) -> None:
    install_command.install(template_uri, project_dir, version=version, data=data)


@infra.command()
@click.argument("project_dir")
@click.argument("app_name")
@opt_template_uri
@opt_data
def add_app(
    project_dir: str, app_name: str, template_uri: str, data: dict[str, str] | None
) -> None:
    add_app_command.add_app(template_uri, project_dir, app_name)


@infra.command()
@click.argument("project_dir")
@opt_template_uri
@opt_version
@opt_data
def update(project_dir: str, template_uri: str, version: str, data: dict[str, str] | None) -> None:
    try:
        update_command.update(template_uri, project_dir, version=version, data=data)
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
def update_base(
    project_dir: str, template_uri: str, version: str, data: dict[str, str] | None, commit: bool
) -> None:
    update_command.update_base(template_uri, project_dir, version=version, data=data, commit=commit)


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
def migrate_from_legacy(project_dir: str, origin_template_uri: str) -> None:
    migrate_from_legacy_command.migrate_from_legacy(project_dir, origin_template_uri)
