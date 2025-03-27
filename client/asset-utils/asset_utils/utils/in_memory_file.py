"""Used only in asset-server"""
import io
import os
from typing import Union

from .file_utils import FileUtils
from .in_memory_zip import InMemoryZip

BinaryFormats = {".zip"}
DataFormats = {".json", ".yaml", ".yml"}


class InMemoryFile:
    # create a file-like object in memory
    file: Union[io.StringIO, io.BytesIO]
    file_ext: str

    def __init__(self, file_ext: str, file_data=None):
        self.file_ext = file_ext
        self.file = io.BytesIO() if format in BinaryFormats else io.StringIO()
        self.add_data(filedata=file_data)

    def add_data(self, filedata: dict):
        if not filedata:
            return
        if self.file_ext in BinaryFormats:
            self.file = serialize_for_file(file_ext=self.file_ext, filedata=filedata)
        else:
            serialize_for_file(file_ext=self.file_ext, filedata=filedata, io_stream=self.file)

    def write(self, path: str):
        if self.file_ext in BinaryFormats:
            FileUtils.write_binary(dst=path, content=self.file.getvalue())
        else:
            FileUtils.write_text(dst=path, content=self.file.getvalue())


def serialize_for_file(file_ext: str, filedata, io_stream: io.StringIO = None):
    if file_ext in [".yaml", ".yml"]:
        if io_stream:
            FileUtils.write_yaml_to_stream(data=filedata, stream=io_stream)
        else:
            return FileUtils.yaml_serialize(filedata)
    elif file_ext in [".json"]:
        if io_stream:
            FileUtils.write_json_to_stream(data=filedata, stream=io_stream)
        else:
            return FileUtils.json_serialize(filedata)
    elif file_ext in [".zip"]:
        memzip = InMemoryZip()
        serialized = []
        for filename in filedata:
            # convert recursively
            serialized.append((filename, serialize_for_file(os.path.splitext(filename)[1], filedata[filename])))
        memzip.add_files(serialized)
        return memzip.mem_zip
    else:
        io_stream.write(filedata)
