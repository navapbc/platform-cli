from click.testing import CliRunner


def test_install(cli, tmp_template, tmp_project):
    cli(["infra", "install", str(tmp_template), str(tmp_project)])
