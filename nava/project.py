from pathlib import Path

from nava import git
from nava.commands.infra.get_app_names import get_app_names


class Project:
    project_dir: Path
    git_project: git.GitProject

    def __init__(self, project_dir: Path):
        self.project_dir = project_dir
        self.git_project = git.GitProject(project_dir)

    def template_version(self):
        pass

    @property
    def app_names(self):
        return get_app_names(self.project_dir)
