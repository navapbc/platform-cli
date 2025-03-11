from pathlib import Path
from typing import Annotated, cast

import questionary
import typer

import nava.platform.util.collections.dict as dict_util
from nava.platform.cli.commands.common import (
    opt_answers_only,
    opt_commit,
    opt_data,
    opt_force_update,
    opt_template_uri,
    opt_version,
)
from nava.platform.cli.context import CliContext
from nava.platform.projects.migrate_from_legacy_template import MigrateFromLegacyTemplate
from nava.platform.projects.project import Project
from nava.platform.templates.template import Template

app = typer.Typer(help="Manage application templates")


@app.command()
def install(
    typer_context: typer.Context,
    project_dir: Annotated[
        Path,
        typer.Argument(
            file_okay=False,
        ),
    ],
    app_name: Annotated[str, typer.Argument(help="What to call the new application")],
    template_uri: Annotated[str, opt_template_uri],
    version: Annotated[str | None, opt_version] = None,
    data: Annotated[list[str] | None, opt_data] = None,
    commit: Annotated[bool, opt_commit] = False,
    template_name: Annotated[
        str | None,
        typer.Option(
            help="The name of the template. Usually this can be derived from the repository name automatically, but if you are running from a local checkout under a different name, you will need to specify the upstream name here."
        ),
    ] = None,
) -> None:
    """Install application template in project."""
    ctx = typer_context.ensure_object(CliContext)

    with ctx.handle_exceptions():
        template = Template(ctx, template_uri=template_uri, template_name=template_name)
        project = Project(project_dir)
        template.install(
            project=project,
            app_name=app_name,
            version=version,
            data=dict_util.from_str_values(data),
            commit=commit,
        )


@app.command()
def update(
    typer_context: typer.Context,
    project_dir: Annotated[
        Path,
        typer.Argument(
            exists=True,
            file_okay=False,
        ),
    ],
    app_name: Annotated[
        str, typer.Argument(help="Name of the application based on given template to update")
    ],
    template_uri: Annotated[str | None, opt_template_uri] = None,
    version: Annotated[str | None, opt_version] = None,
    data: Annotated[list[str] | None, opt_data] = None,
    commit: Annotated[bool, opt_commit] = True,
    template_name: Annotated[
        str | None,
        typer.Option(
            help="The name of the template. Usually this can be derived from the repository name automatically, but if you are running from a local checkout under a different name, you will need to specify the upstream name here."
        ),
    ] = None,
    answers_only: Annotated[bool, opt_answers_only] = False,
    force: Annotated[bool, opt_force_update] = False,
) -> None:
    """Update application based on template in project."""
    ctx = typer_context.ensure_object(CliContext)

    with ctx.handle_exceptions():
        project = Project(project_dir)

        if template_uri:
            template = Template(ctx, template_uri=template_uri, template_name=template_name)
        else:
            installed_templates_for_app = list(
                filter(
                    lambda t_name: t_name != "template-infra",
                    project.installed_template_names_for_app(app_name),
                )
            )

            if len(installed_templates_for_app) == 1:
                template_name = installed_templates_for_app[0]
            else:
                template_name = cast(
                    str,
                    questionary.select(
                        f"Which template for {app_name}?",
                        choices=installed_templates_for_app,
                        use_search_filter=True,
                        use_jk_keys=False,
                    ).unsafe_ask(),
                )

            template = Template.from_existing(
                ctx, project, app_name=app_name, template_name=template_name
            )

        ctx.console.rule(f"{app_name} ({template.template_name.id})")
        template.update(
            project=project,
            app_name=app_name,
            version=version,
            data=dict_util.from_str_values(data),
            commit=commit,
            answers_only=answers_only,
            force=force,
        )


@app.command()
def migrate_from_legacy(
    typer_context: typer.Context,
    project_dir: Annotated[
        Path,
        typer.Argument(
            exists=True,
            file_okay=False,
        ),
    ],
    origin_template_uri: Annotated[
        str,
        typer.Option(
            help="Path or URL to the legacy template that was used to set up the project. Can be a path to a local clone of the template.",
        ),
    ],
    app_name: Annotated[
        str, typer.Argument(help="Name of the application based on given template to migrate")
    ],
    commit: Annotated[bool, opt_commit] = True,
    legacy_version_file: Annotated[
        Path | None,
        typer.Option(
            exists=True,
            dir_okay=False,
            readable=True,
            resolve_path=True,
            help="Relative path to the old version file",
        ),
    ] = None,
) -> None:
    """Migrate an older version of a template to platform-cli setup."""
    ctx = typer_context.ensure_object(CliContext)

    with ctx.handle_exceptions():
        project = Project(project_dir)
        MigrateFromLegacyTemplate(
            ctx,
            project,
            origin_template_uri=origin_template_uri,
            new_version_answers_file_name=app_name + ".yml",
            legacy_version_file_name=str(legacy_version_file.relative_to(project.dir.resolve()))
            if legacy_version_file
            else None,
        ).migrate_from_legacy(commit=commit)
