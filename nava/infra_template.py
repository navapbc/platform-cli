from pathlib import Path
import copier

from nava.commands.infra import add_app_command
from nava.commands.infra.compute_app_includes_excludes import (
    compute_app_includes_excludes,
)
from nava.project import Project


class InfraTemplate:
    template_dir: Path
    _base_excludes: list[str]
    _app_excludes: list[str]

    def __init__(self, template_dir: Path):
        self.template_dir = template_dir

        self._compute_excludes()

    def install(self, project: Project):
        data = {"app_name": "template-only"}

        print("Running copier with parameters:")
        print(f"  template_dir: {self.template_dir}")
        print(f"  project_dir: {project.project_dir}")
        print(f"  answers_file: {self._base_answers_file()}")
        print(f"  data: {data}")
        print(f"  exclude: {self._base_excludes}")
        copier.run_copy(
            str(self.template_dir),
            project.project_dir,
            answers_file=self._base_answers_file(),
            data=data,
            exclude=self._base_excludes,
        )

        add_app_command.add_app(self.template_dir, str(project.project_dir), "foo")

    def update(self, project: Project):
        pass

    def add_app(self, project: Project, app_name: str):
        pass

    def version(self):
        pass

    def _compute_excludes(self):
        app_includes, app_excludes = compute_app_includes_excludes(self.template_dir)
        global_excludes = ["*template-only*"]
        self._base_excludes = global_excludes + list(app_includes)
        self._app_excludes = list(app_excludes)

    def _base_answers_file(self):
        return ".template-infra-base.yml"

    def _app_answers_file(self, app_name: str):
        return f".template-infra-app-{app_name}.yml"
