import json
import os
from server_core.utils.file_utils import FileUtils


def test_generate_zip():
    cwd = os.path.dirname(__file__)
    zip_path = os.path.join(cwd, "test.zip")
    if os.path.exists(zip_path):
        os.unlink(zip_path)  # cleanup
    data ={
        "some": "value"
    }
    FileUtils.generate_zip([("objects.json", FileUtils.json_serialize(data))], zip_path)
    assert os.path.exists(zip_path)

    # read and test
    zip_contents = FileUtils.read_zip_file(zip_path)
    retrieved = json.loads(zip_contents["objects.json"])
    assert retrieved == data
    os.unlink(zip_path)


def test_zip_in_memory_zip():
    cwd = os.path.dirname(__file__)
    zip_path = os.path.join(cwd, "test.zip")
    if os.path.exists(zip_path):
        os.unlink(zip_path)  # cleanup
    data ={
        "some": "value"
    }
    zip: bytes = FileUtils.zip_in_memory([("objects.json", FileUtils.json_serialize(data))])
    with open(zip_path, "wb") as f:
        f.write(zip)
    # FileUtils.write_text(zip_path, zip)
    assert os.path.exists(zip_path)

    # read and test
    zip_contents = FileUtils.read_zip_file(zip_path)
    retrieved = json.loads(zip_contents["objects.json"])
    assert retrieved == data
    # os.unlink(zip_path)



