import click
import shutil

import copier


@click.group()
def infra():
    pass


@infra.command()
@click.argument("template_dir")
@click.argument("project_dir")
def install(template_dir, project_dir):
    answers_file = ".template-infra-base.yml"
    exclude = ["template-only-*"]
    copier.run_copy(
        template_dir, project_dir, answers_file=answers_file, exclude=exclude
    )
    # options
    # vcs_ref:str
    # data:dict[str,any]
    # exclude:list[str]
    # overwrite=True
    # answers_file relative to project_dir


@infra.command()
def add_app():
    click.echo("Adding application to infrastructure...")


@infra.command()
@click.argument("template_dir")
@click.argument("project_dir")
def update(template_dir, project_dir):
    exclude = ["template-only-*"]
    copier.run_update(template_dir, project_dir, exclude=exclude)
