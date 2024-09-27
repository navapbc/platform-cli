import click
import shutil
import os


@click.group()
def infra():
    pass


@infra.command()
@click.argument("template_dir")
@click.argument("project_dir")
def install(template_dir, project_dir):
    shutil.copytree(template_dir, project_dir, dirs_exist_ok=True)


@infra.command()
def add_app():
    click.echo("Adding application to infrastructure...")


@infra.command()
def update():
    click.echo("Updating infrastructure...")
