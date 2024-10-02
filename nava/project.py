from pathlib import Path

from nava.commands.infra.get_app_names import get_app_names


class Project:
    def __init__(self, project_dir: Path):
        self.project_dir = project_dir

    def template_version(self):
        pass

    @property
    def app_names(self):
        return get_app_names(self.project_dir)
