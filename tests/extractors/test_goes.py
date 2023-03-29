#!/usr/bin/env python
# -*- coding: utf-8 -*-
# License: MIT (https://tldrlegal.com/license/mit-license)
# Copyright (c) 2022, Paula Romero Jure et al.
# All rights reserved.
from unittest import mock

import pytest

from stratopy.extractors import goes

import xarray as xa


@pytest.mark.parametrize("ptype", goes.GOES16._PRODUCT_TYPES_PARSERS)
def test_GOES_get_endpoint(ptype):
    goes_obj = goes.GOES16(ptype)
    assert goes_obj.get_endpoint() == f"s3://noaa-goes16/{ptype}"


def test_wrong_product():
    with pytest.raises(ValueError):
        goes.GOES16("holis")


@pytest.mark.parametrize("prod_type", goes.GOES16._PRODUCT_TYPES_PARSERS)
def test_repr(prod_type):
    goes_obj = goes.GOES16(prod_type)
    expected = f"<GOES16 product_type={prod_type!r}>"
    assert repr(goes_obj) == expected


# tests with channel
@mock.patch("s3fs.S3FileSystem.glob", return_value=["fake/path/test"])
def test_GOES16_fetch_ch(mglob, data_bytes, dataset):
    # noqa
    buff = data_bytes(
        "GOES16",
        "OR_ABI-L2-CMIPF-M3C03_G16_s20190040600363_e20190040611130_c20190040611199.nc",  # noqa
    )

    with mock.patch("s3fs.S3FileSystem.open", return_value=buff) as mopen:
        result = goes.GOES16("ABI-L1b-RadF").fetch("25/jun/2010", tzone="UTC")

    mglob.assert_called_once_with(
        "s3://noaa-goes16/ABI-L1b-RadF/2010/176/00/OR_ABI-L1b-RadF-M3C03_G16_s20101760000*"  # noqa
    )

    expected = dataset(
        "GOES16",
        "OR_ABI-L2-CMIPF-M3C03_G16_s20190040600363_e20190040611130_c20190040611199.nc",  # noqa
        "h5netcdf",
    )
    mopen.assert_called_once_with("fake/path/test", "rb")
    xa.testing.assert_allclose(result, expected)

    assert isinstance(result, xa.Dataset)  # new
    assert buff.closed


# tests without channel
@mock.patch("s3fs.S3FileSystem.glob", return_value=["fake/path/test"])
def test_GOES16_fetch_noch(mglob, data_bytes, dataset):
    # noqa
    buff = data_bytes(
        "GOES16",
        "OR_ABI-L2-ACHTF-M6_G16_s20200091200211_e20200091209519_c20200091211458.nc",  # noqa
    )

    with mock.patch("s3fs.S3FileSystem.open", return_value=buff) as mopen:
        result = goes.GOES16("ABI-L2-ACHTF").fetch("25/jun/2010", tzone="UTC")

    mglob.assert_called_once_with(
        "s3://noaa-goes16/ABI-L2-ACHTF/2010/176/00/OR_ABI-L2-ACHTF-M3_G16_s20101760000*"  # noqa
    )

    expected = dataset(
        "GOES16",
        "OR_ABI-L2-ACHTF-M6_G16_s20200091200211_e20200091209519_c20200091211458.nc",  # noqa
        "h5netcdf",
    )
    mopen.assert_called_once_with("fake/path/test", "rb")

    xa.testing.assert_allclose(result, expected)

    assert isinstance(result, xa.Dataset)  # new
    assert buff.closed