import dataclasses
from pathlib import Path
from typing import Literal, Self

import copier.vcs
from copier.template import Template as CopierTemplate
from packaging.version import Version

from nava.platform.cli.context import CliContext
from nava.platform.copier_worker import run_copy, run_update
from nava.platform.get_template_name_from_uri import get_template_name_from_uri
from nava.platform.projects.project import Project
from nava.platform.templates.errors import MergeConflictsDuringUpdateError
from nava.platform.templates.state import (
    TemplateVersionAnswer,
    answers_file_rel,
    get_template_uri_for_existing_app,
    get_template_version_for_existing_app,
    project_state_dir_rel,
)
from nava.platform.templates.template_name import TemplateId, TemplateName
from nava.platform.types import RelativePath
from nava.platform.util import git, wrappers

BASE_SRC_EXCLUDE = ["*template-only*"]


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
        template_name: TemplateName | TemplateId,
        src_excludes: list[str] | None = None,
    ) -> Self:
        template_uri = get_template_uri_for_existing_app(
            project, app_name=app_name, template_name=TemplateName.parse(template_name)
        )

        if not template_uri:
            raise ValueError(
                f"Can not determine existing template `{template_name}` source for `{app_name}`"
            )

        return cls(
            ctx, template_uri=template_uri, template_name=template_name, src_excludes=src_excludes
        )

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
            src_path=str(self.template_uri),
            dst_path=project.dir,
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
        answers_only: bool = False,
        force: bool = False,
    ) -> None:
        # save the data as provided for later usage
        passed_data = data

        # but this is really the "data" for the template
        data = (data or {}) | {
            "app_name": app_name,
            "template": self.template_name.template_name,
            "template_name_id": self.template_name.id,
        }

        self._check_answers_file(project, app_name)

        existing_version = get_template_version_for_existing_app(
            project, app_name, self.template_name
        )

        if not existing_version:
            raise ValueError(
                "Can not find existing version in answers file (or issue reading the file)"
            )

        # if just updating answers, re-use existing version
        if answers_only:
            # not necessarily true, could just print a message that we are
            # ignoring the provided version, but being strict for now
            if version is not None:
                raise ValueError("Can not specify a version and 'answers only'")

            # not necessarily true either, but should probably be the case
            if not passed_data:
                raise ValueError("If 'answers only', must specify some data")

            version = existing_version.answer_value

        self._checkout_copier_ref(version)

        # if we are already running the version that would be installed, then
        # skip, unless overridden
        bypass_same_version_check = force or (answers_only and passed_data)
        if not bypass_same_version_check and self._is_same_version(existing_version):
            self.ctx.console.print(f"Already up to date ({existing_version.display_str})")
            return

        self.ctx.console.print(f"Current template version: {existing_version.display_str}")

        update_func = self._run_update if not force else self._run_copy

        update_func(
            dst_path=project.dir,
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

    def _check_answers_file(self, project: Project, app_name: str) -> bool:
        answers_file = project.dir / self.answers_file_rel(app_name)
        if not answers_file.exists():
            raise ValueError(f"Answers file does not exist: {answers_file}")

        return True

    def _commit_action(
        self, project: Project, action: Literal["install", "update"], app_name: str
    ) -> None:
        msg = self._commit_action_msg(action, app_name)

        if project.git.is_git():
            self._commit_project(project, msg)
        else:
            from rich.markdown import Markdown

            self.ctx.console.warning.print(
                "Asked to commit, but project is not a git repository. Would have used message:"
            )
            self.ctx.console.print(Markdown(msg))

    def _commit_action_msg(self, action: Literal["install", "update"], app_name: str) -> str:
        # TODO: include hash of answers file in message body? Since if someone
        # is just changing answers the "Updating" message points to the same
        # version? Which is kinda correct.
        #
        # Or different message if just re-rendering with different answers?
        msg_prefix = ""
        if not self.template_name.is_singular_instance(app_name):
            msg_prefix = f"{app_name}: "

        match action:
            case "install":
                msg = f"{msg_prefix}Install `{self.template_name.id}` at version {self.copier_template.version}"
            case "update":
                msg = f"{msg_prefix}Update `{self.template_name.id}` to version {self.copier_template.version}"

        return msg

    # TODO: move to Project?
    def _commit_project(self, project: Project, msg: str) -> None:
        if project.git.has_merge_conflicts():
            raise MergeConflictsDuringUpdateError(commit_msg=msg)

        if project.git.is_clean():
            self.ctx.console.print("Nothing to commit.")
            return

        result = project.git.commit_all(msg)

        if result.returncode != 0:
            self.ctx.console.error.print(result.stderr if result.stderr else result.stdout)
            self.ctx.exit(2)

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

            # TODO: do a fetch origin first?

            # might want to more closely mirror upstream behavior and support submodules:
            # https://github.com/copier-org/copier/blob/2dc1687af389505a708f25b0bc4e37af56179e99/copier/vcs.py#L216
            if ref is None:
                copier.vcs.checkout_latest_tag(copier_git.dir, use_prereleases=False)
            elif ref == "HEAD":
                copier_git.checkout("origin/HEAD")
            else:
                copier_git.checkout(ref)

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

    def _is_same_version(self, version_obj: TemplateVersionAnswer) -> bool:
        commit = self.commit
        if commit is None:
            return False

        return commit == version_obj.answer_value
