"""Used only in asset-server"""
from google.cloud import storage


def get_bucket_cors(credentials: dict, bucket_name: str):
    """Set a bucket's CORS policies configuration."""
    storage_client = storage.Client.from_service_account_info(credentials)
    bucket = storage_client.get_bucket(bucket_name)
    return bucket.cors


def update_cors_configuration(credentials: dict, bucket_name, origin_url: str):
    """Set a bucket's CORS policies configuration.
    cors = [
        {
            "origin": [
                "http://localhost:5000"
                "https://asset.test.com:8001"
            ],
            "method": [
                "GET"
            ],
            "responseHeader": [
                "Content-Type"
            ],
            "maxAgeSeconds": 3600
        }
    ]
    """
    storage_client = storage.Client.from_service_account_info(credentials)
    bucket = storage_client.get_bucket(bucket_name)
    cors = bucket.cors
    cors[0]["origin"].append(origin_url)
    bucket.cors = cors
    bucket.patch()
    print(f"Set CORS policies for bucket {bucket.name} is {bucket.cors}")
    return bucket
