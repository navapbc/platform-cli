from pathlib import Path
import copier

from nava import git
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

    def install(self, project: Project, app_names: list[str]):
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

        self.add_app(project, "foo")

    def update(self, project: Project):
        num_changes = 0

        git_project = git.GitProject(project.project_dir)

        copier.run_update(
            project.project_dir,
            answers_file=self._base_answers_file_path(),
            exclude=self._base_excludes,
            overwrite=True,
            skip_answered=True,
        )
        git_project.stash()
        num_changes += 1

        for app_name in project.app_names:
            copier.run_update(
                project.project_dir,
                answers_file=self._app_answers_file_path(app_name),
                exclude=list(self._app_excludes),
                overwrite=True,
                skip_answered=True,
            )
            git_project.stash()
            num_changes += 1

        for i in range(num_changes):
            git_project.pop()

    def add_app(self, project: Project, app_name: str):
        data = {"app_name": app_name}

        copier.run_copy(
            str(self.template_dir),
            project.project_dir,
            answers_file=self._app_answers_file(app_name),
            data=data,
            exclude=list(self._app_excludes),
        )

    def version(self):
        pass

    def _compute_excludes(self):
        app_includes, app_excludes = compute_app_includes_excludes(self.template_dir)
        global_excludes = ["*template-only*"]
        self._base_excludes = global_excludes + list(app_includes)
        self._app_excludes = list(app_excludes)

    def _base_answers_file(self):
        return ".template-infra-base.yml"

    def _base_answers_file_path(self):
        return f".template/{self._base_answers_file()}"

    def _app_answers_file(self, app_name: str):
        return f".template-infra-app-{app_name}.yml"

    def _app_answers_file_path(self, app_name: str):
        return f".template/{self._app_answers_file(app_name)}"
