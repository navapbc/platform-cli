# platform/cli.py
import click
import platform.commands.infra as infra
import platform.commands.app as app


@click.group()
def cli():
    pass


cli.add_command(infra.infra)
cli.add_command(app.app)

if __name__ == "__main__":
    cli()
