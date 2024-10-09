import click

from . import add_app_command, install_command, update_command, migrate_from_legacy_command


@click.group()
def infra() -> None:
    pass


@infra.command()
@click.argument("project_dir")
@click.option(
    "--template-uri",
    default="https://github.com/navapbc/template-infra.git",
    help="Path or URL to infra template. Can be a path to a local clone of template-infra. Defaults to the template-infra repository on GitHub.",
)
@click.option(
    "--version",
    default=None,
    help="Template version to install. Can be a branch, tag, or commit hash. Defaults to the latest tag version.",
)
def install(project_dir: str, template_uri: str, version: str) -> None:
    install_command.install(template_uri, project_dir, version=version)


@infra.command()
@click.argument("project_dir")
@click.argument("app_name")
@click.option(
    "--template-uri",
    default="https://github.com/navapbc/template-infra.git",
    help="Path or URL to infra template. Can be a path to a local clone of template-infra. Defaults to the template-infra repository on GitHub.",
)
def add_app(project_dir: str, app_name: str, template_uri: str) -> None:
    add_app_command.add_app(template_uri, project_dir, app_name)


@infra.command()
@click.argument("project_dir")
@click.option(
    "--template-uri",
    default="https://github.com/navapbc/template-infra.git",
    help="Path or URL to infra template. Can be a path to a local clone of template-infra. Defaults to the template-infra repository on GitHub.",
)
@click.option(
    "--version",
    default=None,
    help="Template version to install. Can be a branch, tag, or commit hash. Defaults to the latest tag version.",
)
def update(project_dir: str, template_uri: str, version: str) -> None:
    update_command.update(template_uri, project_dir, version=version)


@infra.command()
@click.argument("project_dir")
@click.option(
    "--origin-template-uri",
    default="https://github.com/navapbc/template-infra.git",
    help="Path or URL to the legacy infra template that was used to set up the project. Can be a path to a local clone of template-infra. Defaults to the template-infra repository on GitHub.",
)
def migrate_from_legacy(project_dir: str, origin_template_uri: str) -> None:
    migrate_from_legacy_command.migrate_from_legacy(project_dir, origin_template_uri)
