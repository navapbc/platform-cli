import click

import nava.platform.cli.commands.app as app
import nava.platform.cli.commands.infra as infra
import nava.platform.cli.console
import nava.platform.cli.logging
from nava.platform.cli.config import OutputLevel
from nava.platform.cli.context import CliContext


@click.group()
@click.option("-v", "--verbose", count=True, help="Increase verbosity")
@click.option("-q", "--quiet", is_flag=True, help="Limit output")
@click.pass_context
def cli(ctx: click.Context, verbose: int, quiet: bool) -> None:
    output_level = resolve_verbosity(verbose, quiet)
    log = nava.platform.cli.logging.initialize(output_level)
    console = nava.platform.cli.console.initialize(output_level)

    ctx.obj = CliContext(
        output_level=output_level,
        log=log.bind(),
        console=console,
        fail=ctx.fail,
        exit=ctx.exit,
    )


def resolve_verbosity(verbose: int, quiet: bool) -> OutputLevel:
    # In the context of logging:
    # VERBOSE -> enable debug mode logging to file
    # DEBUG -> print logs on screen
    #
    # In the context of the CLI's own output:
    # NONE -> print nothing
    # NORMAL -> normal
    # VERBOSE -> if there's extra info that could be provided, print it
    # DEBUG -> same as VERBOSE, but logs will now be printed as well
    if quiet:
        return OutputLevel.NONE

    if verbose == 0:
        return OutputLevel.NORMAL

    if verbose == 1:
        return OutputLevel.VERBOSE

    return OutputLevel.DEBUG


cli.add_command(infra.infra)
cli.add_command(app.app)

if __name__ == "__main__":
    cli()
