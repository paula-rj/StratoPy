#!/usr/bin/env python
# -*- coding: utf-8 -*-
# License: MIT (https://tldrlegal.com/license/mit-license)
# Copyright (c) 2022, Paula Romero Jure et al.
# All rights reserved.
import os
from unittest import mock

import pytest

from stratopy.extractors import base


# ----------------------------------
# General tests
# -----------------------------------
def test_ConnectorABC():
    class FakeConnector(base.ConnectorABC):
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
            return response

    conn = FakeConnector()
    result = conn.fetch("june 25th 2022 18:00", tzone="UTC")

    expected = [
        ("_makequery", "2022-06-25T18:00:00+00:00"),
        "_download",
        "_parse_result",
    ]
    assert result == expected


def test_ConnectorABC_get_endpoint_not_implementhed():
    class Fake1Connector(base.ConnectorABC):
        def get_endpoint(self):
            return super().get_endpoint()

        def _makequery(self, endpoint, pdate):
            return None

        def _download(self, query):
            return None

        def _parse_result(self, response):
            return None

    with pytest.raises(NotImplementedError):
        Fake1Connector().fetch("27 jul 1981", tzone="UTC")


def test_ConnectorABC_makequery_not_implementhed():
    class Fake2Connector(base.ConnectorABC):
        def get_endpoint(self):
            return None

        def _makequery(self, endpoint, pdate):
            return super()._makequery(endpoint, pdate)

        def _download(self, query):
            return None

        def _parse_result(self, response):
            return None

    with pytest.raises(NotImplementedError):
        Fake2Connector().fetch("27 jul 1981", tzone="UTC")


def test_ConnectorABC_download_not_implementhed():
    class Fake3Connector(base.ConnectorABC):
        def get_endpoint(self):
            return None

        def _makequery(self, endpoint, pdate):
            return None

        def _download(self, query):
            return super()._download(query)

        def _parse_result(self, response):
            return None

    with pytest.raises(NotImplementedError):
        Fake3Connector().fetch("27 jul 1981", tzone="UTC")


def test_ConnectorABC_parse_result_not_implementhed():
    class Fake4Connector(base.ConnectorABC):
        def get_endpoint(self):
            return None

        def _makequery(self, endpoint, pdate):
            return None

        def _download(self, query):
            return None

        def _parse_result(self, response):
            return super()._parse_result(response)

    with pytest.raises(NotImplementedError):
        Fake4Connector().fetch("27 jul 1981", tzone="UTC")


# --------------------------------------------------------------
# S3Mixin
# --------------------------------------------------------------


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
            conn.fetch("27 jul 1981", tzone="UTC")
    mglob.assert_called_once_with("1981-07-27T00:00:00+00:00")


# ---------------------------------------------------
# SFTPMixin
# ---------------------------------------------------


@mock.patch("paramiko.SSHClient.open_sftp")
@mock.patch("paramiko.SSHClient.connect")
@mock.patch("paramiko.RSAKey.from_private_key_file", return_value="pkey")
def test_SFTPMixin_download(from_private_key_file, connect, open_sftp):
    class TestSFTP(base.SFTPMixin, base.ConnectorABC):
        def get_endpoint(cls):
            return "endpoint"

        def _makequery(self, endpoint, pdate):
            return "dir/pattern.*"

        def _parse_result(self, response):
            return response

    conn = TestSFTP("host", "port", "zaraza@coso.com", keyfile="algo")

    from_private_key_file.assert_called_once_with("algo", password=None)
    connect.assert_called_once_with(
        "host", port="port", username="zaraza@coso.com", pkey="pkey"
    )

    # mock listdir
    listdir = open_sftp.return_value.__enter__.return_value.listdir
    listdir.return_value = ["pattern.ext"]

    get = open_sftp.return_value.__enter__.return_value.get
    get.return_value = "value"

    response = conn.fetch("27/07/1981", force=True)

    listdir.assert_called_once_with("dir")

    get.assert_called_once()
    get.call_args.kwargs["remotepath"] == "dir/pattern.ext"
    # localpath is a randomstring

    assert os.path.basename(response).startswith("stpy_cloudsat_")

    del conn  # to check coverage
