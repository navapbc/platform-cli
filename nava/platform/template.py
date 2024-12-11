import dataclasses
import re
from pathlib import Path
from typing import ClassVar, Literal, Self, cast

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

BASE_SRC_EXCLUDE = ["*template-only*"]


class MergeConflictsDuringUpdateError(Exception):
    pass


@dataclasses.dataclass
class TemplateName:
    """Handling the "name" of "a" "template".

    There are a number of conventions the tooling follows based on the "name" of
    a template. Most of the time a single repo == a single template and the
    "name" of the template is just the name of the repo. Easy.

    Some times, notably ``navapbc/template-infra``, there are multiple
    "templates" (a distinct collection of templated files that are handled
    together) in the same repo, though the repo itself is also referred to as a
    "template" in conversation. These multiple templates are not necessarily
    hierarchical, though generally related/interdependent. So both when
    outputting info to a user and for internal operations at different times we
    need refer to just the repo name (e.g., for state directory location), just
    the template name (e.g., for state file location, context variables), and
    both (e.g., to uniquely identify the template in some user messaging).

    This class papers over those differences.
    """

    SEPARATOR: ClassVar[str] = ":"

    repo_name: str
    template_name: str

    @classmethod
    def parse(cls, s: Self | str) -> Self:
        if isinstance(s, cls):
            return s

        return cls.from_str(cast(str, s))

    @classmethod
    def from_str(cls, s: str) -> Self:
        parts = s.split(cls.SEPARATOR)

        if len(parts) == 1:
            return cls(repo_name=parts[0], template_name=parts[0])
        else:
            return cls(repo_name=parts[0], template_name=cls.SEPARATOR.join(parts[1:]))

    @property
    def id(self) -> str:
        if self.repo_name == self.template_name:
            return self.repo_name

        return self.SEPARATOR.join([self.repo_name, self.template_name])

    @property
    def answers_file_prefix(self) -> str:
        if self.repo_name == self.template_name:
            return ""

        return self.template_name + "-"

    def is_singular_instance(self, app_name: str) -> bool:
        """Check if this app_name implies the template only exists once for project.

        Effectively, when the app name is the same name as the template itself,
        assume the template is something which only has one instance in a given
        project.
        """
        return app_name == self.template_name


class Template:
    """A collection of templated files and things to do with them.

    Represents both the current state of a template (akin to ``copier``'s
    ``Template``) and some operational logic against it (akin to ``copier``'s
    ``Worker``).
    """

    ctx: CliContext
    template_uri: Path | str
    template_name: TemplateName
    src_excludes: list[str]
    copier_template: CopierTemplate
    ref: str | None

    def __init__(
        self,
        ctx: CliContext,
        template_uri: Path | str,
        src_excludes: list[str] | None = None,
        *,
        template_name: TemplateName | str | None = None,
        ref: str | None = None,
    ):
        self.ctx = ctx
        self.template_uri = template_uri

        if template_name is None:
            self.template_name = TemplateName.parse(get_template_name_from_uri(template_uri))
        else:
            self.template_name = TemplateName.parse(template_name)

        if src_excludes is not None and len(src_excludes) == 0:
            self.src_excludes = []
        else:
            self.src_excludes = BASE_SRC_EXCLUDE + (src_excludes or [])

        self.copier_template = CopierTemplate(url=str(template_uri), ref=ref)

        self._run_copy = wrappers.log_call(run_copy, logger=ctx.log.info)
        self._run_update = wrappers.log_call(run_update, logger=ctx.log.info)

    @classmethod
    def from_existing(
        cls,
        ctx: CliContext,
        project: Project,
        app_name: str,
        template_name: TemplateName | str,
        src_excludes: list[str] | None = None,
    ) -> Self:
        template_uri = get_template_uri_for_existing_app(
            project, app_name=app_name, template_name=TemplateName.parse(template_name)
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
        commit: bool = False,
    ) -> None:
        data = (data or {}) | {
            "app_name": app_name,
            "template": self.template_name.template_name,
            "template_name_id": self.template_name.id,
        }

        self._checkout_copier_ref(version)

        self._run_copy(
            str(self.template_uri),
            project.dir,
            answers_file=self.answers_file_rel(app_name),
            data=data,
            src_exclude=self.src_excludes,
            vcs_ref=version,
        )

        if commit:
            self._commit_action(project, "install", app_name)

    def update(
        self,
        project: Project,
        app_name: str,
        *,
        version: str | None = None,
        data: dict[str, str] | None = None,
        commit: bool = False,
    ) -> None:
        data = (data or {}) | {
            "app_name": app_name,
            "template": self.template_name.template_name,
            "template_name_id": self.template_name.id,
        }

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
            self._commit_action(project, "update", app_name)

    def project_state_dir_rel(self) -> RelativePath:
        return project_state_dir_rel(self.template_name)

    def answers_file_rel(self, app_name: str) -> RelativePath:
        return answers_file_rel(template_name=self.template_name, app_name=app_name)

    def _commit_action(
        self, project: Project, action: Literal["install", "update"], app_name: str
    ) -> None:
        msg = self._commit_action_msg(action, app_name)

        if not project.git.is_git():
            from rich.markdown import Markdown

            self.ctx.console.warning.print(
                "Asked to commit, but project is not a git repository. Would have used message:"
            )
            self.ctx.console.print(Markdown(msg))
            return

        self._commit_project(project, msg)

    def _commit_action_msg(self, action: Literal["install", "update"], app_name: str) -> str:
        if self.template_name.is_singular_instance(app_name):
            msg_app_identifier = f"`{self.template_name.id}`"
        else:
            msg_app_identifier = f"`{self.template_name.id}` `{app_name}`"

        match action:
            case "install":
                msg = f"Install {msg_app_identifier} version {self.copier_template.version}"
            case "update":
                msg = f"Update {msg_app_identifier} to version {self.copier_template.version}"

        return msg

    # TODO: move to Project?
    def _commit_project(self, project: Project, msg: str) -> None:
        if project.git.has_merge_conflicts():
            raise MergeConflictsDuringUpdateError()

        result = project.git.commit_all(msg)

        if result.stdout:
            self.ctx.console.print(result.stdout)

    def _checkout_copier_ref(self, ref: str | None = None) -> None:
        # only update if the ref is different from existing, this may have some
        # edge cases if the underlying template repo has changes the caller was
        # intending to be picked up
        if self.copier_template.ref == ref:
            return None

        if self.copier_template.vcs != "git":
            return None

        prev_template = self.copier_template

        # CopierTemplate caches a lot of info on first access, most of which is
        # dependant on what version is requested, so create a new copy that will
        # pickup any changes
        self.copier_template = dataclasses.replace(self.copier_template, ref=ref)

        # but if there was an existing checkout, point the updated copy at the
        # existing temp checkout so it doesn't have to re-fetch remote repos
        if prev_template._temp_clone is not None:
            self.copier_template.__dict__["local_abspath"] = prev_template.local_abspath

            copier_git = git.GitProject(self.copier_template.local_abspath)
            # might want to more closely mirror upstream behavior and support submodules:
            # https://github.com/copier-org/copier/blob/2dc1687af389505a708f25b0bc4e37af56179e99/copier/vcs.py#L216
            copier_git.checkout(ref or "HEAD")
            # remove any dirty changes copier might have previously committed as
            # draft if not using HEAD
            if ref not in (None, "HEAD"):
                # we could just
                #
                #   copier_git.reset("--hard", f"origin/{ref}")
                #
                # but that's only if `ref` is a tag/branch name and not
                # something else and maybe safer to be a bit more targeted, so
                # we'll look for if the latest commit is the expected "dirty
                # commit" and remove it
                import copier.vcs

                # x09 is the hex code for tab
                last_commit_parts = copier_git.log("-1", "--pretty=%an%x09%ae%x09%s").stdout
                [author_name, author_email, commit_subject] = map(
                    lambda s: s.strip(), last_commit_parts.split("\t")
                )

                if (
                    author_name == copier.vcs.GIT_USER_NAME
                    and author_email == copier.vcs.GIT_USER_EMAIL
                    and commit_subject == "Copier automated commit for draft changes"
                ):
                    copier_git.reset("--hard", "HEAD~1")
        return None

    @property
    def version(self) -> Version | None:
        return self.copier_template.version

    @property
    def commit(self) -> str | None:
        """The value that will be saved in the answers file."""
        return self.copier_template.commit

    @property
    def commit_hash(self) -> str | None:
        return self.copier_template.commit_hash


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
