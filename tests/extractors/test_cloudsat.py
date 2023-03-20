#!/usr/bin/env python
# -*- coding: utf-8 -*-
# License: MIT (https://tldrlegal.com/license/mit-license)
# Copyright (c) 2022, Paula Romero Jure et al.
# All rights reserved.
import os

from unittest import mock

import pytest

import xarray as xa

from stratopy.extractors import cloudsat
import ipdb

CLOUDSAT_PATH = (
    "tests/data/CloudSat/"
    "2019002175851_67551_CS_2B-CLDCLASS_GRANULE_P1_R05_E08_F03.hdf"
)

DEFAULT_SSH_KEY = os.path.expanduser(
    os.path.join("tests/data", ".ssh", "id_rsa")
)


def test_read_hdf4():
    cs_dataset = cloudsat.read_hdf4(CLOUDSAT_PATH)
    assert isinstance(cs_dataset, xa.Dataset)


mock_client = mock.MagicMock()
mock_policy = mock.MagicMock()


@mock.patch("paramiko.SSHClient", mock_client)
@mock.patch("paramiko.AutoAddPolicy", mock_policy)
def test_wrong_product():
    with pytest.raises(ValueError):
        cloudsat.CloudSat(
            "wrong_prod", "fakeusr@gmail.edu", keyfile=DEFAULT_SSH_KEY
        )


@mock.patch("paramiko.SSHClient", mock_client)
@mock.patch("paramiko.AutoAddPolicy", mock_policy)
@pytest.mark.parametrize("ptype", cloudsat.CloudSat._PRODUCT_TYPES)
def test_repr(ptype):
    cs_obj = cloudsat.CloudSat(
        product_type=ptype,
        username="fakeusr@gmail.edu",
        keyfile=DEFAULT_SSH_KEY,
    )
    assert cs_obj.get_endpoint() == f"Data/{ptype}"
    expected = f"<CloudSat product_type={ptype!r}>"
    assert cs_obj.__repr__() == expected


ipdb.set_trace()


@mock.patch("paramiko.SSHClient", mock_client)
@mock.patch("paramiko.AutoAddPolicy", mock_policy)
def test_CloudSat_fetch(msftp, data_sftp, dataset_from_hdf):

    path = data_sftp(
        "CloudSat",
        "2019002175851_67551_CS_2B-CLDCLASS_GRANULE_P1_R05_E08_F03.hdf",
    )

    with mock.patch(
        "paramiko.SSHClient.open_sftp", return_value=path
    ) as mconn:
        result = cloudsat.CloudSat(
            product_type="2B-CLDCLASS.P1_R05",
            username="fakeusr@gmail.edu",
            keyfile=DEFAULT_SSH_KEY,
        ).fetch("25/jun/2010 18:00", tzone="UTC")

    msftp.assert_called_once_with(
        "Data/2B-CLDCLASS.P1_R05/2010/176/20101761800*"
    )

    expected = dataset_from_hdf(
        "CloudSat",
        "2019002175851_67551_CS_2B-CLDCLASS_GRANULE_P1_R05_E08_F03.hdf",
    )

    mconn.assert_awaited_once_with("fake/path/test", "rb")
    xa.testing.assert_allclose(result, expected)
