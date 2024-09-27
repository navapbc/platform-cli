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
    for item in os.listdir(template_dir):
        s = os.path.join(template_dir, item)
        d = os.path.join(project_dir, item)
        if os.path.isdir(s):
            shutil.copytree(s, d, dirs_exist_ok=True)
        else:
            shutil.copy2(s, d)

    click.echo(f"Copied everything from {template_dir} to {project_dir}.")


@infra.command()
def add_app():
    click.echo("Adding application to infrastructure...")


@infra.command()
def update():
    click.echo("Updating infrastructure...")
