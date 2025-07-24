import contextlib
import re
from collections import defaultdict
from collections.abc import Iterable
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING, Any, NewType

import dunamai
import yaml
from packaging.version import Version

from nava.platform.templates.template_name import TemplateName
from nava.platform.types import RelativePath

if TYPE_CHECKING:
    from nava.platform.projects.project import Project


Answers = NewType("Answers", dict[str, str])


def project_state_dir_rel(template_name: TemplateName) -> RelativePath:
    return Path(f".{template_name.repo_name}")


def template_repo_name_from_project_state_dir(template_state_dir: Path) -> str:
    return template_state_dir.name.removeprefix(".")


def template_repo_name_from_answers_file(answers_file: Path) -> str:
    return template_repo_name_from_project_state_dir(answers_file.parent)


def template_names_from_project_state_dir(template_state_dir: Path) -> list[TemplateName]:
    """A single "template" state dir/repo may contain multiple "templates", check for all the names."""
    template_answers_files = filter(lambda f: f.is_file(), template_state_dir.glob("*.yml"))
    return template_names_from_answers_files(template_answers_files)


def template_names_from_answers_files(template_answers_files: Iterable[Path]) -> list[TemplateName]:
    mapping = _get_repo_to_template_from_answers(template_answers_files)

    ret = []
    for repo_name, sub_template_names in mapping.items():
        if sub_template_names:
            ret.extend(
                [
                    TemplateName(repo_name=repo_name, template_name=sub_template_name)
                    for sub_template_name in sub_template_names
                    if sub_template_name
                ]
            )
        else:
            ret.append(TemplateName.parse(repo_name))

    return ret


def _get_repo_to_template_from_answers(
    template_answer_files: Iterable[Path],
) -> dict[str, list[str]]:
    template_repo_to_maybe_subtemplate_pairs = map(
        lambda f: (
            template_repo_name_from_answers_file(f),
            get_sub_template_name_from_answers(read_answers_file(f)),
        ),
        template_answer_files,
    )

    ret: dict[str, list[str]] = defaultdict(list)

    for k, v in template_repo_to_maybe_subtemplate_pairs:
        # always access the key, so defaultdict ensures there's a value for all
        # our pairs, even if there are no subtemplate values to add
        subtemplate_names = ret[k]

        if v:
            subtemplate_names.append(v)

    return ret


def answers_file_rel(template_name: TemplateName, app_name: str) -> RelativePath:
    if template_name.is_singular_instance(app_name):
        answers_file_name = app_name
    else:
        answers_file_name = template_name.answers_file_prefix + app_name

    return project_state_dir_rel(template_name) / (answers_file_name + ".yml")


def get_template_uri_for_existing_app(
    project: "Project", app_name: str, template_name: TemplateName
) -> str | None:
    answers = get_answers(project, app_name, template_name)

    return get_template_uri_from_answers(answers)


def get_template_uri_from_answers(answers: Answers | None) -> str | None:
    if not answers:
        return None

    template_uri = answers.get("_src_path", None)

    return template_uri


def get_sub_template_name_from_answers(answers: Answers | None) -> str | None:
    if not answers:
        return None

    # the specific key is template-dependant/controlled by the template's
    # copier.yml file, but convention so far is to store the name under
    # `template`
    template_name = answers.get("template", None)

    return template_name


@dataclass(frozen=True)
class TemplateVersionAnswer:
    answer_value: str
    """What is saved in the answers file as `_commit` (it's the output from a `git describe`)"""
    version: Version | None
    """A PEP 440 object corresponding to `answer_value` (if possible)"""

    @property
    def display_str(self) -> str:
        """Public facing representation of the version.

        `copier.Template.version`/the PEP 440 value is what Copier uses in its
        messaging ("Updating to template version <foo>"), so match that if
        possible, otherwise fall back to raw answer value.
        """
        if self.version:
            return str(self.version)

        return self.answer_value


def get_template_version_for_existing_app(
    project: "Project", app_name: str, template_name: TemplateName
) -> TemplateVersionAnswer | None:
    answers = get_answers(project, app_name, template_name)

    return get_template_version_from_answers(answers)


def get_template_version_from_answers_file(answers_file: Path) -> TemplateVersionAnswer | None:
    answers = read_answers_file(answers_file)

    return get_template_version_from_answers(answers)


def get_template_version_from_answers(
    answers: Answers | None,
) -> TemplateVersionAnswer | None:
    if not answers:
        return None

    template_version = answers.get("_commit", None)
    parsed_version = None

    if not template_version:
        return None

    with contextlib.suppress(ValueError):
        parsed_version = get_version_from_git_describe(template_version)

    return TemplateVersionAnswer(answer_value=template_version, version=parsed_version)


def get_answers(project: "Project", app_name: str, template_name: TemplateName) -> Answers | None:
    answers_file = project.dir / answers_file_rel(template_name, app_name)

    if not answers_file.exists():
        return None

    return read_answers_file(answers_file)


def read_answers_file(answers_file: Path) -> Answers | None:
    answers = read_answers_file_raw_yaml(answers_file)

    # in real operation, the answers file should always be a dictionary, but in
    # testing or other odd cases, perhaps it won't be, so indicate that
    if not isinstance(answers, dict):
        return None

    return Answers(answers)


def read_answers_file_raw_yaml(answers_file: Path) -> Any:
    return yaml.safe_load(answers_file.read_text())


def get_version_from_git_describe(v: str) -> Version:
    """Parse the string as a `Version`.

    This is an imperfect, but minimally-complicated effort to match
    `copier.Template.version` behavior. It mostly diverges from the upstream
    value when version string is not a valid PEP 440 identifier (e.g., the
    template uses a date stamp as it's version), as we can't fully match
    Copier's behavior without access to the full git history, since upstream
    discards all tags that are not PEP 440 compliant before generating its value
    (and if there are no PEP 440 compliant tags at all in the template, will
    spit out something like: `0.0.0.post<count of commits since beginning of
    project>.dev0+<current commit short hash>`).
    """
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
