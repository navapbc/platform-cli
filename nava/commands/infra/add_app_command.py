import os
from pathlib import Path
import copier


def add_app(template_dir: str | Path, project_dir: str, app_name: str):
    answers_file = f".template-infra-app-{app_name}.yml"
    data = {"app_name": app_name}

    app_excludes = set([".template", ".git"])
    template_dir = Path(template_dir)
    paths = set(template_dir.iterdir())
    while len(paths) > 0:
        path = paths.pop()

        subpath = str(path.relative_to(template_dir))

        if subpath in app_excludes:
            continue

        if "{{app_name}}" in subpath:
            continue

        if "template-only" in subpath:
            app_excludes.add(subpath)
            continue

        if path.is_dir():
            paths.update(path.iterdir())
            continue

        app_excludes.add(subpath)

    copier.run_copy(
        str(template_dir),
        project_dir,
        answers_file=answers_file,
        data=data,
        exclude=list(app_excludes),
    )
