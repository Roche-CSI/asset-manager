from gcp.signed_url import generate_signed_url
import os


def test_generate_url():
    url = generate_signed_url(
        service_account_file=os.environ.get("GOOGLE_APPLICATION_CREDENTIALS"),
        bucket_name = "placeholder_bucket",
        object_name = "placeholder/path/to/object.yaml"
    )
    print(url)
