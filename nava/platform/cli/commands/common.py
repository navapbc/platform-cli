import typer

opt_template_uri = typer.Option(
    help="Path or URL to template source. Can be a path to a local clone of the template repo.",
)

opt_version = typer.Option(
    help="Template version to install. Can be a branch, tag, commit hash, or 'HEAD' (for latest commit). Defaults to the latest tag version.",
)

# Unfortunately typer doesn't handle args annotated as dictionaries[1], even
# when the dictionary parsing is happening via a `callback`. So we annotate
# `data` as a list of strings, and do the parsing we'd normally do in `callback`
# in the body of the command.
#
# https://github.com/fastapi/typer/issues/130
opt_data = typer.Option(
    help="Parameters in form VARIABLE=VALUE, will make VARIABLE available as VALUE when rendering the template.",
)

opt_commit = typer.Option(help="Commit changes with standard message if able.")

opt_answers_only = typer.Option(help="Do not change the version.")

opt_force_update = typer.Option(help="Ignore smart update algorithm.")
