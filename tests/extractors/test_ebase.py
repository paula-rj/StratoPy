#!/usr/bin/env python
# -*- coding: utf-8 -*-
# License: MIT (https://tldrlegal.com/license/mit-license)
# Copyright (c) 2022, Paula Romero Jure et al.
# All rights reserved.
import os
from unittest import mock

import pytest

from stratopy import metadatatools
from stratopy.extractors import ebase


class _WithAttrs:
    def __init__(self, obj, attrs=None):
        self.obj = obj
        self.attrs = dict(attrs) if attrs else {}

    def __getitem__(self, k):
        return self.obj[k]

    def __setitem__(self, k, v):
        self.obj[k] = v

    def __getattr__(self, a):
        return getattr(self.obj, a)


# -----------------------------------------------------------------------------
# General tests
# -----------------------------------------------------------------------------
def test_ConnectorABC_xx():
    class FakeConnector(ebase.ConnectorABC):
        @classmethod
        def get_endpoint(cls):
            return []

        def _makequery(self, endpoint, pdate):
            # noqa
            endpoint.extend([("_makequery", pdate.isoformat())])
            return endpoint

        def _download(self, query):
            query.append("_download")
            return query

        def _parse_result(self, response):
            response.append("_parse_result")
            return _WithAttrs(response)

        def get_orbit_type(cls):
            return metadatatools.POLAR

        def get_instrument_type(self):
            return metadatatools.RADARS

        def get_platform(self):
            return "G16"

        def get_product_type_key(self):
            return "some product"

    conn = FakeConnector()
    result = conn.fetch("june 25th 2022 18:00", tzone="UTC")

    expected_obj = [
        ("_makequery", "2022-06-25T18:00:00+00:00"),
        "_download",
        "_parse_result",
    ]
    expected_attrs = {
        metadatatools.STRATOPY_METADATA_KEY: metadatatools.Metadata(
            orbit_type=metadatatools.POLAR,
            platform=metadatatools.GOES,
            instrument_type=metadatatools.RADARS,
            product_key="some product",
        )
    }

    assert result.obj == expected_obj
    assert result.attrs == expected_attrs


def test_ConnectorABC_get_endpoint_not_implementhed():
    class Fake1Connector(ebase.ConnectorABC):
        def get_endpoint(self):
            return super().get_endpoint()

        def _makequery(self, endpoint, pdate):
            return None

        def _download(self, query):
            return None

        def _parse_result(self, response):
            return None

        @classmethod
        def get_orbit_type(cls):
            return metadatatools.POLAR

        def get_platform(self):
            return super().get_platform()

        def get_product_type_key(self):
            return "some product"

    with pytest.raises(NotImplementedError):
        Fake1Connector().fetch("27 jul 1981", tzone="UTC")


def test_ConnectorABC_makequery_not_implementhed():
    class Fake2Connector(ebase.ConnectorABC):
        def get_endpoint(self):
            return None

        def _makequery(self, endpoint, pdate):
            return super()._makequery(endpoint, pdate)

        def _download(self, query):
            return None

        def _parse_result(self, response):
            return None

        @classmethod
        def get_orbit_type(cls):
            return metadatatools.POLAR

        def get_platform(self):
            return super().get_platform()

        def get_instrument_type(self):
            return metadatatools.RADARS

        def get_product_type_key(self):
            return "some product"

    with pytest.raises(NotImplementedError):
        Fake2Connector().fetch("27 jul 1981", tzone="UTC")


def test_ConnectorABC_download_not_implementhed():
    class Fake3Connector(ebase.ConnectorABC):
        def get_endpoint(self):
            return None

        def _makequery(self, endpoint, pdate):
            return None

        def _download(self, query):
            return super()._download(query)

        def _parse_result(self, response):
            return None

        @classmethod
        def get_orbit_type(cls):
            return metadatatools.POLAR

        def get_platform(self):
            return metadatatools.RADARS

        def get_product_type_key(self):
            return "some product"

    with pytest.raises(NotImplementedError):
        Fake3Connector().fetch("27 jul 1981", tzone="UTC")


def test_ConnectorABC_parse_result_not_implementhed():
    class Fake4Connector(ebase.ConnectorABC):
        def get_endpoint(self):
            return None

        def _makequery(self, endpoint, pdate):
            return None

        def _download(self, query):
            return None

        def _parse_result(self, response):
            return super()._parse_result(response)

        @classmethod
        def get_orbit_type(cls):
            return metadatatools.POLAR

        def get_platform(self):
            return super().get_platform()

        def get_product_type_key(self):
            return "some product"

    with pytest.raises(NotImplementedError):
        Fake4Connector().fetch("27 jul 1981", tzone="UTC")


def test_ConnectorABC_orbitype_not_implementhed():
    class Fake5Connector(ebase.ConnectorABC):
        def get_endpoint(self):
            return super().get_endpoint()

        def _makequery(self, endpoint, pdate):
            return None

        def _download(self, query):
            return None

        def _parse_result(self, response):
            return None

        def get_platform(self):
            return super().get_platform()

        def get_product_type_key(self):
            return "some product"

    with pytest.raises(TypeError):
        Fake5Connector().fetch("27 jul 1981", tzone="UTC")


def test_ConnectorABC_platform_not_implementhed():
    class Fake6Connector(ebase.ConnectorABC):
        def get_endpoint(self):
            return None

        def _makequery(self, endpoint, pdate):
            return super()._makequery(endpoint, pdate)

        def _download(self, query):
            return None

        def _parse_result(self, response):
            return None

        def get_orbit_type(cls):
            return metadatatools.POLAR

        def get_instrument_type(self):
            return metadatatools.RADARS

        def get_product_type_key(self):
            return "some product"

    with pytest.raises(TypeError):
        Fake6Connector().fetch("27 jul 1981", tzone="UTC")


def test_ConnectorABC_instrumentype_not_implementhed():
    class Fake7Connector(ebase.ConnectorABC):
        def get_endpoint(self):
            return None

        def _makequery(self, endpoint, pdate):
            return super()._makequery(endpoint, pdate)

        def _download(self, query):
            return None

        def _parse_result(self, response):
            return None

        def get_orbit_type(cls):
            return metadatatools.POLAR

        def get_platform(self):
            return super().get_platform()

        def get_product_type_key(self):
            return "some product"

    with pytest.raises(TypeError):  # salta el make query
        Fake7Connector().fetch("27 jul 1981", tzone="UTC")


def test_ConnectorABC_productkey_not_implementhed():
    class Fake8Connector(ebase.ConnectorABC):
        def get_endpoint(self):
            return None

        def _makequery(self, endpoint, pdate):
            return super()._makequery(endpoint, pdate)

        def _download(self, query):
            return None

        def _parse_result(self, response):
            return None

        def get_orbit_type(cls):
            return metadatatools.POLAR

        def get_platform(self):
            return "G16"

        def get_instrument_type(self):
            return metadatatools.RADARS

    with pytest.raises(TypeError):
        Fake8Connector().fetch("27 jul 1981", tzone="UTC")


# --------------------------------------------------------------
# S3Mixin
# --------------------------------------------------------------


def test_S3mixin_FileNotFoundError():
    class TestFileNotFoundError(ebase.S3Mixin, ebase.ConnectorABC):
        def get_endpoint(cls):
            return None

        def _makequery(self, endpoint, pdate):
            return pdate.isoformat()

        def _parse_result(self, response):
            return None

        @classmethod
        def get_orbit_type(cls):
            return metadatatools.GEOSTATIONARY

        def get_platform(self):
            return super().get_platform()

        def get_product_type_key(self):
            return "some product"

    conn = TestFileNotFoundError()

    with mock.patch("s3fs.S3FileSystem.glob", return_value=[]) as mglob:
        with pytest.raises(FileNotFoundError):
            conn.fetch("27 jul 1981", tzone="UTC")
    mglob.assert_called_once_with("1981-07-27T00:00:00+00:00*")


# -----------------------------------------------------------------------------
# SFTPMixin
# -----------------------------------------------------------------------------


@mock.patch("paramiko.SSHClient.open_sftp")
@mock.patch("paramiko.SSHClient.connect")
@mock.patch("paramiko.RSAKey.from_private_key_file", return_value="pkey")
def test_SFTPMixin_download(from_private_key_file, connect, open_sftp):
    class TestSFTP(ebase.SFTPMixin, ebase.ConnectorABC):
        def get_endpoint(cls):
            return "endpoint"

        def _makequery(self, endpoint, pdate):
            return "dir/pattern.*"

        def _parse_result(self, response):
            # response.append("_parse_result")
            return response

        @classmethod
        def get_orbit_type(cls):
            return metadatatools.POLAR

        def get_platform(self):
            return metadatatools.GOES

        def get_instrument_type(self):
            return metadatatools.RADARS

        def get_product_type_key(self):
            return "some product"

    conn = TestSFTP("host", "port", "zaraza@coso.com", keyfile="algo")

    from_private_key_file.assert_called_once_with("algo", password=None)
    connect.assert_called_once_with(
        "host", port="port", username="zaraza@coso.com", pkey="pkey"
    )

    # mock listdir
    listdir = open_sftp.return_value.__enter__.return_value.listdir
    listdir.return_value = ["pattern.ext"]

    get = open_sftp.return_value.__enter__.return_value.get
    get.return_value = ["value"]

    response = conn.fetch("27/07/1981", force=True)

    listdir.assert_called_once_with("dir")

    get.assert_called_once()
    get.call_args.kwargs["remotepath"] == "dir/pattern.ext"
    # localpath is a randomstring

    assert os.path.basename(response).startswith("stpy_")

    del conn  # to check coverage
