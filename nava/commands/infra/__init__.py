import click

from nava.infra_template import MergeConflictsDuringUpdateError

from . import add_app_command, install_command, migrate_from_legacy_command, update_command


@click.group()
def infra() -> None:
    pass


@infra.command()
@click.argument("project_dir")
@click.option(
    "--template-uri",
    default="https://github.com/navapbc/template-infra",
    help="Path or URL to infra template. Can be a path to a local clone of template-infra. Defaults to the template-infra repository on GitHub.",
)
@click.option(
    "--version",
    # Temporarily default to using lorenyu/platform-cli as the version
    # until the rollout plan for the Platform CLI is complete
    # TODO: Set the default back to None once the rollout plan is complete
    default="lorenyu/platform-cli",
    help="Template version to install. Can be a branch, tag, or commit hash. Defaults to the latest tag version.",
)
def install(project_dir: str, template_uri: str, version: str) -> None:
    install_command.install(template_uri, project_dir, version=version)


@infra.command()
@click.argument("project_dir")
@click.argument("app_name")
@click.option(
    "--template-uri",
    default="https://github.com/navapbc/template-infra",
    help="Path or URL to infra template. Can be a path to a local clone of template-infra. Defaults to the template-infra repository on GitHub.",
)
def add_app(project_dir: str, app_name: str, template_uri: str) -> None:
    add_app_command.add_app(template_uri, project_dir, app_name)


@infra.command()
@click.argument("project_dir")
@click.option(
    "--template-uri",
    default="https://github.com/navapbc/template-infra",
    help="Path or URL to infra template. Can be a path to a local clone of template-infra. Defaults to the template-infra repository on GitHub.",
)
@click.option(
    "--version",
    default=None,
    help="Template version to install. Can be a branch, tag, or commit hash. Defaults to the latest tag version.",
)
def update(project_dir: str, template_uri: str, version: str) -> None:
    try:
        update_command.update(template_uri, project_dir, version=version)
    except MergeConflictsDuringUpdateError as error:
        click.echo()
        message = (
            "Merge conflicts found occurred during the update\n"
            "Try running `infra update-base` and `infra update-app` commands separately and resolve conflicts as needed"
        )
        raise click.ClickException(message) from error


@infra.command()
@click.argument("project_dir")
@click.option(
    "--template-uri",
    default="https://github.com/navapbc/template-infra",
    help="Path or URL to infra template. Can be a path to a local clone of template-infra. Defaults to the template-infra repository on GitHub.",
)
@click.option(
    "--version",
    default=None,
    help="Template version to install. Can be a branch, tag, or commit hash. Defaults to the latest tag version.",
)
def update_base(project_dir: str, template_uri: str, version: str) -> None:
    update_command.update_base(template_uri, project_dir, version=version)


@infra.command()
@click.argument("project_dir")
@click.argument("app_name")
@click.option(
    "--template-uri",
    default="https://github.com/navapbc/template-infra",
    help="Path or URL to infra template. Can be a path to a local clone of template-infra. Defaults to the template-infra repository on GitHub.",
)
@click.option(
    "--version",
    default=None,
    help="Template version to install. Can be a branch, tag, or commit hash. Defaults to the latest tag version.",
)
def update_app(project_dir: str, app_name: str, template_uri: str, version: str) -> None:
    update_command.update_app(template_uri, project_dir, app_name, version=version)


@infra.command()
@click.argument("project_dir")
@click.option(
    "--origin-template-uri",
    default="https://github.com/navapbc/template-infra",
    help="Path or URL to the legacy infra template that was used to set up the project. Can be a path to a local clone of template-infra. Defaults to the template-infra repository on GitHub.",
)
def migrate_from_legacy(project_dir: str, origin_template_uri: str) -> None:
    migrate_from_legacy_command.migrate_from_legacy(project_dir, origin_template_uri)
