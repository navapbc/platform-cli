import click

import copier

from . import add_app_command, install_command, update_command


@click.group()
def infra():
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
def install(project_dir, template_uri, version):
    install_command.install(template_uri, project_dir, version=version)


@infra.command()
@click.argument("project_dir")
@click.argument("app_name")
@click.option(
    "--template-uri",
    default="https://github.com/navapbc/template-infra.git",
    help="Path or URL to infra template. Can be a path to a local clone of template-infra. Defaults to the template-infra repository on GitHub.",
)
def add_app(project_dir, app_name, template_uri):
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
def update(project_dir, template_uri, version):
    update_command.update(template_uri, project_dir, version=version)
