import os
import shutil
import logging
import tempfile
from asset_core.store.repo import Repo

logger = logging.getLogger(__file__)


def test_create_repo():
    """
    initializes repo and verifies the .assets exists at the base directory of the repo
    """
    temp_dir = os.path.realpath(tempfile.mkdtemp())

    # initialize assets
    repo_dir = Repo.create_repo(root_dir=temp_dir)
    logger.info("created assets repo at:{}".format(repo_dir))

    # make sure it got created
    if not os.path.exists(os.path.join(str(repo_dir), Repo.asset_dir())):
        # remove temp_dir
        shutil.rmtree(path=repo_dir)

    assert os.path.exists(os.path.join(str(repo_dir), Repo.asset_dir()))


def test_find_root():
    """test finding root of the repo, the function is supposed to traverse up in the directory tree
    until it finds a .assets dir"""
    leaf_dir_name = "./parent/child/grand_child/grand_grand_child"

    # remove symlinks, assets only recognizes realpath
    temp_dir = os.path.realpath(tempfile.mkdtemp())
    leaf_dir = os.path.abspath(os.path.join(temp_dir, leaf_dir_name))

    # initialize assets
    repo_dir = Repo.create_repo(root_dir=temp_dir)
    logger.info("created assets repo at:{}".format(repo_dir))

    # create dir tree
    os.makedirs(leaf_dir, exist_ok=True)

    # change to leaf_node
    os.chdir(leaf_dir)
    logger.info("checking repo from:{}".format(os.getcwd()))

    # find repo
    repo = Repo.find_root()
    logger.info("found repo at:{}".format(repo))

    # delete the temp_dir before asserting, we want to start clean when test fails
    shutil.rmtree(path=temp_dir)
    logger.info("removed directory tree at:{}".format(temp_dir))

    # make sure its pointing to the root
    assert str(repo) == temp_dir
