from pathlib import Path

from packaging.version import Version

from nava.platform.cli.context import CliContext
from nava.platform.copier_worker import render_template_file
from nava.platform.infra_project import InfraProject
from nava.platform.template import Template


class MergeConflictsDuringUpdateError(Exception):
    pass


class InfraTemplate:
    ctx: CliContext
    template_uri: Path | str

    def __init__(self, ctx: CliContext, template_uri: Path | str, *, ref: str | None = None):
        self.ctx = ctx
        self.template_uri = template_uri

        self.template_base = Template(
            ctx,
            template_uri=template_uri,
            src_excludes=["*{{app_name}}*"],
            template_name="template-infra:base",
            ref=ref,
        )

        self.template_app = Template(
            ctx,
            template_uri=template_uri,
            src_excludes=[
                "*",
                "!*{{app_name}}*",
                "!/.template-infra/",
            ],
            template_name="template-infra:app",
            ref=ref,
        )

    def install(
        self,
        project: InfraProject,
        app_names: list[str],
        *,
        version: str | None = None,
        data: dict[str, str] | None = None,
    ) -> None:
        self.ctx.console.rule("Infra base")
        # TODO: the data in template_base will include `app_name` now, check it
        # doesn't get saved to answers file
        self.template_base.install(project, app_name="base", version=version, data=data)

        for app_name in app_names:
            self.ctx.console.rule(f"Infra app: {app_name}")
            self.add_app(project, app_name, version=version, data=data)

    def update(
        self,
        project: InfraProject,
        *,
        version: str | None = None,
        data: dict[str, str] | None = None,
    ) -> None:
        self.ctx.console.rule("Infra base")
        self.update_base(project, version=version, data=data, commit=True)

        for app_name in project.app_names:
            self.ctx.console.rule(f"Infra app: {app_name}")
            self.update_app(project, app_name, version=version, data=data, commit=True)

    def update_base(
        self,
        project: InfraProject,
        *,
        version: str | None = None,
        data: dict[str, str] | None = None,
        commit: bool = False,
    ) -> None:
        self.template_base.update(
            project, app_name="base", version=version, data=data, commit=False
        )

        # the network file needs re-rendered with the app_names
        self._update_network_config(
            project,
            app_names=project.app_names,
            version=version,
        )

        if commit:
            self._commit_project(
                project,
                f"Update infra-base to version {self.template_base.version}",
            )

    def update_app(
        self,
        project: InfraProject,
        app_name: str,
        *,
        version: str | None = None,
        data: dict[str, str] | None = None,
        commit: bool = False,
    ) -> None:
        self.template_app.update(
            project, app_name=app_name, version=version, data=data, commit=False
        )

        if commit:
            self._commit_project(
                project,
                f"Update infra-app `{app_name}` to version {self.template_app.version}",
            )

    def _commit_project(self, project: InfraProject, msg: str) -> None:
        if project.git.has_merge_conflicts():
            raise MergeConflictsDuringUpdateError()

        result = project.git.commit_all(msg)

        if result.stdout:
            self.ctx.console.print(result.stdout)

    def add_app(
        self,
        project: InfraProject,
        app_name: str,
        *,
        version: str | None = None,
        data: dict[str, str] | None = None,
        existing_apps: list[str] | None = None,
    ) -> None:
        # Use the template version that the project is currently on, unless
        # an override is provided (mainly during initial install)
        vcs_ref = version if version is not None else project.template_version

        self.template_app.install(project, app_name=app_name, version=vcs_ref, data=data)

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
        self, project: InfraProject, app_names: list[str], *, version: str | None = None
    ) -> None:
        data = {"app_names": list(app_names)}
        path = "infra/networks/main.tf.jinja"

        if not (self.template_base.copier_template.local_abspath / path).exists():
            return

        self.ctx.console.print(f"Regenerating {path.removesuffix('.jinja')}")

        # TODO: this might conceivably need to include the base template
        # data/answers at some point
        render_template_file(
            src_path=str(self.template_uri),
            src_file_path=path,
            dst_path=project.dir,
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
    def version(self) -> Version | None:
        return self.template_base.version

    @property
    def commit(self) -> str | None:
        return self.template_base.commit

    @property
    def commit_hash(self) -> str | None:
        return self.template_base.commit_hash

    @property
    def short_commit_hash(self) -> str | None:
        return self.commit_hash[:7] if self.commit_hash else None
