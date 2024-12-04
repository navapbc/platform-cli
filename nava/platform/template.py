import dataclasses
import re
from pathlib import Path
from typing import Self, cast

import dunamai
import yaml
from copier.template import Template as CopierTemplate
from packaging.version import Version

from nava.platform.cli.context import CliContext
from nava.platform.copier_worker import run_copy, run_update
from nava.platform.get_template_name_from_uri import get_template_name_from_uri
from nava.platform.project import Project
from nava.platform.util import git, wrappers

RelativePath = Path


class MergeConflictsDuringUpdateError(Exception):
    pass


BASE_SRC_EXCLUDE = ["*template-only*"]


class Template:
    ctx: CliContext
    template_uri: Path | str
    template_name: str
    src_excludes: list[str]
    copier_template: CopierTemplate

    def __init__(
        self,
        ctx: CliContext,
        template_uri: Path | str,
        src_excludes: list[str] | None = None,
        *,
        template_name: str | None = None,
    ):
        self.ctx = ctx
        self.template_uri = template_uri

        if template_name is None:
            self.template_name = get_template_name_from_uri(template_uri)
        else:
            self.template_name = template_name

        if src_excludes is not None and len(src_excludes) == 0:
            self.src_excludes = []
        else:
            self.src_excludes = BASE_SRC_EXCLUDE + (src_excludes or [])

        self.copier_template = CopierTemplate(url=str(template_uri), ref="HEAD")

        self._run_copy = wrappers.log_call(run_copy, logger=ctx.log.info)
        self._run_update = wrappers.log_call(run_update, logger=ctx.log.info)

    @classmethod
    def from_existing(
        cls,
        ctx: CliContext,
        project: Project,
        app_name: str,
        template_name: str,
        src_excludes: list[str] | None = None,
    ) -> Self:
        template_uri = get_template_uri_for_existing_app(
            project, app_name=app_name, template_name=template_name
        )

        if not template_uri:
            raise ValueError(
                f"Can not determine existing template `{template_name}` source for `{app_name}`"
            )

        return cls(ctx, template_uri=template_uri, src_excludes=src_excludes)

    def install(
        self,
        project: Project,
        app_name: str,
        *,
        version: str | None = None,
        data: dict[str, str] | None = None,
    ) -> None:
        data = (data or {}) | {"app_name": app_name}

        self._checkout_copier_ref(version)

        self._run_copy(
            str(self.template_uri),
            project.dir,
            answers_file=self.answers_file_rel(app_name),
            data=data,
            src_exclude=self.src_excludes,
            vcs_ref=version,
        )

    def update(
        self,
        project: Project,
        app_name: str,
        *,
        version: str | None = None,
        data: dict[str, str] | None = None,
        commit: bool = False,
    ) -> None:
        data = (data or {}) | {"app_name": app_name}

        self._checkout_copier_ref(version)

        existing_version = get_template_version_for_existing_app(
            project, app_name, self.template_name
        )

        if (
            isinstance(self.version, Version)
            and isinstance(existing_version, Version)
            and self.version == existing_version
        ):
            self.ctx.console.print(f"Already up to date ({existing_version})")
            return

        self.ctx.console.print(f"Current template version: {existing_version}")

        self._run_update(
            project.dir,
            # note `src_path` currently has no effect on updates, the path from
            # answers file is used
            #
            # https://github.com/navapbc/platform-cli/issues/5
            src_path=str(self.template_uri),
            data=data,
            answers_file=self.answers_file_rel(app_name),
            src_exclude=self.src_excludes,
            overwrite=True,
            skip_answered=True,
            vcs_ref=version,
        )

        if commit:
            self._commit_project(
                project,
                f"Update app `{app_name}` to version {self.copier_template.version}",
            )

    def project_state_dir_rel(self) -> RelativePath:
        return project_state_dir_rel(self.template_name)

    def answers_file_rel(self, app_name: str) -> RelativePath:
        return answers_file_rel(template_name=self.template_name, app_name=app_name)

    def _commit_project(self, project: Project, msg: str) -> None:
        if project.git.has_merge_conflicts():
            raise MergeConflictsDuringUpdateError()

        result = project.git.commit_all(msg)

        if result.stdout:
            self.ctx.console.print(result.stdout)

    def _checkout_copier_ref(self, ref: str | None = None) -> None:
        if self.copier_template.vcs == "git" and ref:
            prev_template = self.copier_template

            # CopierTemplate caches a lot of info on first access, most of which
            # is dependant on what version is requested, so create a new copy
            # that will pickup any changes, but point it at the existing temp
            # checkout so it doesn't have to re-fetch remote repos
            self.copier_template = dataclasses.replace(self.copier_template, ref=ref)
            self.copier_template.local_abspath = prev_template.local_abspath

            copier_git = git.GitProject(self.copier_template.local_abspath)
            copier_git.checkout(ref)

        return None

    @property
    def version(self) -> Version | None:
        return self.copier_template.version

    @property
    def commit_hash(self) -> str | None:
        return self.copier_template.commit_hash


def project_state_dir_rel(template_name: str) -> RelativePath:
    return Path(f".{template_name}")


def answers_file_rel(template_name: str, app_name: str) -> RelativePath:
    return project_state_dir_rel(template_name) / (app_name + ".yml")


def get_template_uri_for_existing_app(
    project: Project, app_name: str, template_name: str
) -> str | None:
    answers = get_answers(project, app_name, template_name)

    return get_template_uri_from_answers(answers)


def get_template_uri_from_answers(answers: dict[str, str] | None) -> str | None:
    if not answers:
        return None

    template_uri = answers.get("_src_path", None)

    return template_uri


def get_template_version_for_existing_app(
    project: Project, app_name: str, template_name: str
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


def get_answers(project: Project, app_name: str, template_name: str) -> dict[str, str] | None:
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
