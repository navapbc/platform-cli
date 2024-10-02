from pathlib import Path
import copier

from nava import git
from .compute_app_includes_excludes import compute_app_includes_excludes
from .get_app_names import get_app_names


def update(template_dir: str, project_dir: str):
    base_answers_file = ".template/.template-infra-base.yml"

    app_includes, app_excludes = compute_app_includes_excludes(Path(template_dir))
    global_excludes = ["*template-only*"]
    base_excludes = global_excludes + list(app_includes)

    num_changes = 0

    copier.run_update(
        project_dir,
        answers_file=base_answers_file,
        exclude=base_excludes,
        overwrite=True,
        skip_answered=True,
    )
    git.stash(project_dir)
    num_changes += 1

    for app_name in get_app_names(Path(project_dir)):
        app_answers_file = f".template/.template-infra-app-{app_name}.yml"
        copier.run_update(
            project_dir,
            answers_file=app_answers_file,
            exclude=list(app_excludes),
            overwrite=True,
            skip_answered=True,
        )
        git.stash(project_dir)
        num_changes += 1

    for i in range(num_changes):
        git.pop(project_dir)
