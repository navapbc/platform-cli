import re
from pathlib import Path
from typing import cast

import dunamai
import yaml
from packaging.version import Version

from nava.platform.projects.project import Project
from nava.platform.templates.template_name import TemplateName
from nava.platform.types import RelativePath


def project_state_dir_rel(template_name: TemplateName) -> RelativePath:
    return Path(f".{template_name.repo_name}")


def answers_file_rel(template_name: TemplateName, app_name: str) -> RelativePath:
    if template_name.is_singular_instance(app_name):
        answers_file_name = app_name
    else:
        answers_file_name = template_name.answers_file_prefix + app_name

    return project_state_dir_rel(template_name) / (answers_file_name + ".yml")


def get_template_uri_for_existing_app(
    project: Project, app_name: str, template_name: TemplateName
) -> str | None:
    answers = get_answers(project, app_name, template_name)

    return get_template_uri_from_answers(answers)


def get_template_uri_from_answers(answers: dict[str, str] | None) -> str | None:
    if not answers:
        return None

    template_uri = answers.get("_src_path", None)

    return template_uri


def get_template_version_for_existing_app(
    project: Project, app_name: str, template_name: TemplateName
) -> Version | str | None:
    answers = get_answers(project, app_name, template_name)

    return get_template_version_from_answers(answers)


def get_template_version_from_answers(answers: dict[str, str] | None) -> Version | str | None:
    if not answers:
        return None

    template_version = answers.get("_commit", None)

    if template_version:
        try:
            return get_version_from_git_describe(template_version)
        except ValueError:
            # TODO: log? or return a tuple of (raw, parsed) value of type `(str, Version | None) | None`?
            pass

    return template_version


def get_answers(
    project: Project, app_name: str, template_name: TemplateName
) -> dict[str, str] | None:
    answers_file = project.dir / answers_file_rel(template_name, app_name)

    if not answers_file.exists():
        return None

    answers = yaml.safe_load(answers_file.read_text())

    return cast(dict[str, str], answers)


def get_version_from_git_describe(v: str) -> Version:
    if not re.match(r"^.+-\d+-g\w+$", v):
        raise ValueError(f"Not a valid git describe: {v}")

    base, count, git_hash = v.rsplit("-", 2)

    dunamai_version = dunamai.Version(
        base=base.removeprefix("v"), distance=int(count), commit=git_hash.removeprefix("g")
    )

    # We could just:
    #
    #   Version(f"{base}.post{count}+{git_hash}")
    #
    # but dunamai adds a default `.dev0` in there during the serialization
    # logic, which is what upstream uses[1], so match upstream's version logic
    # for correct comparisions against git templates (i.e., calls to
    # `template.version`).
    #
    # [1] https://github.com/copier-org/copier/blob/63fec9a500d9319f332b489b6d918ecb2e0598e3/copier/template.py#L584-L588
    return Version(dunamai_version.serialize(style=dunamai.Style.Pep440))
