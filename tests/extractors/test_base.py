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


# ------------------------------
# S3Mixin
# ------------------------------


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


# -----------------------------------------------
# SFTPMixin
# -----------------------------------------------
DEFAULT_SSH_KEY = os.path.expanduser(
    os.path.join("tests/data", ".ssh", "id_rsa")
)


def test_SFTPMixin_FileNotFoundError():
    class TestFileNotFoundError(base.SFTPMixin, base.ConnectorABC):
        def get_endpoint(cls):
            return None

        def _makequery(self, endpoint, pdate):
            return pdate.isoformat()

        def _parse_result(self, response):
            return None

        mock_client = mock.MagicMock()
        mock_policy = mock.MagicMock()

        @mock.patch("paramiko.SSHClient", mock_client)
        @mock.patch("paramiko.AutoAddPolicy", mock_policy)
        def mock_connection(mock_client, mock_pol):
            mock_client.set_missing_host_key_policy(mock_pol)

    conn = TestFileNotFoundError(
        "www.cloudsat.cira.colostate.edu",
        22,
        "pepito@mimail.com",
        keyfile=DEFAULT_SSH_KEY,
    )

    with mock.patch("paramiko.SSHClient.open_sftp", return_value=[]) as conn:
        with pytest.raises(FileNotFoundError):
            conn.fetch("27 jul 1981", tzone="UTC")
    conn.assert_called_once_with("1981-07-27T00:00:00+00:00")
