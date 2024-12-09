from pathlib import Path

import yaml

from nava.platform.get_app_names_from_infra_dir import get_app_names_from_infra_dir
from nava.platform.util import git

RelativePath = Path


class InfraProject:
    project_dir: Path
    git_project: git.GitProject

    def __init__(self, project_dir: Path):
        self.project_dir = project_dir
        self.git_project = git.GitProject(project_dir)

    @property
    def template_version(self) -> str:
        base_version = self.base_template_version()
        app_versions = [self.app_template_version(app_name) for app_name in self.app_names]
        assert all(
            app_version == base_version for app_version in app_versions
        ), "Project template base and app version are out of sync"
        return base_version

    def base_template_version(self) -> str:
        return self._get_template_version_from_answers_file(self.base_answers_file())

    def app_template_version(self, app_name: str) -> str:
        return self._get_template_version_from_answers_file(self.app_answers_file(app_name))

    @property
    def app_names_possible(self) -> list[str]:
        return get_app_names_from_infra_dir(self.project_dir)

    @property
    def app_names(self) -> list[str]:
        app_answer_files = self.project_dir.glob(".template-infra/app-*.yml")
        return list(
            sorted(
                map(lambda f: f.name.removeprefix("app-").removesuffix(".yml"), app_answer_files)
            )
        )

    def base_answers_file_rel(self) -> RelativePath:
        return self.base_answers_file().relative_to(self.project_dir)

    def base_answers_file(self) -> Path:
        return self.project_dir / ".template-infra/base.yml"

    def app_answers_file_rel(self, app_name: str) -> RelativePath:
        return self.app_answers_file(app_name).relative_to(self.project_dir)

    def app_answers_file(self, app_name: str) -> Path:
        return self.project_dir / f".template-infra/app-{app_name}.yml"

    def _get_template_version_from_answers_file(self, answers_file: Path) -> str:
        answers_file_text = answers_file.read_text()
        answers = yaml.safe_load(answers_file_text)
        return str(answers["_commit"])

    #
    # Legacy projects
    #

    @property
    def has_legacy_version_file(self) -> bool:
        return self.legacy_version_file_path().exists()

    def legacy_version_file_path(self) -> Path:
        return self.project_dir / ".template-version"
