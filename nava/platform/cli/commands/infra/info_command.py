from pathlib import Path

import yaml
from rich.console import Group
from rich.panel import Panel
from rich.table import Table

from nava.platform.cli.context import CliContext
from nava.platform.projects.infra_project import InfraProject
from nava.platform.templates.util import get_newer_releases, get_template_git


def info(ctx: CliContext, project_dir: Path, template_uri: str | None = None) -> None:
    project = InfraProject(project_dir)
    is_template = project.base_answers_file().exists()

    if not template_uri and is_template:
        base_answers = yaml.safe_load(project.base_answers_file().read_text())
        template_uri = base_answers.get("_src_path", None)

    with get_template_git(template_uri) as template_git:
        newer_releases = None
        if is_template:
            newer_releases = get_newer_releases(project.base_template_version(), template_git)

        project_info = Group(
            f"Base version: {project.base_template_version() if is_template else None}",
            f"Newer releases?: {list(map(str, newer_releases)) if newer_releases is not None else 'Unknown. Specify --template-uri to check.'}",
        )

        ctx.console.print(Panel.fit(project_info, title="Project Info"))

        if project.has_legacy_version_file:
            legacy_template_version = (
                project.legacy_version_file_path().read_text().strip()
                if project.has_legacy_version_file
                else None
            )

            closest_template_version_to_legacy = None
            if legacy_template_version and template_git:
                closest_template_version_to_legacy = template_git.get_closest_tag(
                    legacy_template_version
                )

            legacy_project_info = Group(
                f"Has legacy version?: {project.has_legacy_version_file} {'(' + legacy_template_version + ')' if legacy_template_version else ''}",
                f"Closest upstream version: {closest_template_version_to_legacy if closest_template_version_to_legacy is not None else 'Unknown'}",
            )

            ctx.console.print(Panel.fit(legacy_project_info, title="Legacy Project Info"))

        if is_template:
            app_table = Table(title="Apps")
            app_table.add_column("Name")
            app_table.add_column("Template Version")

            for app_name in project.app_names:
                app_table.add_row(app_name, project.app_template_version(app_name))

            ctx.console.print(app_table)

            non_template_app_names = set(project.app_names_possible) - set(project.app_names)

            if non_template_app_names:
                non_template_app_table = Table(title="Possible Apps (not currently using template)")
                non_template_app_table.add_column("Name")
                for non_template_app_name in sorted(non_template_app_names):
                    non_template_app_table.add_row(non_template_app_name)

                ctx.console.print(non_template_app_table)
        elif project.has_legacy_version_file:
            app_table = Table(title="Detected Apps")
            app_table.add_column("Name")

            for app_name in project.app_names_possible:
                app_table.add_row(app_name)

            ctx.console.print(app_table)
