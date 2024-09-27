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
    data = {"app_name": "template-only"}

    app_includes = [".github/", "infra/{{app_name}}"]
    global_excludes = ["*template-only*"]
    base_excludes = global_excludes + app_includes

    copier.run_copy(
        template_dir,
        project_dir,
        answers_file=answers_file,
        data=data,
        exclude=base_excludes,
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
