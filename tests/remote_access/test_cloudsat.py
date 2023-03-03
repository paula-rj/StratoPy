#!/usr/bin/env python
# -*- coding: utf-8 -*-
# License: MIT (https://tldrlegal.com/license/mit-license)
# Copyright (c) 2022, Paula Romero Jure et al.
# All rights reserved.
from unittest import mock

import pytest

from stratopy.remote_access import cloudsat


@mock.patch("paramiko.SSHClient.connect", return_value=None)
def test_CloudSat_conn(mock_conn):
    for prod_type in cloudsat.CloudSatextractor._PRODUCT_TYPES:
        cs_obj = cloudsat.CloudSatextractor(
            product_type=prod_type,
            username="fakeusr@gmail.edu",
            keypass="2022",
        )
        assert cs_obj.get_endpoint() == f"Data/{prod_type}"
        expected = f"<CloudSat product_type={prod_type!r}>"
        assert cs_obj.__repr__() == expected


@mock.patch("paramiko.SSHClient.connect", return_value=None)
def test_wrong_product(mock_conn):
    with pytest.raises(ValueError):
        cloudsat.CloudSatextractor("holis", "fakeusr@gmail.edu", keypass="2022")


@mock.patch("paramiko.SSHClient.connect", return_value=None)
@mock.patch("paramiko.RSAKey.from_private_key_file")
def test_CloudSat_obj(mock_conn, mock_keys):
    cs_obj = cloudsat.CloudSatextractor(
        "2B-CLDCLASS.P1_R05", "fakeusr@gmail.edu", keypass="1234"
    )
    assert cs_obj.__repr__() == "<CloudSat product_type='2B-CLDCLASS.P1_R05'>"


@mock.patch("paramiko.SSHClient.connect", return_value=None)
def test_Cloudsat_fetch(mconn, data_bytes, dataset):
    buff = data_bytes(
        "CloudSat",
        "2019002175851_67551_CS_2B-CLDCLASS_GRANULE_P1_R05_E08_F03.hdf",  # noqa
    )

    with mock.patch(
        "paramiko.SSHClient.open_sftp", return_value=buff
    ) as mopen:
        cs_obj = cloudsat.CloudSatextractor(
            "2B-CLDCLASS.P1_R05", "fakeusr@gmail.edu", keypass="2022"
        )
        result = cs_obj.fetch("25/jun/2010", tzone="UTC")
