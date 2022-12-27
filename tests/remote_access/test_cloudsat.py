#!/usr/bin/env python
# -*- coding: utf-8 -*-
# License: MIT (https://tldrlegal.com/license/mit-license)
# Copyright (c) 2022, Paula Romero Jure et al.
# All rights reserved.
from unittest import mock

import pytest

from stratopy.remote_access import cloudsat


@pytest.mark.parametrize("prod_type", cloudsat.CloudSat._PRODUCT_TYPES)
def test_CloudSat_get_endpoint(prod_type):
    cs_obj = cloudsat.CloudSat(
        product_type=prod_type,
        username="paula.romero@mi.unc.edu.ar",
        keypass="2022",
    )
    assert cs_obj.get_endpoint() == f"Data/{prod_type}"


def test_wrong_product():
    with pytest.raises(ValueError):
        cloudsat.CloudSat("holis")


@pytest.mark.parametrize("prod_type", cloudsat.CloudSat._PRODUCT_TYPES)
def test_repr(prod_type):
    cs_obj = cloudsat.CloudSat(prod_type)
    expected = f"<GOES16 product_type={prod_type!r}>"
    assert repr(cs_obj) == expected


@mock.patch("paramiko.SSHClient.connect", return_value=None)
def test_CloudSat_fetch():
    ...
