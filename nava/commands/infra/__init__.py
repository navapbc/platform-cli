import click


@click.group()
def infra():
    pass


@infra.command()
@click.argument("template_dir")
@click.argument("project_dir")
def install(template_dir, project_dir):
    pass
    # click.echo(
    #     f"Installing infrastructure from template {template_dir} to project {project_dir}..."
    # )


@infra.command()
def add_app():
    click.echo("Adding application to infrastructure...")


@infra.command()
def update():
    click.echo("Updating infrastructure...")
