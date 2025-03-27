from asset_core.api.repo_api import VersionAPI


def test_version_api(asset, repo, capfd):
    api = VersionAPI(repo=repo, asset=asset)
    versions = api.list_versions_summary(jsonize=True)
    out, err = capfd.readouterr()
    assert versions is None
    assert "versions not available" in out
    assert not err

    # test name
    name = api.name()
    assert "group_test" in name

    # test active version
    active = api.active_version()
    assert "temp_" in active
