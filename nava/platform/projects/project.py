import itertools
from collections.abc import Iterable
from dataclasses import dataclass
from functools import cached_property
from pathlib import Path

from nava.platform.projects.get_app_names_from_infra_dir import get_app_names_from_infra_dir
from nava.platform.projects.get_app_names_from_template_answers import (
    get_app_names_from_template_answers,
)
from nava.platform.templates.state import (
    TemplateVersionAnswer,
    get_template_version_from_answers,
    read_answers_file,
    template_names_from_answers_files,
    template_names_from_project_state_dir,
    template_repo_name_from_project_state_dir,
)
from nava.platform.templates.template_name import TemplateName
from nava.platform.util import git


@dataclass
class Project:
    dir: Path

    @cached_property
    def git(self) -> git.GitProject:
        return git.GitProject(self.dir)

    @property
    def installed_app_names_possible(self) -> frozenset[str]:
        return get_app_names_from_infra_dir(self.dir) | get_app_names_from_template_answers(
            self.dir
        )

    def installed_template_repo_names(self) -> frozenset[str]:
        return frozenset(
            map(template_repo_name_from_project_state_dir, self._installed_template_state_dirs())
        )

    def installed_template_names(self) -> frozenset[TemplateName]:
        return frozenset(
            itertools.chain.from_iterable(
                map(template_names_from_project_state_dir, self._installed_template_state_dirs())
            )
        )

    def installed_template_names_for_app(self, app_name: str) -> Iterable[TemplateName]:
        answer_files = self._installed_template_answer_files_for_app(app_name)

        return template_names_from_answers_files(answer_files)

    def _installed_template_state_dirs(self) -> Iterable[Path]:
        return filter(lambda f: f.is_dir(), self.dir.glob(".template-*"))

    def _installed_template_answer_files_for_app(self, app_name: str) -> Iterable[Path]:
        answer_files = filter(
            lambda f: f.is_file()
            # account for apps named "app", which conflicts with naming schemes
            # for some templates using the simple glob
            and (f.name == app_name + ".yml" or f.name == "app-" + app_name + ".yml"),
            self.dir.glob(f".template-*/*{app_name}*"),
        )

        return answer_files

    def _get_template_version_from_answers_file(self, answers_file: Path) -> TemplateVersionAnswer:
        answers = read_answers_file(answers_file)
        version = get_template_version_from_answers(answers)

        # TODO: should handle this better
        if version is None:
            raise Exception("Template state is malformed.")

        return version
