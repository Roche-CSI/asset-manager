import pytest

from asset_core.api.repo_api import AddAPI
from asset_utils.common import exceptions


def test_validate_alias(repo):
    test_data = {
        "test_alias": True,
        "test-alias": True,
        "test.alias": True,
        "": False,
        "12345": False,
        12345: False,
        "temp_123": False,
        "test@alias": False,
        "test$alias": False,
        "test#alias": False,
        "test&alias": False,
    }
    api = AddAPI(repo)
    for alias, valid in test_data.items():
        if valid:
            assert api.validate_alias(alias) is None
        else:
            with pytest.raises(exceptions.InvalidAliasError):
                api.validate_alias(alias)
