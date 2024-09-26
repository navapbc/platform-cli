import click


@click.group()
def app():
    pass


@app.command()
def install():
    click.echo("Installing application...")


@app.command()
def update():
    click.echo("Updating application...")
