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
        base_version = self._get_template_version_from_answers_file(self.base_answers_file())
        app_versions = [
            self._get_template_version_from_answers_file(self.app_answers_file(app_name))
            for app_name in self.app_names
        ]
        assert all(app_version == base_version for app_version in app_versions)
        return base_version

    @property
    def app_names(self) -> list[str]:
        return get_app_names(self.project_dir)

    def base_answers_file(self) -> str:
        return ".template-infra/.template-infra-base.yml"

    def app_answers_file(self, app_name: str) -> str:
        return f".template-infra/.template-infra-app-{app_name}.yml"

    def _get_template_version_from_answers_file(self, answers_file: str) -> str:
        answers_file_text = (self.project_dir / answers_file).read_text()
        answers = yaml.safe_load(answers_file_text)
        return str(answers["_commit"])
