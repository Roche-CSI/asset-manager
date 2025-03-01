from utils import string_to_timestamp


def test_string_to_timestamp():
    pst = "2022/02/03 15-36-55 -0800"
    time = string_to_timestamp(pst)
    assert time == 1643931415