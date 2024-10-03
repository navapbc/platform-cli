import click

import copier

from . import add_app_command, install_command, update_command


@click.group()
def infra():
    pass


@infra.command()
@click.argument("project_dir")
@click.option(
    "--src",
    default="https://github.com/navapbc/template-infra.git",
    help="Path or URL to infra template. Can be a path to a local clone of template-infra. Defaults to the template-infra repository on GitHub.",
)
def install(project_dir, src):
    install_command.install(src, project_dir)


@infra.command()
@click.argument("template_dir")
@click.argument("project_dir")
@click.argument("app_name")
def add_app(template_dir, project_dir, app_name):
    add_app_command.add_app(template_dir, project_dir, app_name)


@infra.command()
@click.argument("template_dir")
@click.argument("project_dir")
def update(template_dir, project_dir):
    update_command.update(template_dir, project_dir)
