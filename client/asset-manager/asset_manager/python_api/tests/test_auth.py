from asset_manager.python_api.auth import Auth


def test_auth_login():
    user = Auth().login()
    expected = {"username": str, "email": str, "token": str, "projects": list}
    for key in expected:
        assert type(user.get(key)) == expected[key]


def test_auth_login_with_token():
    token = "your_asset_manager_token"
    user = Auth().login(token=token)
    expected = {"username": str, "email": str, "token": str, "projects": list}
    for key in expected:
        assert type(user.get(key)) == expected[key]


def test_auth_info():
    info = Auth().info()
    expected = ["username", "email", "project"]
    for key in expected:
        assert info.get(key)


def test_auth_info_token():
    info = Auth().info(token=True)
    expected = ["token"]
    for key in expected:
        assert info.get(key)


def test_auth_info_update():
    user = Auth().update()
    expected = {"username": str, "email": str, "token": str, "projects": list}
    for key in expected:
        assert type(user.get(key)) == expected[key]
