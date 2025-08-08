from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path
from typing import Self

import yaml

from nava.platform.cli.context import CliContext
from nava.platform.get_template_name_from_uri import get_template_name_from_uri
from nava.platform.projects.project import Project
from nava.platform.types import RelativePath
from nava.platform.util.git import GitProject


@dataclass
class MigrateFromLegacyTemplate:
    ctx: CliContext
    project: Project
    origin_template_uri: str
    new_version_answers_file_name: str

    extra_answers: Callable[[Self], dict[str, str]] | None = None

    # these will be derived from above data if not provided
    template_name: str | None = None
    legacy_version_file_name: str | None = None
    new_version_state_dir: str | None = None

    def __post_init__(self) -> None:
        self._template_name: str = self.template_name or get_template_name_from_uri(
            self.origin_template_uri
        )

        if not self._template_name and not (
            self.legacy_version_file_name and self.new_version_state_dir
        ):
            raise ValueError(
                "Unable to determine template name from given parameters. Either set `template_name` or set `legacy_version_file_name` and `new_version_answers_file_name`"
            )

        self._legacy_version_file_name: str = (
            self.legacy_version_file_name or f".{self._template_name}-version"
        )

    @property
    def has_legacy_version_file(self) -> bool:
        return self.legacy_version_file_path().exists()

    def legacy_version_file_path(self) -> Path:
        return self.project.dir / self._legacy_version_file_name

    def project_state_dir_rel(self) -> RelativePath:
        dir = self.new_version_state_dir or f".{self._template_name}"
        return Path(dir)

    def project_state_dir(self) -> Path:
        return self.project.dir / self.project_state_dir_rel()

    def answers_file_rel(self) -> RelativePath:
        return self.project_state_dir_rel() / self.new_version_answers_file_name

    def answers_file(self) -> Path:
        return self.project.dir / self.answers_file_rel()

    def migrate_from_legacy(
        self,
        preserve_legacy_file: bool = False,
        commit: bool = False,
        use_migration_tags: bool = False,
    ) -> None:
        if not self.has_legacy_version_file:
            raise ValueError(
                f"No legacy version file found (looking for {self.legacy_version_file_path()})."
            )

        self.ctx.console.print(
            f"Migrating {self.legacy_version_file_path()} to {self.answers_file_rel()}"
        )

        if not self.project_state_dir().exists():
            self.project_state_dir().mkdir()

        template_version = self.legacy_version_file_path().read_text().strip()

        ref = template_version
        if use_migration_tags:
            with GitProject.clone_if_necessary(self.origin_template_uri) as template_git:
                ref, perfect_match = get_closest_migration_tag(template_git, template_version)

            if not ref:
                raise ValueError("Issue finding suitable migration point")

            if not perfect_match:
                self.ctx.console.warning.print(
                    f"Couldn't find a perfect match to the current commit, using closest tagged version '{ref}' which is slightly older."
                )

        common_answers = {
            "_commit": ref,
            # Copier requires this to be set to a valid template path, and that template git project
            # needs to have _commit as a valid commit hash
            # If _src_path is not set, run_update will raise
            #   UserMessageError("Cannot update because cannot obtain old template references from <answers_file>")
            # If _src_path is set to a folder that does not have _commit as a valid commit hash, then run_update
            # will trigger an error as part of an intenral _check_unsafe method call which will try to
            # check out _commit from _src_path, resulting in the error
            #   error: pathspec '<_commit>' did not match any file(s) known to git
            "_src_path": self.origin_template_uri,
        }

        extra_answers = self._extra_answers()

        answers = common_answers | extra_answers
        self.answers_file().write_text(yaml.dump(answers, default_flow_style=False))

        if not preserve_legacy_file:
            self.ctx.console.print(f"Deleting legacy file ({self.legacy_version_file_path()})")
            self.legacy_version_file_path().unlink()

        if commit and self.project.git.is_git():
            result = self.project.git.commit_all(
                f"Migrate {self.legacy_version_file_path()} to {self.answers_file_rel()}"
            )

            if result.stdout:
                self.ctx.console.print(result.stdout)

    def _extra_answers(self: Self) -> dict[str, str]:
        if self.extra_answers:
            return self.extra_answers(self)

        return {}


def get_closest_tag_before_commit(git: GitProject, commit: str) -> str:
    """Find nearest tag before given commit."""
    from nava.platform.templates.util import get_version

    closest_tag = git.get_closest_tag(commit)
    if not closest_tag:
        raise Exception(f"Can't find closest tag for {commit}")

    closest_version = get_version(closest_tag)
    if not closest_version:
        raise Exception(f"Can't determine version from tag {closest_tag}")

    return "v" + closest_version.base_version


MIGRATION_TAG_PREFIX = "platform-cli-migration/"


def get_closest_migration_tag(git: GitProject, commit: str) -> tuple[str, bool]:
    """Find nearest migration tag before given commit."""
    from nava.platform.templates.util import get_version

    closest_tag = get_closest_tag_before_commit(git, commit)
    migration_tags = git.get_tags("--list", f"{MIGRATION_TAG_PREFIX}*")
    if not migration_tags:
        raise Exception("Can't find migration tags")

    closest_version = get_version(closest_tag)
    if not closest_version:
        raise Exception(f"Can't determine version from {closest_tag}")

    candidates = []

    for migration_tag in migration_tags:
        migration_version = get_version(
            migration_tag.removeprefix(MIGRATION_TAG_PREFIX).removeprefix("v")
        )

        if not migration_version:
            raise Exception(f"Can't determine migration version from {migration_tag}")

        if closest_version == migration_version:
            return migration_tag, True

        if migration_version < closest_version:
            candidates.append(migration_version)

    if candidates:
        closest_migration_version = sorted(candidates, reverse=True)[0]
        return MIGRATION_TAG_PREFIX + "v" + str(closest_migration_version), False

    raise Exception(f"Can't find matching migration version for {closest_tag}")
