import os
import shutil
import tempfile

import pytest

from asset_core.store import Repo


@pytest.fixture(scope="module")
def repo_dst():
    temp_dir = os.path.realpath(tempfile.mkdtemp())
    yield temp_dir
    shutil.rmtree(temp_dir)


def test_create_repo(repo_dst, store):
    """
    Parameters
    ----------
    repo_dst: local fixture
    store: global fixture, creates a separate asset store for testing purpose
    """
    test_repo = Repo.create_repo(root_dir=repo_dst)
    assert test_repo.id
    assert test_repo.fs_path == repo_dst

    # verify paths
    assert os.path.exists(test_repo.repo_file)
