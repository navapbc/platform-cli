import click

import nava.platform.cli.commands.app as app
import nava.platform.cli.commands.infra as infra


@click.group()
def cli() -> None:
    pass


cli.add_command(infra.infra)
cli.add_command(app.app)

if __name__ == "__main__":
    cli()
