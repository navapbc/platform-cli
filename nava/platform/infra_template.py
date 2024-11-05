import functools
import operator
from pathlib import Path

import copier

from nava.platform.project import Project
from nava.platform.util import git, wrappers
from nava.platform.util.files.inode import DirNode, Inode


class MergeConflictsDuringUpdateError(Exception):
    pass


class InfraTemplate:
    template_dir: Path
    git_project: git.GitProject

    _base_excludes: list[str]
    _app_excludes: list[str]

    def __init__(self, template_dir: Path):
        git_project = git.GitProject.from_existing(template_dir)

        if git_project is None:
            raise ValueError("Infra template must be a git working directory")

        self.template_dir = template_dir
        self.git_project = git_project

        self._compute_excludes()
        self._run_copy = wrappers.print_call(copier.run_copy)
        self._run_update = wrappers.print_call(copier.run_update)

    def install(
        self,
        project: Project,
        app_names: list[str],
        *,
        version: str | None = None,
        data: dict[str, str] | None = None,
    ) -> None:
        data = {"app_name": "template-only"} | (data or {})
        self._run_copy(
            str(self.template_dir),
            project.project_dir,
            answers_file=self._base_answers_file(),
            data=data,
            exclude=self._base_excludes,
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
        data = {"app_name": "template-only"} | (data or {})
        self._run_update(
            project.project_dir,
            src_path=str(self.template_dir),
            data=data,
            answers_file=project.base_answers_file(),
            exclude=self._base_excludes,
            overwrite=True,
            skip_answered=True,
            vcs_ref=version,
        )

    def update_app(
        self,
        project: Project,
        app_name: str,
        *,
        version: str | None = None,
        data: dict[str, str] | None = None,
    ) -> None:
        data = {"app_name": app_name} | (data or {})
        self._run_update(
            project.project_dir,
            data=data,
            answers_file=project.app_answers_file(app_name),
            exclude=list(self._app_excludes),
            overwrite=True,
            skip_answered=True,
            vcs_ref=version,
        )

    def add_app(self, project: Project, app_name: str, *, version: str | None = None, data: dict[str, str] | None = None) -> None:
        data = {"app_name": app_name} | (data or {})
        self._run_copy(
            str(self.template_dir),
            project.project_dir,
            answers_file=self._app_answers_file(app_name),
            data=data,
            exclude=list(self._app_excludes),
            # Use the template version that the project is currently on, unless
            # an override is provided (mainly during initial install)
            vcs_ref=version if version is not None else project.template_version,
        )

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
        node = DirNode.build_tree_from_paths(self.git_project.get_tracked_files())
        app_includes, app_excludes = self._compute_app_includes_excludes(node)
        global_excludes = ["*template-only*"]
        self._base_excludes = global_excludes + list(app_includes)
        self._app_excludes = global_excludes + list(app_excludes)

    def _base_answers_file(self) -> str:
        return "base.yml"

    def _app_answers_file(self, app_name: str) -> str:
        return f"app-{app_name}.yml"

    def _compute_app_includes_excludes(self, node: Inode) -> tuple[set[str], set[str]]:
        app_includes, app_excludes = self._compute_app_includes_excludes_helper(node)
        app_excludes.difference_update([".template-infra", "."])
        return app_includes, app_excludes

    def _compute_app_includes_excludes_helper(self, node: Inode) -> tuple[set[str], set[str]]:
        relpath_str = str(node.path)

        if "{{app_name}}" in relpath_str:
            return (set([relpath_str]), set())

        if "template-only" in relpath_str:
            return (set(), set())

        if node.is_file():
            return (set(), set([relpath_str]))

        assert isinstance(node, DirNode)
        children = node.children.values()
        if len(children) == 0:
            return (set(), set())

        subresults = list(self._compute_app_includes_excludes_helper(child) for child in children)

        subincludes, subexcludes = zip(*subresults)
        includes: set[str] = functools.reduce(operator.or_, subincludes, set())
        excludes: set[str] = functools.reduce(operator.or_, subexcludes, set())

        if len(includes) == 0:
            return (set(), set([relpath_str]))

        return (includes, excludes)
