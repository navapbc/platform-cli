from dataclasses import dataclass
from functools import cache, partial
from pathlib import Path
from typing import Self

from packaging.version import Version

import nava.platform.templates.util as template_utils
from nava.platform.projects.project import Project
from nava.platform.templates.state import (
    Answers,
    TemplateVersionAnswer,
    get_template_uri_for_existing_app,
    get_template_uri_from_answers,
    get_template_version_for_existing_app,
    get_template_version_from_answers,
    read_answers_file,
    template_names_from_answers_files,
)
from nava.platform.templates.template_name import TemplateId, TemplateName


@cache
def cached_template_releases(template_uri: str) -> list[Version]:
    with template_utils.get_template_git(template_uri) as template_git:
        if not template_git:
            return []

        return template_utils.get_releases(template_git)


def cached_newer_releases(template_uri: str, current_version: str) -> list[Version]:
    return (
        template_utils.get_newer_releases(
            current_version, template_versions=cached_template_releases(template_uri)
        )
        or []
    )


@dataclass(frozen=True)
class TemplateInfo:
    id: TemplateId
    name: TemplateName
    version: TemplateVersionAnswer | None
    src_uri: str | None

    @classmethod
    def from_answers(cls, template: TemplateName | TemplateId, answers: Answers | None) -> Self:
        template_name = TemplateName.parse(template)
        return cls(
            id=template_name.id,
            name=template_name,
            version=get_template_version_from_answers(answers),
            src_uri=get_template_uri_from_answers(answers),
        )

    def newer_releases(self) -> list[Version]:
        if self.src_uri and self.version:
            return cached_newer_releases(self.src_uri, self.version.display_str)

        return []


@dataclass(frozen=True)
class AppInfo:
    name: str
    templates: list[TemplateInfo]

    def get_template(self, template_id: TemplateId) -> TemplateInfo | None:
        return next((ti for ti in self.templates if ti.id == template_id), None)


@dataclass(frozen=True)
class ProjectInfo:
    name: str
    template_ids: list[TemplateId]
    apps: list[AppInfo]
    template_answers_raw: dict[Path, Answers | None]
    template_answers_to_id: dict[Path, TemplateId]
    # templates: list[TemplateInfo]
    # template__raw: dict[Tuple[Path, TemplateName], dict[str, str] | None]


def project_info(project: Project, offline: bool = False) -> ProjectInfo:
    all_answers_files = project.dir.glob(".template-*/*.yml")
    # all_answers = map(read_answers_file, all_answers_files)
    # all_answers = {
    #     (f, template_names_from_answers_files([f])[0]): read_answers_file(f)
    #     for f in all_answers_files
    # }
    all_answers = {f: read_answers_file(f) for f in all_answers_files}
    apps = map(partial(project_app_info, project), sorted(project.installed_app_names_possible))
    return ProjectInfo(
        name=project.dir.resolve().name,
        template_ids=[tn.id for tn in project.installed_template_names()],
        apps=list(apps),
        template_answers_raw=all_answers,
        template_answers_to_id={
            f: template_names_from_answers_files([f])[0].id for f, _ in all_answers.items()
        },
    )


def project_app_info(project: Project, app_name: str) -> AppInfo:
    return AppInfo(
        name=app_name,
        templates=[
            project_app_template_info(project, app_name, tn)
            for tn in project.installed_template_names_for_app(app_name)
        ],
    )


def project_app_template_info(
    project: Project, app_name: str, template_name: TemplateName
) -> TemplateInfo:
    return TemplateInfo(
        id=template_name.id,
        name=template_name,
        version=get_template_version_for_existing_app(project, app_name, template_name),
        src_uri=get_template_uri_for_existing_app(project, app_name, template_name),
    )
