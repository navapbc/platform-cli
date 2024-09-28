import functools
import itertools
import operator
import os
from pathlib import Path
import copier


def add_app(template_dir: str | Path, project_dir: str, app_name: str):
    answers_file = f".template-infra-app-{app_name}.yml"
    data = {"app_name": app_name}

    _, app_excludes = compute_app_includes_excludes(Path(template_dir))

    copier.run_copy(
        str(template_dir),
        project_dir,
        answers_file=answers_file,
        data=data,
        exclude=list(app_excludes),
    )


def compute_app_includes_excludes(template_dir: Path) -> tuple[set[str], set[str]]:
    app_includes, app_excludes = compute_app_includes_excludes_helper(
        template_dir, template_dir
    )
    app_excludes.difference_update([".template", ".git", "."])
    app_excludes.update(["*template-only*"])
    return app_includes, app_excludes


def compute_app_includes_excludes_helper(
    root_dir: Path, path: Path
) -> tuple[set[str], set[str]]:
    relpath_str = str(path.relative_to(root_dir))
    if "{{app_name}}" in relpath_str:
        return (set([relpath_str]), set())

    if "template-only" in relpath_str:
        return (set(), set())

    if path.is_file():
        return (set(), set([relpath_str]))

    assert path.is_dir()
    subpaths = list(path.iterdir())
    if len(subpaths) == 0:
        return (set(), set())

    subresults = list(
        compute_app_includes_excludes_helper(root_dir, subpath) for subpath in subpaths
    )

    subincludes, subexcludes = zip(*subresults)
    includes: set[str] = functools.reduce(operator.or_, subincludes, set())
    excludes: set[str] = functools.reduce(operator.or_, subexcludes, set())

    if len(includes) == 0:
        return (set(), set([relpath_str]))

    return (includes, excludes)
