import click


@click.group()
def app() -> None:
    pass


@app.command()
def install() -> None:
    click.echo("Installing application...")


@app.command()
def update() -> None:
    click.echo("Updating application...")
