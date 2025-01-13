from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path
from typing import Self

import yaml

from nava.platform.cli.context import CliContext
from nava.platform.get_template_name_from_uri import get_template_name_from_uri
from nava.platform.projects.project import Project
from nava.platform.types import RelativePath


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

    def migrate_from_legacy(self, preserve_legacy_file: bool = False, commit: bool = False) -> None:
        if not self.has_legacy_version_file:
            raise ValueError(
                f"No legacy version file found (looking for {self.legacy_version_file_path()})."
            )

        self.ctx.console.print(
            f"Migrating {self.legacy_version_file_path()} to {self.answers_file_rel()}"
        )

        if not self.project_state_dir().exists():
            self.project_state_dir().mkdir()

        template_version = self.legacy_version_file_path().read_text()
        short_version = template_version[:7]
        common_answers = {
            "_commit": short_version,
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
            self.project.git.commit_all(
                f"Migrate {self.legacy_version_file_path()} to {self.answers_file_rel()}"
            )

    def _extra_answers(self: Self) -> dict[str, str]:
        if self.extra_answers:
            return self.extra_answers(self)

        return {}
