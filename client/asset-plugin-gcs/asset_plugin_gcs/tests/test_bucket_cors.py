from asset_plugin_gcs.bucket_cors import update_cors_configuration


def test_add():
    credentials = {}
    bucket_name = "my_test_bucket"
    origin_url = "http://localhost:3000"
    bucket = update_cors_configuration(credentials, bucket_name, origin_url)
    print(f"bucket :{bucket}")
