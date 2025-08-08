from enum import Enum
from pathlib import Path
from typing import Annotated, Any

import typer
from pydantic_core import to_json
from rich.console import Console
from rich.table import Table

import nava.platform.projects.info
from nava.platform.cli.context import CliContext
from nava.platform.projects.info import ProjectInfo, TemplateInfo
from nava.platform.projects.project import Project
from nava.platform.templates.template_name import TemplateId, TemplateName

app = typer.Typer(help="Get info about platform usage in the project")


class OutputType(str, Enum):
    console = "console"
    json = "json"


@app.command()
def info(
    typer_context: typer.Context,
    project_dir: Annotated[
        Path,
        typer.Argument(
            file_okay=False,
        ),
    ],
    output: OutputType = OutputType.console,
    offline: bool = False,
) -> None:
    """Get info about platform usage in the project."""
    ctx = typer_context.ensure_object(CliContext)

    with ctx.handle_exceptions():
        project = Project(project_dir)

        project_info = nava.platform.projects.info.project_info(project, offline=offline)

        match output:
            case OutputType.console:
                _console_output(ctx.console, project_info)
            case OutputType.json:
                _json_output(ctx.console, project_info)


def _console_output(console: Console, project_info: ProjectInfo) -> None:
    if not project_info.template_ids:
        console.print("It appears this is not a project using the Nava Platform.")
        return

    # console.rule("Info")
    console.print(f"Project name: {project_info.name}")
    console.print(f"Project templates: {project_info.template_ids}")
    # ctx.console.print(list(project.installed_template_names()))
    # ctx.console.rule(f"{app_name} ({template.template_name.id})")

    console.print("")

    template_table = Table(title="Templates", show_lines=True)
    template_table.add_column("Name")
    template_table.add_column("Version(s)")
    template_table.add_column("Versions match")
    template_table.add_column("Newer releases")

    for template_id in project_info.template_ids:
        instances_of_template = []

        for app in project_info.apps:
            template = app.get_template(template_id)
            if template:
                instances_of_template.append(template)

        # handle non-app template
        if not instances_of_template:
            template_answers_file = next(
                (k for k, v in project_info.template_answers_to_id.items() if v == template_id),
                None,
            )

            if template_answers_file:
                template_answers = project_info.template_answers_raw.get(template_answers_file)

                if template_answers:
                    template_info = TemplateInfo.from_answers(
                        template_id,
                        template_answers,
                    )

                    instances_of_template.append(template_info)

        all_instance_versions = set([ti.version for ti in instances_of_template if ti.version])
        all_instance_versions_match = len(all_instance_versions) == 1

        newer_releases = []
        if all_instance_versions_match:
            newer_releases = instances_of_template[0].newer_releases()

        template_table.add_row(
            display_template_id(template_id),
            ", ".join(v.display_str for v in all_instance_versions),
            str(all_instance_versions_match),
            ", ".join(map(str, newer_releases)),
        )

    console.print(template_table)

    console.print("")

    app_table = Table(title="Apps", show_lines=True)
    app_table.add_column("Name")
    app_table.add_column("Templates")
    for app in project_info.apps:
        template_table = Table(show_header=False)
        # template_table.add_column("ID")
        # template_table.add_column("Version")
        for template_info in app.templates:
            template_version_str = "unknown version"
            if template_info.version:
                template_version_str = template_info.version.display_str

            template_table.add_row(
                display_template_id(template_info),
                template_version_str,
            )

        app_table.add_row(app.name, template_table)

    console.print(app_table)


def display_template_id(t: TemplateId | TemplateName | TemplateInfo) -> str:
    display_str = t.id if isinstance(t, TemplateName | TemplateInfo) else t

    return display_str.removeprefix("template-")


def _json_output(console: Console, project_info: ProjectInfo) -> None:
    console.print_json(
        to_json(project_info, fallback=_json_encoding_fallback).decode(encoding="utf-8")
    )


def _json_encoding_fallback(value: Any) -> Any:
    from packaging.version import Version

    if isinstance(value, Version):
        return str(value)
