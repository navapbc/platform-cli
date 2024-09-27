import click

import copier
from .get_app_names import get_app_names
from . import add_app_command


def install(template_dir: str, project_dir: str):
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

    if len(get_app_names(template_dir)) == 0:
        app_name = click.prompt("What is the name of your application?")

        add_app_command.add_app(template_dir, project_dir, app_name)

    # options
    # vcs_ref:str
    # data:dict[str,any]
    # exclude:list[str]
    # overwrite=True
    # answers_file relative to project_dir
