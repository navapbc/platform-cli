import click

import copier

from . import install_command, update_command


@click.group()
def infra():
    pass


@infra.command()
@click.argument("template_dir")
@click.argument("project_dir")
def install(template_dir, project_dir):
    install_command.install(template_dir, project_dir)


@infra.command()
def add_app():
    click.echo("Adding application to infrastructure...")


@infra.command()
@click.argument("template_dir")
@click.argument("project_dir")
def update(template_dir, project_dir):
    update_command.update(template_dir, project_dir)
