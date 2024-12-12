from rich.panel import Panel

from nava.platform.cli.context import CliContext
from nava.platform.templates.errors import MergeConflictsDuringUpdateError


def exception_handler(ctx: CliContext, e: BaseException) -> None:
    match e:
        case MergeConflictsDuringUpdateError():
            ctx.console.error.print(e.message)
            if e.commit_msg:
                ctx.console.print(Panel(e.commit_msg, title="Prepared commit message"))
            ctx.exit(1)
        case _:
            raise e
