import typer
from pycli_mcp import CommandMCPServer, CommandQuery

# from pycli_mcp.metadata.types.click import walk_commands
# from pycli_mcp.metadata.query import walk_commands
# from typer.main import get_command
from nava.platform.cli.context import CliContext

app = typer.Typer(help="""Model Context Support (MCP) server support.""")


@app.command()
def start(
    typer_context: typer.Context,
) -> None:
    """Start MCP server."""
    ctx = typer_context.ensure_object(CliContext)

    ctx.console.log("Starting MCP server")

    from nava.platform.cli.main import app as full_cli_app

    query = CommandQuery(full_cli_app, aggregate="group")

    # cmds = list(walk_commands(get_command(full_cli_app), aggregate="none"))
    # cmds = list(walk_commands(full_cli_app, aggregate="none"))
    # ctx.console.log(len(cmds))
    # ctx.console.log(cmds)

    server = CommandMCPServer(
        # commands=cmds,
        commands=[query],
        stateless=True,
    )
    server.run()
