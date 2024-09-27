import filecmp


def assert_dirs_equal(dir1, dir2):
    comparison = filecmp.dircmp(dir1, dir2)
    assert not comparison.left_only
    assert not comparison.right_only
    assert not comparison.diff_files
