# platform/cli.py
import click
import platform.commands.infra as infra


@click.group()
def cli():
    pass


cli.add_command(infra.infra)


@cli.group()
def app():
    pass


@app.command()
def install():
    click.echo("Installing application...")


@app.command()
def update():
    click.echo("Updating application...")


if __name__ == "__main__":
    cli()
