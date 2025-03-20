import os
import shutil
from datetime import datetime

from asset_plugin_posix.transporter.async_posix_transporter import AsyncPosixTransporter
from asset_plugin_posix.transporter.posix_transport_resource import PosixTransportResource

TEST_URLS = [
    "file_types/csvs/customers.csv",
    "file_types/csvs/income.csv",
    "file_types/jpegs/photo-1522364723953-452d3431c267.jpg",
    "file_types/jsons/web_app.json",
    "file_types/yamls/invoice.yaml",
    "file_types/yamls/model.yml"
]


def datetime_string(date: datetime):
    return date.strftime("%m-%d-%Y_%H-%M-%S")


def test_upload(test_data):
    date_string = datetime_string(date=datetime.now())
    upload_url = os.path.join(test_data, "upload_test", date_string)
    targets = []
    for url_string in TEST_URLS:
        dst = os.path.join(upload_url, os.path.basename(url_string))
        res = PosixTransportResource(src=os.path.join(test_data, url_string), dst=dst)
        targets.append(res)

    # upload with transporter
    transport = AsyncPosixTransporter.shared()
    transport.upload(resources=targets)
    # verify
    for target in targets:
        assert os.path.exists(target.dst)
    # cleanup
    shutil.rmtree(upload_url)


def test_download(test_data):
    date_string = datetime_string(date=datetime.now())
    download_dir = os.path.join(test_data, "download_test", date_string)
    targets = []
    for url_string in TEST_URLS:
        dst = os.path.join(download_dir, os.path.basename(url_string))
        res = PosixTransportResource(src=os.path.join(test_data, url_string), dst=dst)
        targets.append(res)

    # download with transporter
    transport = AsyncPosixTransporter.shared()
    transport.download(resources=targets)
    # verify
    for target in targets:
        assert os.path.exists(target.dst)
    # cleanup
    shutil.rmtree(download_dir)


def test_copy(test_data):
    date_string = datetime_string(date=datetime.now())
    copy_dir = os.path.join(test_data, "copy_test", date_string)
    targets = []
    for url_string in TEST_URLS:
        dst = os.path.join(copy_dir, os.path.basename(url_string))
        res = PosixTransportResource(src=os.path.join(test_data, url_string), dst=dst)
        targets.append(res)

    # copy with transporter
    transport = AsyncPosixTransporter.shared()
    transport.copy(resources=targets)
    # verify
    for target in targets:
        assert os.path.exists(target.dst)
    # cleanup
    shutil.rmtree(copy_dir)
