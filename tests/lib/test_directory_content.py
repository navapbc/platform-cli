from tests.lib.directory_content import DirectoryContent


def test_directory_content_from_fs(tmp_path):
    (tmp_path / "onedir").mkdir()
    (tmp_path / "onedir" / "onefile").write_text("content")
    (tmp_path / "twodir").mkdir()
    (tmp_path / "twodir" / "threedir").mkdir()
    (tmp_path / "twodir" / "threedir" / "threefile").write_text("content")
    directory_content = DirectoryContent.from_fs(tmp_path)
    assert directory_content == DirectoryContent(
        {
            "onedir": DirectoryContent({"onefile": "content"}),
            "twodir": DirectoryContent({"threedir": DirectoryContent({"threefile": "content"})}),
        }
    )


def test_directory_content_from_fs_with_ignore(tmp_path):
    (tmp_path / "ignore").mkdir()
    (tmp_path / "ignore" / "ignorefile").write_text("content")
    (tmp_path / "twodir").mkdir()
    (tmp_path / "twodir" / "ignore").mkdir()
    (tmp_path / "twodir" / "ignore" / "threefile").write_text("content")
    (tmp_path / "twodir" / "threedir").mkdir()
    (tmp_path / "twodir" / "threedir" / "threefile").write_text("content")
    (tmp_path / "twodir" / "threedir" / "ignore").write_text("content")
    directory_content = DirectoryContent.from_fs(tmp_path, ignore=["ignore"])
    assert directory_content == DirectoryContent(
        {
            "twodir": DirectoryContent({"threedir": DirectoryContent({"threefile": "content"})}),
        }
    )
