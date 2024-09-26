import os
import pytest

from nava.commands.infra.get_app_names import get_app_names


@pytest.fixture
def tmp_template(tmp_path):
    infra_dir = tmp_path / "infra"
    infra_dir.mkdir()
    (infra_dir / "app1").mkdir()
    (infra_dir / "app2").mkdir()
    (infra_dir / "infra").mkdir()
    (infra_dir / "accounts").mkdir()
    return tmp_path


def test_get_app_names(tmp_template, capsys):
    # Call the function with the temporary directory
    get_app_names(str(tmp_template))

    # Capture the output
    captured = capsys.readouterr()

    # Check that only the non-excluded directories are printed
    assert "app1" in captured.out
    assert "app2" in captured.out
    assert "infra" not in captured.out
    assert "accounts" not in captured.out


def test_get_app_names_no_infra_dir(tmp_path, capsys):
    # Call the function with a directory that does not contain 'infra'
    get_app_names(str(tmp_path))

    # Capture the output
    captured = capsys.readouterr()

    # Check that the appropriate message is printed
    assert f"The path {tmp_path / 'infra'} does not exist." in captured.out
