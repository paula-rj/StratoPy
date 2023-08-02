#!/usr/bin/env python
# -*- coding: utf-8 -*-
# License: MIT (https://tldrlegal.com/license/mit-license)
# Copyright (c) 2022, Paula Romero Jure et al.
# All rights reserved.
import os
from unittest import mock

import pytest

from stratopy.extractors import cloudsat

import xarray as xa


CLOUDSAT_PATH = (
    "tests/data/CloudSat/"
    "2019002175851_67551_CS_2B-CLDCLASS_GRANULE_P1_R05_E08_F03.hdf"
)

FAKE_FILE_LIST = [
    "2010176155049_67652_CS_2B-CLDCLASS_GRANULE_P1_R05_E08_F03.hdf",
    "2010176150042_67652_CS_2B-CLDCLASS_GRANULE_P1_R05_E08_F03.hdf",
    "2010176180002_67652_CS_2B-CLDCLASS_GRANULE_P1_R05_E08_F03.hdf",
]


@mock.patch("paramiko.SSHClient.connect")
@mock.patch("paramiko.RSAKey.from_private_key_file", return_value="pkey")
def test_wrong_product(from_private_key_file, connect):
    with pytest.raises(ValueError):
        cloudsat.CloudSat(
            "wrong_prod", "fakeusr@gmail.edu", keyfile="fake_file"
        )
    connect.assert_called


@mock.patch("paramiko.SSHClient.connect")
@mock.patch("paramiko.RSAKey.from_private_key_file", return_value="pkey")
@pytest.mark.parametrize("ptype", cloudsat.CloudSat._PRODUCT_TYPES)
def test_repr(connect, from_private_key_file, ptype):
    cs_obj = cloudsat.CloudSat(
        product_type=ptype,
        username="fakeusr@gmail.edu",
        keyfile="some_file",
    )
    # test repr ok for all types of products
    assert repr(cs_obj) == f"<CloudSat product_type={ptype!r}>"
    # Test get endpoint (store directory ok)
    assert cs_obj.get_endpoint() == f"Data/{ptype}"


# Test make query ok
# Test parse_product ok
@mock.patch("paramiko.SSHClient.open_sftp")
@mock.patch("paramiko.SSHClient.connect")
@mock.patch("paramiko.RSAKey.from_private_key_file", return_value="pkey")
def test_download(from_private_key_file, connect, open_sftp):
    cs_obj = cloudsat.CloudSat(
        product_type="2B-CLDCLASS.P1_R05",
        username="fakeusr@gmail.edu",
        keyfile="some_file",
    )

    # Test make query
    dt = cs_obj.parse_date("25/jun/2010 18:00", time_zone="UTC")
    mq = cs_obj._makequery(cs_obj.get_endpoint(), dt)
    assert mq == "Data/2B-CLDCLASS.P1_R05/2010/176/2010176180000"

    # tests read_hdf4()
    expected = cloudsat.read_as_SatelliteData(CLOUDSAT_PATH,"2B-CLDCLASS.P1_R05" ).data
    result = cs_obj._parse_result(CLOUDSAT_PATH)
    
    import ipdb; ipdb.set_trace()
    assert isinstance(expected, xa.Dataset)
    xa.testing.assert_equal(expected, result)

    # mock listdir
    listdir = open_sftp.return_value.__enter__.return_value.listdir
    listdir.return_value = FAKE_FILE_LIST

    get = open_sftp.return_value.__enter__.return_value.get
    get.return_value = "value"

    response = cs_obj._download(mq)

    listdir.assert_called_once_with("Data/2B-CLDCLASS.P1_R05/2010/176")

    get.assert_called_once()
    get.call_args.kwargs[
        "remotepath"
    ] == f"Data/2B-CLDCLASS.P1_R05/2010/176/{CLOUDSAT_PATH[20:31]}"
    # localpath is a randomstring

    assert os.path.basename(response).startswith("stpy_CloudSat_")
