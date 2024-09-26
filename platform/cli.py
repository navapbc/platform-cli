# platform/cli.py
import click


@click.group()
def cli():
    pass


@cli.group()
def infra():
    pass


@cli.group()
def app():
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


@app.command()
def install():
    click.echo("Installing application...")


@app.command()
def update():
    click.echo("Updating application...")


if __name__ == "__main__":
    cli()
