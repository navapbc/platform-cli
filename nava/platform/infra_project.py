from pathlib import Path

import yaml

from nava.platform.cli.context import CliContext
from nava.platform.get_app_names_from_infra_dir import get_app_names_from_infra_dir
from nava.platform.util import git

RelativePath = Path


class InfraProject:
    project_dir: Path
    git_project: git.GitProject

    def __init__(self, project_dir: Path):
        self.project_dir = project_dir
        self.git_project = git.GitProject(project_dir)

    @property
    def template_version(self) -> str:
        base_version = self.base_template_version()
        app_versions = [self.app_template_version(app_name) for app_name in self.app_names]
        assert all(
            app_version == base_version for app_version in app_versions
        ), "Project template base and app version are out of sync"
        return base_version

    def base_template_version(self) -> str:
        return self._get_template_version_from_answers_file(self.base_answers_file())

    def app_template_version(self, app_name: str) -> str:
        return self._get_template_version_from_answers_file(self.app_answers_file(app_name))

    @property
    def app_names_possible(self) -> list[str]:
        return get_app_names_from_infra_dir(self.project_dir)

    @property
    def app_names(self) -> list[str]:
        app_answer_files = self.project_dir.glob(".template-infra/app-*.yml")
        return list(
            map(lambda f: f.name.removeprefix("app-").removesuffix(".yml"), app_answer_files)
        )

    def base_answers_file_rel(self) -> RelativePath:
        return self.base_answers_file().relative_to(self.project_dir)

    def base_answers_file(self) -> Path:
        return self.project_dir / ".template-infra/base.yml"

    def app_answers_file_rel(self, app_name: str) -> RelativePath:
        return self.app_answers_file(app_name).relative_to(self.project_dir)

    def app_answers_file(self, app_name: str) -> Path:
        return self.project_dir / f".template-infra/app-{app_name}.yml"

    def _get_template_version_from_answers_file(self, answers_file: Path) -> str:
        answers_file_text = answers_file.read_text()
        answers = yaml.safe_load(answers_file_text)
        return str(answers["_commit"])

    #
    # Legacy projects
    #

    @property
    def has_legacy_version_file(self) -> bool:
        return self.legacy_version_file_path().exists()

    def legacy_version_file_path(self) -> Path:
        return self.project_dir / ".template-version"

    def migrate_from_legacy(self, ctx: CliContext, origin_template_uri: str) -> None:
        """
        Create copier answers files in .template-infra
        from the legacy .template-version file
        """
        assert self.has_legacy_version_file
        if not (self.project_dir / ".template-infra").exists():
            (self.project_dir / ".template-infra").mkdir()

        template_version = self.legacy_version_file_path().read_text()
        short_version = template_version[:7]
        common_answers = {
            "_commit": short_version,
            # Copier requires this to be set to a valid template path, and that template git project
            # needs to have _commit as a valid commit hash
            # If _src_path is not set, run_update will raise
            #   UserMessageError("Cannot update because cannot obtain old template references from <answers_file>")
            # If _src_path is set to a folder that does not have _commit as a valid commit hash, then run_update
            # will trigger an error as part of an intenral _check_unsafe method call which will try to
            # check out _commit from _src_path, resulting in the error
            #   error: pathspec '<_commit>' did not match any file(s) known to git
            "_src_path": origin_template_uri,
        }

        base_project_config_answers = self._answers_from_project_config(ctx)

        base_answers = common_answers | base_project_config_answers | {"template": "base"}
        self.base_answers_file().write_text(yaml.dump(base_answers, default_flow_style=False))
        for app_name in self.app_names_possible:
            app_answers = common_answers | {"app_name": app_name, "template": "app"}
            self.app_answers_file(app_name).write_text(
                yaml.dump(app_answers, default_flow_style=False)
            )

    def _answers_from_project_config(self, ctx: CliContext) -> dict[str, str]:
        import json
        import shutil
        import subprocess

        is_terraform_available = shutil.which("terraform") is not None
        project_config_dir = self.project_dir / "infra/project-config"
        project_config_file = project_config_dir / "main.tf"

        if not (project_config_file.exists() and is_terraform_available):
            return {}

        # be sure the local project has the lastest data
        subprocess.run(["terraform", "refresh"], cwd=project_config_dir, stdout=subprocess.DEVNULL)

        # attempt to read the project-config
        result = subprocess.run(
            ["terraform", "output", "-json"],
            cwd=project_config_dir,
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            ctx.console.warning.print(
                "Error from terraform getting project config. Skipping migrating project config automatically."
            )
            return {}

        try:
            project_config = json.loads(result.stdout)
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
