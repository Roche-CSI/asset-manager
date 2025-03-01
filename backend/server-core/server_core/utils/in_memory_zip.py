import io
import zipfile


class InMemoryZip:
    mem_zip: io.BytesIO = None

    def __init__(self):
        # create a file-like object for the Zip file
        self.mem_zip = io.BytesIO()

    def add_files(self, files: [tuple]):
        """adds files to zip
        """
        with zipfile.ZipFile(self.mem_zip, 'w') as zf:
            for file_name, file_data in files:
                # add the file to the Zip file
                zf.writestr(file_name, file_data)

    def get_bytes(self) -> bytes:
        # get the bytes of the Zip file
        return self.mem_zip.getvalue()

    def write(self, path: str):
        with open(path, 'wb') as f:
            # write the contents of the BytesIO object to the file
            f.write(self.mem_zip.getvalue())
