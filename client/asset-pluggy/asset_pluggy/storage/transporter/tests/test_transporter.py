import json

import pytest

from asset_pluggy.storage.transporter import Transporter

GCS_1 = {
    "credentials": {
        "project_id": "general_random1_gcs",
        "email": "general@general.com",
        "private_key_id": "e6dd5048-7be8-4c74-a786-2d0596eb635b"
    },
    "prefixes": ["gcs"]
}

GCS_2 = {
    "credentials": {
        "project_id": "random2_general_gcs",
        "email": "random2@general.com",
        "private_key_id": "90d8ca60-9027-4ad2-9f8c-dfdfc22e874c"
    },
    "prefixes": ["gcs"]
}

S3_1 = {
    "credentials": {
        "project_id": "s3_random2_general",
        "email": "random2@general.com",
        "private_key_id": "b61ebf28-d5ab-490f-9bb0-f3a466eb91cb"
    },
    "prefixes": ["s3"]
}

S3_2 = {
    "credentials": {
        "project_id": "s3_random2_general",
        "email": "random2@general.com",
        "private_key_id": "04757873-e93f-4b8f-bd4f-0fb92b2fc972"
    },
    "prefixes": ["s3"]
}


def test_transporter():
    assert_transporter(cred=GCS_1)
    # test with null credentials
    Transporter.de_init()
    with pytest.raises(Exception) as e:
        assert_transporter(cred={})
    assert e
    Transporter.de_init()
    # test credentials switch
    creds = [GCS_1, GCS_2]
    for cred in creds:
        assert_transporter(cred=cred)


def assert_transporter(cred: dict):
    transport = Transporter.shared(credentials=cred.get("credentials"),
                                   prefixes=cred.get("prefixes"),
                                   validate=True)
    assert transport and isinstance(transport, Transporter)
    assert json.dumps(transport.credentials) == json.dumps(cred.get("credentials"))
