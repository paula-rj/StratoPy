import datetime

from stratopy.remote_access import base


def test_ConnectorABC():
    class FakeConnector(base.ConnectorABC):
        @classmethod
        def get_endpoint(cls):
            return []

        def _makequery(self, endpoint, pdate):
            endpoint.extend(["_makequery", pdate])
            return endpoint

        def _download(self, query):
            query.append("_download")
            return query

        def _parse_result(self, response):
            response.append("_parse_result")
            return response

    conn = FakeConnector()
    result = conn.fetch("june 25th 2022")

    expected = [
        "_makequery",
        datetime.datetime(2022, 6, 25),
        "_download",
        "_parse_result",
    ]
    assert result == expected
