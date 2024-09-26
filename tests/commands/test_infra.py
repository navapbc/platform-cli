from click.testing import CliRunner

from nava.cli import cli


def test_install(tmp_template, tmp_project):
    runner = CliRunner()
    runner.invoke(cli, ["infra", "install", str(tmp_template), str(tmp_project)])
