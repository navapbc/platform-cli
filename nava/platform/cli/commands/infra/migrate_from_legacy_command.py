from pathlib import Path

from nava.platform.cli.context import CliContext
from nava.platform.projects.infra_project import InfraProject
from nava.platform.projects.migrate_from_legacy_template import MigrateFromLegacyTemplate


def migrate_from_legacy(
    ctx: CliContext, project_dir: str, origin_template_uri: str, commit: bool = False
) -> None:
    project = InfraProject(Path(project_dir))

    if not project.has_legacy_version_file:
        ctx.console.error.print(
            f"No legacy version file found (looking for {project.legacy_version_file_path()}). Are you sure this is a legacy template?"
        )
        ctx.exit(1)

    _migrate_from_legacy(ctx, project, origin_template_uri, commit)


def _migrate_from_legacy(
    ctx: CliContext, infra_project: InfraProject, origin_template_uri: str, commit: bool
) -> None:
    base_project_config_answers = _answers_from_project_config(ctx, infra_project.dir)

    project = infra_project

    base_migrate = MigrateFromLegacyTemplate(
        ctx=ctx,
        project=project,
        origin_template_uri=origin_template_uri,
        template_name="template-infra",
        legacy_version_file_name=".template-version",
        new_version_answers_file_name="base.yml",
        extra_answers=lambda _: (base_project_config_answers | {"template": "base"}),
    )
    base_migrate.migrate_from_legacy(preserve_legacy_file=True, commit=commit)

    for app_name in infra_project.app_names_possible:
        app_answers = {"app_name": app_name, "template": "app"}
        app_migrate = MigrateFromLegacyTemplate(
            ctx=ctx,
            project=project,
            origin_template_uri=origin_template_uri,
            template_name="template-infra",
            legacy_version_file_name=".template-version",
            new_version_answers_file_name=f"app-{app_name}.yml",
            extra_answers=lambda _: app_answers,  # noqa: B023
        )
        app_migrate.migrate_from_legacy(preserve_legacy_file=True, commit=commit)

    # remove the old file once we are done with it
    ctx.console.print(f"Deleting legacy file ({base_migrate.legacy_version_file_path()})")
    base_migrate.legacy_version_file_path().unlink()

    if commit and project.git.is_git():
        project.git.commit_all("Remove legacy version file")


def _answers_from_project_config(ctx: CliContext, project_dir: Path) -> dict[str, str]:
    import json
    import shutil
    import subprocess

    is_terraform_available = shutil.which("terraform") is not None
    project_config_dir = project_dir / "infra/project-config"
    project_config_file = project_config_dir / "main.tf"

    if not (project_config_file.exists() and is_terraform_available):
        return {}

    # be sure the local project has the lastest data
    refresh_result = subprocess.run(
        ["terraform", "refresh"], cwd=project_config_dir, capture_output=True, text=True
    )
    if refresh_result.returncode != 0:
        ctx.console.warning.print(
            "Error from terraform getting project config. Skipping migrating project config automatically."
        )
        ctx.console.error.print(refresh_result.stderr)
        return {}

    # attempt to read the project-config
    output_result = subprocess.run(
        ["terraform", "output", "-json"],
        cwd=project_config_dir,
        capture_output=True,
        text=True,
    )
    if output_result.returncode != 0:
        ctx.console.warning.print(
            "Error from terraform getting project config. Skipping migrating project config automatically."
        )
        ctx.console.error.print(refresh_result.stderr)
        return {}

    try:
        project_config = json.loads(output_result.stdout)
    except json.JSONDecodeError:
        ctx.console.warning.print(
            "Error parsing JSON response from terraform. Skipping migrating project config automatically."
        )
        return {}

    if not isinstance(project_config, dict):
        ctx.console.warning.print(
            "Project config is not in the expected format. Skipping migrating project config automatically."
        )
        return {}

    mapping = {
        "base_project_name": "project_name",
        "base_owner": "owner",
        "base_code_repository_url": "code_repository_url",
        "base_default_region": "default_region",
    }

    answers = {}
    for answer_key, project_config_key in mapping.items():
        project_config_output = project_config.get(project_config_key, None)
        if not project_config_output:
            continue

        project_config_value = project_config_output.get("value", None)
        if clean_answer := str(project_config_value).strip():
            answers[answer_key] = clean_answer

    return answers
