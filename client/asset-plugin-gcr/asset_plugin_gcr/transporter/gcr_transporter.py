from asset_pluggy.storage.transporter import Transporter, TransportResource


class GcrTransporter(Transporter):

    def upload(self, resources: [TransportResource]):
        # no upload or download allowed currently
        raise NotImplementedError

    def download(self, resources: [TransportResource]):
        # no upload or download allowed currently
        # todo: use docker to download the image
        raise NotImplementedError

    def copy(self, resources: [TransportResource]):
        # no copy allowed currently
        raise NotImplementedError
