from pathlib import Path
import re

from nava import git
from nava.commands.infra.get_app_names import get_app_names


class Project:
    project_dir: Path
    git_project: git.GitProject

    _template_version_regex: re.Pattern

    def __init__(self, project_dir: Path):
        self.project_dir = project_dir
        self.git_project = git.GitProject(project_dir)

        self._template_version_regex = re.compile(r"_commit: (\w+)")

    @property
    def template_version(self):
        base_version = self._get_template_version_from_answers_file(
            self._base_answers_file()
        )
        app_versions = [
            self._get_template_version_from_answers_file(
                self._app_answers_file(app_name)
            )
            for app_name in self.app_names
        ]
        assert all(app_version == base_version for app_version in app_versions)
        return base_version

    @property
    def app_names(self):
        return get_app_names(self.project_dir)

    def _base_answers_file(self):
        return self.project_dir / ".template/.template-infra-base.yml"

    def _app_answers_file(self, app_name: str):
        return self.project_dir / f".template/.template-infra-app-{app_name}.yml"

    def _get_template_version_from_answers_file(self, answers_file: Path):
        answers_file_text = answers_file.read_text()
        return self._template_version_regex.search(answers_file_text).group(1)
