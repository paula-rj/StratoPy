#!/usr/bin/env python
# -*- coding: utf-8 -*-
# License: MIT (https://tldrlegal.com/license/mit-license)
# Copyright (c) 2022, Paula Romero Jure et al.
# All rights reserved.
from unittest import mock

import pytest

from stratopy import metadatatools
from stratopy.extractors import ebase

import xarray as xa


CLDSAT_PATH = (
    "StratoPy/tests/data/CloudSat/",
    "2019002175851_67551_CS_2B-CLDCLASS_GRANULE_P1_R05_E08_F03.hdf",
)


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
            return xa.DataArray()

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
    listdir.return_value = [
        "2010176150042_67652_CS_2B-CLDCLASS_GRANULE_P1_R05_E08_F03.hdf",
    ]

    get = open_sftp.return_value.__enter__.return_value.get
    get.return_value = ["value"]

    response = conn.fetch("27/07/1981", force=True)
    listdir.assert_called_once_with("dir")

    assert isinstance(response, xa.DataArray)
    del conn  # to check coverage
