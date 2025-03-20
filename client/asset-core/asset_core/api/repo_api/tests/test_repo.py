from asset_core.api.repo_api.repo import RepoAPI


def test_asset(asset, repo):
    api = RepoAPI(repo=repo, asset=asset)
    assert api.asset.name == asset.name
    assert api.asset.id == asset.id
    assert api.asset.remote_url == asset.remote_url
    assert api.asset.repo_dir == asset.repo_dir
    assert api.asset.project_id == asset.project_id


def test_project_id(asset, repo):
    api = RepoAPI(repo=repo, asset=asset)
    assert api.project_id == asset.project_id
