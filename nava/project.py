from pathlib import Path

import yaml

from nava import git
from nava.commands.infra.get_app_names import get_app_names


class Project:
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
    def app_names(self) -> list[str]:
        return get_app_names(self.project_dir)

    def base_answers_file(self) -> str:
        return ".template-infra/base.yml"

    def app_answers_file(self, app_name: str) -> str:
        return f".template-infra/app-{app_name}.yml"

    def _get_template_version_from_answers_file(self, answers_file: str) -> str:
        answers_file_text = (self.project_dir / answers_file).read_text()
        answers = yaml.safe_load(answers_file_text)
        return str(answers["_commit"])

    #
    # Legacy projects
    #

    @property
    def has_legacy_version_file(self) -> bool:
        return (self.project_dir / ".template-version").exists()

    def migrate_from_legacy(self, origin_template_uri: str) -> None:
        """
        Create copier answers files in .template-infra
        from the legacy .template-version file
        """
        assert self.has_legacy_version_file
        if not (self.project_dir / ".template-infra").exists():
            (self.project_dir / ".template-infra").mkdir()

        template_version = (self.project_dir / ".template-version").read_text()
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

        base_answers = common_answers | {"app_name": "template-only"}
        (self.project_dir / self.base_answers_file()).write_text(
            yaml.dump(base_answers, default_flow_style=False)
        )
        for app_name in self.app_names:
            app_answers = common_answers | {"app_name": app_name}
            (self.project_dir / self.app_answers_file(app_name)).write_text(
                yaml.dump(app_answers, default_flow_style=False)
            )
