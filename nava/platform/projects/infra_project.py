from pathlib import Path

from nava.platform.projects.get_app_names_from_infra_dir import get_app_names_from_infra_dir
from nava.platform.projects.project import Project
from nava.platform.types import RelativePath


class InfraProject(Project):
    @property
    def template_version(self) -> str:
        base_version = self.base_template_version()
        app_versions = [self.app_template_version(app_name) for app_name in self.app_names]
        assert all(app_version == base_version for app_version in app_versions), (
            "Project template base and app version are out of sync"
        )
        return base_version

    def base_template_version(self) -> str:
        return self._get_template_version_from_answers_file(self.base_answers_file()).answer_value

    def app_template_version(self, app_name: str) -> str:
        return self._get_template_version_from_answers_file(
            self.app_answers_file(app_name)
        ).answer_value

    @property
    def app_names_possible(self) -> frozenset[str]:
        return get_app_names_from_infra_dir(self.dir)

    @property
    def app_names(self) -> frozenset[str]:
        app_answer_files = self.dir.glob(".template-infra/app-*.yml")
        return frozenset(
            map(lambda f: f.name.removeprefix("app-").removesuffix(".yml"), app_answer_files)
        )

    def base_answers_file_rel(self) -> RelativePath:
        return self.base_answers_file().relative_to(self.dir)

    def base_answers_file(self) -> Path:
        return self.dir / ".template-infra/base.yml"

    def app_answers_file_rel(self, app_name: str) -> RelativePath:
        return self.app_answers_file(app_name).relative_to(self.dir)

    def app_answers_file(self, app_name: str) -> Path:
        return self.dir / f".template-infra/app-{app_name}.yml"

    #
    # Legacy projects
    #

    @property
    def has_legacy_version_file(self) -> bool:
        return self.legacy_version_file_path().exists()

    def legacy_version_file_path(self) -> Path:
        return self.dir / ".template-version"
