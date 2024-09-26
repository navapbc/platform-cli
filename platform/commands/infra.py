import click


@click.group()
def infra():
    pass


@infra.command()
def install():
    click.echo("Installing infrastructure...")


@infra.command()
def add_app():
    click.echo("Adding application to infrastructure...")


@infra.command()
def update():
    click.echo("Updating infrastructure...")
