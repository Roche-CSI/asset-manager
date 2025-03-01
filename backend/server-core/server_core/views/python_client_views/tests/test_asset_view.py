

def test_root_url(test_app):
    res = test_app.get('/', follow_redirects=True)
    res.data.decode("ascii") == "Hello World!" and res.status_code == 200


def test_asset_list(test_app):
    res = test_app.get('/asset', follow_redirects=True)
    assert res.status_code == 200


