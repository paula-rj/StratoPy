import datetime

from unittest import mock, TestCase

import pytest

from stratopy.remote_access import base

import xarray


def test_ConnectorABC():
    class FakeConnector(base.ConnectorABC):
        @classmethod
        def get_endpoint(cls):
            return []

        def _makequery(self, endpoint, pdate):
            endpoint.extend([("_makequery", pdate.isoformat())])
            return endpoint

        def _download(self, query):
            query.append("_download")
            return query

        def _parse_result(self, response):
            response.append("_parse_result")
            return response

    conn = FakeConnector()
    result = conn.fetch("june 25th 2022 18:00")

    expected = [
        ("_makequery", "2022-06-25T18:00:00"),
        "_download",
        "_parse_result",
    ]
    assert result == expected


def test_S3mixin_FileNotFoundError():
    class TestFileNotFoundError(base.S3Mixin, base.ConnectorABC):
        def get_endpoint(cls):
            return None

        def _makequery(self, endpoint, pdate):
            return pdate.isoformat()

        def _parse_result(self, response):
            return None

    conn = TestFileNotFoundError()

    with mock.patch("s3fs.S3FileSystem.glob", return_value=[]) as mglob:
        with pytest.raises(FileNotFoundError):
            conn.fetch("27 jul 1981")
    mglob.assert_called_once_with("1981-07-27T00:00:00")
