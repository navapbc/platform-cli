from pathlib import Path
import copier

from .compute_app_includes_excludes import (
    compute_app_includes_excludes,
)


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
