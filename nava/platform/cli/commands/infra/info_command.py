import re
from pathlib import Path

import yaml
from packaging.version import Version
from rich.console import Group
from rich.panel import Panel
from rich.table import Table

from nava.platform.cli.context import CliContext
from nava.platform.infra_project import InfraProject
from nava.platform.util.git import GitProject


def info(ctx: CliContext, project_dir: Path, template_uri: str | None = None) -> None:
    project = InfraProject(project_dir)
    is_template = project.base_answers_file().exists()

    if not template_uri and is_template:
        base_answers = yaml.safe_load(project.base_answers_file().read_text())
        template_uri = base_answers.get("_src_path", None)

    # TODO: clone template_uri if appropriate, in context manager to ensure cleanup?
    template_git = None
    if template_uri:
        template_git = GitProject.from_existing(Path(template_uri))

    newer_versions = None
    if is_template:
        newer_versions = get_newer_versions(project.base_template_version(), template_git)

    project_info = Group(
        f"Base version: {project.base_template_version() if is_template else None}",
        f"Newer versions?: {list(map(str, newer_versions)) if newer_versions is not None else 'Unknown. Specify --template-uri to check.'}",
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
            f"Closest upstream version: {closest_template_version_to_legacy if closest_template_version_to_legacy is not None else "Unknown"}",
        )

        ctx.console.print(Panel.fit(legacy_project_info, title="Legacy Project Info"))

    if is_template:
        app_table = Table(title="Apps")
        app_table.add_column("Name")
        app_table.add_column("Template Version")

        for app_name in project.app_names:
            app_table.add_row(app_name, project.app_template_version(app_name))

        ctx.console.print(app_table)

        non_template_app_table = Table(title="Possible Apps (not currently using template)")
        non_template_app_table.add_column("Name")
        for non_template_app_name in sorted(
            set(project.app_names_possible) - set(project.app_names)
        ):
            non_template_app_table.add_row(non_template_app_name)

        ctx.console.print(non_template_app_table)
    elif project.has_legacy_version_file:
        app_table = Table(title="Detected Apps")
        app_table.add_column("Name")

        for app_name in project.app_names_possible:
            app_table.add_row(app_name)

        ctx.console.print(app_table)


def get_newer_versions(
    project_version: str, template_git: GitProject | None = None
) -> list[Version] | None:
    if not template_git:
        return None

    template_tagged_versions = template_git.get_tags("--list", "v*")
    template_versions = sorted(map(Version, template_tagged_versions))

    project_v = get_version(project_version)
    if not project_v:
        return None

    return list(filter(project_v.__le__, template_versions))


# derived from https://github.com/copier-org/copier/blob/63fec9a500d9319f332b489b6d918ecb2e0598e3/copier/template.py#L575
def get_version(v: str) -> Version | None:
    try:
        return Version(v)
    except ValueError:
        if re.match(r"^.+-\d+-g\w+$", v):
            base, count, git_hash = v.rsplit("-", 2)
            return Version(f"{base}.post{count}+{git_hash}")

    return None
