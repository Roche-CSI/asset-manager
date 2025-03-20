from asset_pluggy.storage import Transporter, TransportResource
from asset_plugin_posix.transporter import async_shutil


class AsyncPosixTransporter(Transporter):

    def validate(self, credentials: dict):
        pass

    def transfer(self, resources: [TransportResource]):
        self.copy(resources=resources)

    def copy(self, resources: [TransportResource]):
        async_shutil.copy_resources(resources=resources)

    def upload(self, resources: [TransportResource]):
        async_shutil.copy_resources(resources=resources)

    def download(self, resources: [TransportResource]):
        async_shutil.copy_resources(resources=resources)
