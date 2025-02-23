from pathlib import Path
from typing import cast

import questionary

from nava.platform.cli.context import CliContext
from nava.platform.projects.infra_project import InfraProject
from nava.platform.templates.infra_template import InfraTemplate


def update(
    ctx: CliContext,
    project_dir: str,
    template_uri: str | None = None,
    version: str | None = None,
    data: dict[str, str] | None = None,
    answers_only: bool = False,
    force: bool = False,
) -> None:
    project = InfraProject(Path(project_dir))

    if template_uri:
        template = InfraTemplate(ctx, template_uri)
    else:
        template = InfraTemplate.from_existing(ctx, project)

    template.update(project, version=version, data=data, answers_only=answers_only, force=force)


def update_base(
    ctx: CliContext,
    project_dir: str,
    template_uri: str | None = None,
    version: str | None = None,
    data: dict[str, str] | None = None,
    commit: bool = False,
    answers_only: bool = False,
    force: bool = False,
) -> None:
    project = InfraProject(Path(project_dir))

    if template_uri:
        template = InfraTemplate(ctx, template_uri)
    else:
        template = InfraTemplate.from_existing(ctx, project)

    template.update_base(
        project, version=version, data=data, commit=commit, answers_only=answers_only, force=force
    )


def update_app(
    ctx: CliContext,
    project_dir: str,
    template_uri: str | None = None,
    app_names: list[str] | None = None,
    version: str | None = None,
    data: dict[str, str] | None = None,
    commit: bool = False,
    all: bool = True,
    answers_only: bool = False,
    force: bool = False,
) -> None:
    project = InfraProject(Path(project_dir))

    if template_uri:
        template = InfraTemplate(ctx, template_uri)
    else:
        template = InfraTemplate.from_existing(ctx, project)

    if all:
        if not commit:
            ctx.fail("If using --all, must also specify --commit.")

        if app_names:
            ctx.fail("If using --all, don't specify app names as arguments")

        app_names = project.app_names
    else:
        if not app_names:
            if len(project.app_names) == 1:
                app_names = project.app_names
                ctx.console.print(f"Only one app detected, updating '{app_names[0]}'")
            else:
                app_names = cast(
                    list[str],
                    questionary.checkbox(
                        "Which app(s)?",
                        choices=project.app_names,
                        use_search_filter=True,
                        use_jk_keys=False,
                        validate=lambda choices: "You must choose at least one app to update"
                        if not choices
                        else True,
                    ).unsafe_ask(),
                )
        elif wrong_app_names := sorted(list(set(app_names).difference(project.app_names))):
            if len(wrong_app_names) == 1:
                ctx.console.error.print(f"App '{wrong_app_names[0]}' does not exist in the project")
            else:
                ctx.console.error.print(f"Apps {wrong_app_names} do not exist in the project")
            ctx.exit(1)

    if not app_names:
        ctx.fail("No apps found")

    for app_name in app_names:
        ctx.console.rule(f"Infra app: {app_name}")
        template.update_app(
            project,
            app_name,
            version=version,
            data=data,
            commit=commit,
            answers_only=answers_only,
            force=force,
        )
