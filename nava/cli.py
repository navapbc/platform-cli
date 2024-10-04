import click
import nava.commands.infra as infra
import nava.commands.app as app


@click.group()
def cli() -> None:
    pass


cli.add_command(infra.infra)
cli.add_command(app.app)

if __name__ == "__main__":
    cli()
