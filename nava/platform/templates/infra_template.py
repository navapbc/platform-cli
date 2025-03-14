from pathlib import Path
from typing import Self

from packaging.version import Version

from nava.platform.cli.context import CliContext
from nava.platform.copier_worker import render_template_file
from nava.platform.projects.infra_project import InfraProject
from nava.platform.templates.state import get_template_uri_for_existing_app
from nava.platform.templates.template import Template
from nava.platform.templates.template_name import TemplateName


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

    @classmethod
    def from_existing(
        cls,
        ctx: CliContext,
        project: InfraProject,
    ) -> Self:
        template_uri = get_template_uri_for_existing_app(
            project, app_name="base", template_name=TemplateName.parse("template-infra:base")
        )

        if not template_uri:
            raise ValueError("Can not determine existing `template-infra` source")

        return cls(ctx, template_uri=template_uri)

    def install(
        self,
        project: InfraProject,
        app_names: list[str],
        *,
        version: str | None = None,
        data: dict[str, str] | None = None,
        commit: bool = False,
    ) -> None:
        self.ctx.console.rule("Infra base")
        self.template_base.install(
            project, app_name="base", version=version, data=data, commit=commit
        )

        for app_name in app_names:
            self.ctx.console.rule(f"Infra app: {app_name}")
            self.add_app(project, app_name, version=version, data=data, commit=commit)

    def update(
        self,
        project: InfraProject,
        *,
        version: str | None = None,
        data: dict[str, str] | None = None,
        answers_only: bool = False,
        force: bool = False,
    ) -> None:
        self.ctx.console.rule("Infra base")
        self.update_base(
            project, version=version, data=data, commit=True, answers_only=answers_only, force=force
        )

        for app_name in project.app_names:
            self.ctx.console.rule(f"Infra app: {app_name}")
            self.update_app(
                project,
                app_name,
                version=version,
                data=data,
                commit=True,
                answers_only=answers_only,
                force=force,
            )

    def update_base(
        self,
        project: InfraProject,
        *,
        version: str | None = None,
        data: dict[str, str] | None = None,
        commit: bool = False,
        answers_only: bool = False,
        force: bool = False,
    ) -> None:
        self.template_base.update(
            project,
            app_name="base",
            version=version,
            data=data,
            commit=False,
            answers_only=answers_only,
            force=force,
        )

        # the network file needs re-rendered with the app_names
        self._update_network_config(
            project,
            app_names=project.app_names,
            version=self.template_base.commit,
        )

        if commit:
            self.template_base._commit_action(project, "update", app_name="base")

    def update_app(
        self,
        project: InfraProject,
        app_name: str,
        *,
        version: str | None = None,
        data: dict[str, str] | None = None,
        commit: bool = False,
        answers_only: bool = False,
        force: bool = False,
    ) -> None:
        self.template_app.update(
            project,
            app_name=app_name,
            version=version,
            data=data,
            commit=commit,
            answers_only=answers_only,
            force=force,
        )

    def add_app(
        self,
        project: InfraProject,
        app_name: str,
        *,
        version: str | None = None,
        data: dict[str, str] | None = None,
        existing_apps: list[str] | None = None,
        commit: bool = False,
    ) -> None:
        # Use the template version that the project is currently on, unless
        # an override is provided (mainly during initial install)
        vcs_ref = version if version is not None else project.template_version

        self.template_app.install(
            project, app_name=app_name, version=vcs_ref, data=data, commit=False
        )

        # the network config is added/maintained in the base template, but it is
        # supposed to import every app config module, so update it for the added app
        self._update_network_config(
            project,
            # `project.app_names` should already include the just added app,
            # but in case caching is ever added there, be sure to included the
            # new app name
            app_names=sorted(set((existing_apps or project.app_names) + [app_name])),
            version=vcs_ref,
        )

        if commit:
            self.template_app._commit_action(project, "install", app_name)

    def _update_network_config(
        self, project: InfraProject, app_names: list[str], *, version: str | None = None
    ) -> None:
        data = {"app_names": list(app_names)}
        possible_network_file_paths_rel = [
            "templates/base/infra/networks/main.tf.jinja",
            "infra/networks/main.tf.jinja",
        ]

        self.template_base._checkout_copier_ref(version)

        found_path = None
        for network_file_path_rel in possible_network_file_paths_rel:
            if (self.template_base.copier_template.local_abspath / network_file_path_rel).exists():
                found_path = network_file_path_rel
                break

        if not found_path:
            # TODO: actually an error to not find one?
            return

        render_path = found_path.removeprefix("templates/base/").removesuffix(".jinja")

        self.ctx.console.print(f"Regenerating {render_path} with apps {app_names}")

        # TODO: this might conceivably need to include the base template
        # data/answers at some point
        render_template_file(
            src_path=str(self.template_uri),
            src_file_path=found_path,
            dst_path=project.dir,
            render_path=render_path,
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
