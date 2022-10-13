import datetime

from unittest import mock, TestCase

from stratopy.remote_access import base

import xarray

import pytest

PATH_CHANNEL_13 = (
    "data/GOES16/"
    "OR_ABI-L2-CMIPF-M3C13_G16_s20190040600363_e20190040611141_"
    "c20190040611220.nc"
)


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
    result = conn.fetch("june 25th 2022 18:00")

    expected = [
        "_makequery",
        datetime.datetime(2022, 6, 25),
        "_download",
        "_parse_result",
    ]
    assert result == expected


def test_NetCDFmixin():
    a = base.NetCDFmixin()
    a_to_xarr = a._parse_result(PATH_CHANNEL_13)
    assert isinstance(a_to_xarr, xarray.core.dataset.Dataset)


def test_NothingHereError():

    class TestNothingHere(base.ConnectorABC, base.S3mixin):
        def get_endpoint(cls):
            return None

        def _makequery(self, endpoint, pdate):
            self.endpoint=endpoint
            self.endpoint=pdate
            return None

        def _download(self, query):
            self.query = query
            return None

        def _parse_result(self, response):
            self.response = response
            return None

        def test_avail(self):
            self.s3obj = base.S3mixin()
            return None 
        
    conn = TestNothingHere()

    with mock.patch("s3fs.S3FileSystem.glob", return_value=[]) as mglob:
        with pytest.raises(base.NothingHereError):
            conn.fetch("27 jul 1981")
    mglob.assert_called_once_with("1981-07-27T00:00:00")



def test_S3mixin():

    m = mock.MagicMock(url_to_mock, body=the_file)

    # with requests_mock.mock() as m:
    # current_folder = os.path.dirname(os.path.abspath(__file__))
    # path = os.path.join(
    #    current_folder, filename
    # )
    # with open(path, "rb") as the_file:
    #    m.get(url_to_mock, body=the_file)

    return None
