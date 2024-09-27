import os
import copier


def add_app(template_dir: str, project_dir: str, app_name: str):
    answers_file = f".template-infra-app-{app_name}.yml"
    data = {"app_name": app_name}

    # compute app exclusions by doing:
    # app includes = .github, infra/{{app_name}}
    # global excludes = template-only* (unused)
    # app excludes = global excludes + all – app includes
    # app_excludes="${global_excludes}
    # $(comm -23 <(echo "${all}" | sort) <(echo "${app_includes}" | sort))"

    app_includes = set([".github/", "infra/{{app_name}}"])
    global_excludes = set(["*template-only*"])
    all_except_infra = set(os.listdir(template_dir)) - set(["infra", ".template"])
    infra_only = set(os.listdir(os.path.join(template_dir, "infra")))
    all = all_except_infra.union(infra_only)
    app_excludes = global_excludes.union(all) - app_includes

    copier.run_copy(
        template_dir,
        project_dir,
        answers_file=answers_file,
        data=data,
        exclude=list(app_excludes),
    )
