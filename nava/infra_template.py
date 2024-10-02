import functools
import inspect
from pathlib import Path
from typing import Callable, ParamSpec, TypeVar, get_type_hints
import copier

from nava import git
from nava.commands.infra.compute_app_includes_excludes import (
    compute_app_includes_excludes,
)
from nava.project import Project

P = ParamSpec("P")
R = TypeVar("R")


def print_method_call(func: Callable[P, R]) -> Callable[P, R]:
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        print(f"Calling: {func.__name__} with args:\n{args}\n and kwargs:\n{kwargs}")
        return func(*args, **kwargs)

    return wrapper


class InfraTemplate:
    template_dir: Path
    git_project: git.GitProject

    _base_excludes: list[str]
    _app_excludes: list[str]

    def __init__(self, template_dir: Path):
        self.template_dir = template_dir
        self.git_project = git.GitProject(template_dir)

        self._compute_excludes()
        self._run_copy = print_method_call(copier.run_copy)
        self._run_update = print_method_call(copier.run_update)

    def install(self, project: Project, app_names: list[str]):
        data = {"app_name": "template-only"}
        self._run_copy(
            str(self.template_dir),
            project.project_dir,
            answers_file=self._base_answers_file(),
            data=data,
            exclude=self._base_excludes,
        )

        for app_name in app_names:
            self.add_app(project, app_name)

    def update(self, project: Project):
        num_changes = 0

        data = {"app_name": "template-only"}

        self._run_update(
            project.project_dir,
            data=data,
            answers_file=project.base_answers_file(),
            exclude=self._base_excludes,
            overwrite=True,
            skip_answered=True,
        )
        project.git_project.stash()
        num_changes += 1

        for app_name in project.app_names:
            data = {"app_name": app_name}
            self._run_update(
                project.project_dir,
                data=data,
                answers_file=project.app_answers_file(app_name),
                exclude=list(self._app_excludes),
                overwrite=True,
                skip_answered=True,
            )
            project.git_project.stash()
            num_changes += 1

        for _ in range(num_changes):
            project.git_project.pop()

    def add_app(self, project: Project, app_name: str):
        data = {"app_name": app_name}
        self._run_copy(
            str(self.template_dir),
            project.project_dir,
            answers_file=self._app_answers_file(app_name),
            data=data,
            exclude=list(self._app_excludes),
        )

    @property
    def version(self):
        return self.git_project.commit_hash()

    @property
    def short_version(self):
        return self.version[:7]

    def _compute_excludes(self):
        app_includes, app_excludes = compute_app_includes_excludes(self.template_dir)
        global_excludes = ["*template-only*"]
        self._base_excludes = global_excludes + list(app_includes)
        self._app_excludes = list(app_excludes)

    def _base_answers_file(self):
        return ".template-infra-base.yml"

    def _app_answers_file(self, app_name: str):
        return f".template-infra-app-{app_name}.yml"
