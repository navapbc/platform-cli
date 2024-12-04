def test_info_empty_project_no_git(cli, new_project_no_git):
    cli(
        [
            "infra",
            "info",
            str(new_project_no_git.dir),
        ],
    )


def test_info_empty_project(cli, new_project):
    cli(
        [
            "infra",
            "info",
            str(new_project.dir),
        ],
    )


def test_info_clean_install(cli, new_project, clean_install):
    cli(
        [
            "infra",
            "info",
            str(new_project.dir),
        ],
    )
