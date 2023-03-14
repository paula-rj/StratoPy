#!/usr/bin/env python
# -*- coding: utf-8 -*-
# License: MIT (https://tldrlegal.com/license/mit-license)
# Copyright (c) 2022, Paula Romero Jure et al.
# All rights reserved.
from unittest import mock

import pytest

from stratopy.extractors import cloudsat


@mock.patch("paramiko.SSHClient.connect", return_value=None)
def test_wrong_product(mock_conn):
    with pytest.raises(ValueError):
        cloudsat.CloudSat("holis", "fakeusr@gmail.edu", keypass="1234")


@mock.patch("paramiko.SSHClient.connect", return_value=None)
def test_CloudSat_fetch(mock_conn):
    local_temp_path = mock_conn(
        "CloudSat",
        "2019002175851_67551_CS_2B-CLDCLASS_GRANULE_P1_R05_E08_F03.hdf",
    )

    with mock.patch(
        "paramiko.SFTPClient.get", return_value=local_temp_path
    ) as mconn:
        cs_obj = cloudsat.CloudSat(
            "2B-CLDCLASS.P1_R05", "fakeusr@gmail.edu", keypass="1234"
        )
        result = cs_obj.fetch("25/jun/2010", tzone="UTC")

        mconn.assert_called_once_with("2010/06/2010176*")

        expected = f"<CloudSat product_type={result!r}>"
        assert cs_obj.__repr__() == expected

    #    for prod_type in cloudsat.CloudSat._PRODUCT_TYPES:
    #        cs_obj = cloudsat.CloudSat(
    #            product_type=prod_type,
    #            username="fakeusr@gmail.edu",
    #            keypass="1234",
    #        )
    #        assert cs_obj.get_endpoint() == f"Data/{prod_type}"
    #        expected = f"<CloudSat product_type={prod_type!r}>"
    #        assert cs_obj.__repr__() == expected
