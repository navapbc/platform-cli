import functools
import operator


from pathlib import Path


def compute_app_includes_excludes(template_dir: Path) -> tuple[set[str], set[str]]:
    app_includes, app_excludes = compute_app_includes_excludes_helper(template_dir, template_dir)
    app_excludes.difference_update([".template-infra", ".git", "."])
    app_excludes.update(["*template-only*"])
    return app_includes, app_excludes


def compute_app_includes_excludes_helper(root_dir: Path, path: Path) -> tuple[set[str], set[str]]:
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
