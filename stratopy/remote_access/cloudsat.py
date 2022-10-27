from . import base


class CloudSat(base.S3Mixin, base.ConnectorABC):
    def __init__(self, product_type):
        self.product_type = product_type

    def __repr__(self):
        return "CloudSat object."

    def get_endpoint(self):
        ...

    def _makequery(self, endpoint, date):
        ...

    def _parse_result(self, result):
        ...
