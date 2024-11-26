from typing import Annotated

import typer

import nava.platform.cli.commands.app as app_command
import nava.platform.cli.commands.infra as infra
import nava.platform.cli.console
import nava.platform.cli.logging
from nava.platform.cli.config import OutputLevel
from nava.platform.cli.context import CliContext

app = typer.Typer()


@app.callback()
def main(
    ctx: typer.Context,
    verbose: Annotated[
        int,
        typer.Option(
            "-v",
            "--verbose",
            count=True,
            help="Increase verbosity. Add enough -v's and you'll get the logs printed to your screen. Enjoy.",
        ),
    ] = 0,
    quiet: Annotated[
        bool, typer.Option("-q", "--quiet", help="Disable all console output")
    ] = False,
) -> None:
    """Tool to help manage using Nava PBC's platform work"""
    output_level = resolve_verbosity(verbose, quiet)
    log = nava.platform.cli.logging.initialize(output_level)
    console = nava.platform.cli.console.initialize(output_level)

    ctx.obj = CliContext(
        output_level=output_level,
        log=log.bind(),
        console=console,
        fail_with_usage=ctx.fail,
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

    if verbose == 2:
        return OutputLevel.DEBUG

    return OutputLevel.TRACE


app.add_typer(infra.app, name="infra")
app.add_typer(app_command.app, name="app")

if __name__ == "__main__":
    app()
