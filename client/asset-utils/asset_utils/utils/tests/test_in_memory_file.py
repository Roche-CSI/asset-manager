import json
import os

from ruamel.yaml import YAML

from asset_utils.utils.file_utils import FileUtils
from asset_utils.utils.in_memory_file import InMemoryFile


def data_file(data, file_ext: str) -> InMemoryFile:
    mem_file = InMemoryFile(file_ext=file_ext)
    mem_file.add_data(filedata=data)
    mem_file.file.seek(0)  # prepare for reading
    return mem_file


def test_add_data():
    data = {"name": "asset-manager"}
    # json
    assert json.load(data_file(data=data, file_ext=".json").file) == data
    # yaml
    assert YAML().load(data_file(data=data, file_ext=".yaml").file) == data
    # zip
    zip_file = data_file(data={"objects.json": data}, file_ext=".zip")
    zip_content = FileUtils.read_zip_stream(zip_bytes=zip_file.file)
    result = json.loads(zip_content["objects.json"])
    assert result == data


def test_write_to_file(test_data):
    data = {"name": "asset-manager"}

    def json_check():
        json_file = data_file(data=data, file_ext=".json")
        dst = os.path.join(test_data, "write.json")
        if os.path.exists(dst):
            os.unlink(dst)
        json_file.write(dst)
        assert os.path.exists(dst)
        contents = FileUtils.read_json(dst)
        assert contents == data

    def yaml_check():
        yaml_file = data_file(data=data, file_ext=".yaml")
        dst = os.path.join(test_data, "write.yaml")
        if os.path.exists(dst):
            os.unlink(dst)
        yaml_file.write(dst)
        assert os.path.exists(dst)
        contents = FileUtils.read_yaml(dst)
        assert contents == data

    def zip_check():
        yaml_file = data_file(data={"objects.yaml": data}, file_ext=".zip")
        dst = os.path.join(test_data, "write.zip")
        if os.path.exists(dst):
            os.unlink(dst)
        yaml_file.write(dst)
        assert os.path.exists(dst)
        zip_content = FileUtils.read_zip_file(dst)
        result = YAML().load(zip_content["objects.yaml"])
        assert result == data

    json_check()
    yaml_check()
    zip_check()
