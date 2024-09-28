from pathlib import Path
import copier

from .compute_app_includes_excludes import compute_app_includes_excludes


def update(template_dir: str, project_dir: str):
    answers_file = ".template/.template-infra-base.yml"

    app_includes, _ = compute_app_includes_excludes(Path(template_dir))
    global_excludes = ["*template-only*"]
    base_excludes = global_excludes + list(app_includes)

    copier.run_update(
        project_dir,
        answers_file=answers_file,
        exclude=base_excludes,
        skip_answered=True,
    )
    # copier update --skip-answered --exclude "template-only*" --vcs-ref "${ref}" "${dest}" --answers-file ".template/.template-infra-base.yml" \
    #   --exclude ".github"
    # git stash
