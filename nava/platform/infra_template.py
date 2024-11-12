from pathlib import Path

from nava.platform.copier_worker import render_template_file, run_copy, run_update
from nava.platform.project import Project
from nava.platform.util import git, wrappers


class MergeConflictsDuringUpdateError(Exception):
    pass


class InfraTemplate:
    template_dir: Path
    git_project: git.GitProject

    _base_src_excludes: list[str]
    _app_src_excludes: list[str]

    def __init__(self, template_dir: Path):
        git_project = git.GitProject.from_existing(template_dir)

        if git_project is None:
            raise ValueError("Infra template must be a git working directory")

        self.template_dir = template_dir
        self.git_project = git_project

        self._compute_excludes()
        self._run_copy = wrappers.print_call(run_copy)
        self._run_update = wrappers.print_call(run_update)

    def install(
        self,
        project: Project,
        app_names: list[str],
        *,
        version: str | None = None,
        data: dict[str, str] | None = None,
    ) -> None:
        base_data = (data or {}) | {"template": "base"}
        self._run_copy(
            str(self.template_dir),
            project.project_dir,
            answers_file=self._base_answers_file(),
            data=base_data,
            src_exclude=self._base_src_excludes,
            vcs_ref=version,
        )

        for app_name in app_names:
            self.add_app(project, app_name, version=version, data=data)

    def update(
        self, project: Project, *, version: str | None = None, data: dict[str, str] | None = None
    ) -> None:
        self.update_base(project, version=version, data=data)

        if project.git_project.has_merge_conflicts():
            raise MergeConflictsDuringUpdateError()

        project.git_project.commit_all(f"Update base to version {project.base_template_version()}")

        for app_name in project.app_names:
            self.update_app(project, app_name, version=version, data=data)

            if project.git_project.has_merge_conflicts():
                raise MergeConflictsDuringUpdateError()

            project.git_project.commit_all(
                f"Update app {app_name} to version {project.app_template_version(app_name)}"
            )

    def update_base(
        self, project: Project, *, version: str | None = None, data: dict[str, str] | None = None
    ) -> None:
        data = (data or {}) | {"template": "base"}
        self._run_update(
            project.project_dir,
            # note `src_path` currently has no effect on updates, the path from
            # answers file is used
            #
            # https://github.com/navapbc/platform-cli/issues/5
            src_path=str(self.template_dir),
            data=data,
            answers_file=project.base_answers_file(),
            src_exclude=self._base_src_excludes,
            overwrite=True,
            skip_answered=True,
            vcs_ref=version,
        )

        # the network file needs re-rendered with the app_names
        self._update_network_config(
            project,
            app_names=project.app_names,
            version=version,
        )

    def update_app(
        self,
        project: Project,
        app_name: str,
        *,
        version: str | None = None,
        data: dict[str, str] | None = None,
    ) -> None:
        data = (data or {}) | {"app_name": app_name, "template": "app"}
        self._run_update(
            project.project_dir,
            # note `src_path` currently has no effect on updates, the path from
            # answers file is used
            #
            # https://github.com/navapbc/platform-cli/issues/5
            src_path=str(self.template_dir),
            data=data,
            answers_file=project.app_answers_file(app_name),
            src_exclude=self._app_src_excludes,
            overwrite=True,
            skip_answered=True,
            vcs_ref=version,
        )

    def add_app(
        self,
        project: Project,
        app_name: str,
        *,
        version: str | None = None,
        data: dict[str, str] | None = None,
        existing_apps: list[str] | None = None,
    ) -> None:
        data = (data or {}) | {"app_name": app_name, "template": "app"}
        self._run_copy(
            str(self.template_dir),
            project.project_dir,
            answers_file=self._app_answers_file(app_name),
            data=data,
            src_exclude=self._app_src_excludes,
            # Use the template version that the project is currently on, unless
            # an override is provided (mainly during initial install)
            vcs_ref=version if version is not None else project.template_version,
        )

        # the network config is added/maintained in the base template, but it is
        # supposed to import every app config module, so update it for the added app
        self._update_network_config(
            project,
            # `project.app_names` should already include the just added app,
            # but in case caching is ever added there, be sure to included the
            # new app name
            app_names=sorted(set((existing_apps or project.app_names) + [app_name])),
            version=version,
        )

    def _update_network_config(
        self, project: Project, app_names: list[str], *, version: str | None = None
    ) -> None:
        data = {"app_names": list(app_names)}
        path = "infra/networks/main.tf.jinja"

        if not (self.template_dir / path).exists():
            return

        print(f"Regenerating {path.removesuffix('.jinja')}")

        # TODO: this might conceivably need to include the base template
        # data/answers at some point
        render_template_file(
            src_path=str(self.template_dir),
            src_file_path=path,
            dst_path=project.project_dir,
            data=data,
            # Use the template version that the project is currently on, unless
            # an override is provided (mainly during initial install)
            vcs_ref=version if version is not None else project.template_version,
            overwrite=True,
            # this will basically always show a conflict for the update, so
            # mimic upstream behavior and be quiet about it
            quiet=True,
        )

        # TODO: run `terraform fmt` after? Currently left for folks to do
        # manually.

    @property
    def version(self) -> str:
        return self.git_project.get_commit_hash_for_head()

    @version.setter
    def version(self, version: str) -> None:
        self.git_project.tag(version)

    @property
    def short_version(self) -> str:
        return self.version[:7]

    def _compute_excludes(self) -> None:
        global_src_excludes = ["*template-only*"]
        self._base_src_excludes = global_src_excludes + ["*{{app_name}}*"]
        self._app_src_excludes = global_src_excludes + [
            "*",
            "!*{{app_name}}*",
            "!/.template-infra/",
        ]

    def _base_answers_file(self) -> str:
        return "base.yml"

    def _app_answers_file(self, app_name: str) -> str:
        return f"app-{app_name}.yml"
