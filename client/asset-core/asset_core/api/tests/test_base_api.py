import copy
import os

from asset_core.api.base_api import BaseAPI


class MockAPI(BaseAPI):

    def __init__(self, counter):
        self.counter = counter

    def set_environment(self):
        self._prev_environs = getattr(self, "_prev_environs", [])
        self._prev_environs.append(copy.deepcopy(dict(os.environ)))
        os.environ["TEST"] = str(self.counter)
        print(f"setting environment to {os.environ['TEST']}")

    def unset_environment(self):
        print(f"unsetting environment {os.environ['TEST']}")
        os.environ.update(self._prev_environs.pop())


def test_info_api_environment():
    os.environ["TEST"] = "NOT_SET"
    try:
        with MockAPI(1).environment():
            with MockAPI(2).environment():
                with MockAPI(3).environment():
                    assert os.environ["TEST"] == "3"
                    raise Exception("test")
                assert os.environ["TEST"] == "2"
            assert os.environ["TEST"] == "1"
    except Exception:
        assert os.environ["TEST"] == "NOT_SET"
