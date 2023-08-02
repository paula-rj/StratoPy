#!/usr/bin/env python
# -*- coding: utf-8 -*-
# License: MIT (https://tldrlegal.com/license/mit-license)
# Copyright (c) 2022, Paula Romero Jure et al.
# All rights reserved.
from unittest import mock

import pytest

from stratopy import metadatatools
from stratopy.extractors import goes

import xarray as xa

FAKE_AVAILS_LIST = [
    "noaa-goes16/ABI-L1b-RadF/2010/176/00/OR_ABI-L1b-RadF-M3C03_G16_s20101760045364_e20190010126142_c20190010126218.nc",  # noqa
    "noaa-goes16/ABI-L1b-RadF/2010/176/00/OR_ABI-L1b-RadF-M3C16_G16_s20101760015363_e20190010141142_c20190010141219.nc",  # noqa
    "noaa-goes16/ABI-L1b-RadF/2010/176/00/OR_ABI-L1b-RadF-M3C03_G16_s20101760000363_e20190040611130_c20190040611199.nc",  # noqa
]

FAKE_AVAILS_LIST_noCH = [
    "noaa-goes16/ABI-L2-ACHTF/2010/176/00/OR_ABI-L2-ACHTF-M3_G16_s20101760045364_e20190010126142_c20190010126218.nc",  # noqa
    "noaa-goes16/ABI-L2-ACHTF/2010/176/00/OR_ABI-L2-ACHTF-M3_G16_s20101760015363_e20190010141142_c20190010141219.nc",  # noqa
    "noaa-goes16/ABI-L2-ACHTF/2010/176/00/OR_ABI-L2-ACHTF-M3_G16_s20101760000363_e20190040611130_c20190040611199.nc",  # noqa
]

PROD_TYPES_LIST = [
    "ABI-L1b-RadF",
    "ABI-L2-CMIPF",
    "ABI-L2-ACHA2KMF",
    "ABI-L2-ACHAF",
    "ABI-L2-ACHTF",
    "ABI-L2-ACMF",
    "ABI-L2-ADPF",
    "ABI-L2-AODF",
    "ABI-L2-BRFF",
    "ABI-L2-CODF",
    "ABI-L2-CPSF",
    "ABI-L2-CTPF",
    "ABI-L2-MCMIPF",
]


@pytest.mark.parametrize("ptype", goes.GOES16._PRODUCT_TYPES_PARSERS)
def test_GOES_get_endpoint(ptype):
    goes_obj = goes.GOES16(ptype, channel=13)
    assert goes_obj.get_endpoint() == f"s3://noaa-goes16/{ptype}"


def test_wrong_product():
    with pytest.raises(ValueError):
        goes.GOES16("holis", channel=13)


@pytest.mark.parametrize("prod_type", goes.GOES16._PRODUCT_TYPES_PARSERS)
def test_repr(prod_type):
    goes_obj = goes.GOES16(prod_type, channel=13)
    if prod_type in PROD_TYPES_LIST[2:]:
        expected = f"<GOES16 product_type={prod_type!r}, ch=None>"
        assert repr(goes_obj) == expected
    else:
        expected = f"<GOES16 product_type={prod_type!r}, ch=13>"
        assert repr(goes_obj) == expected


# tests with channel
@mock.patch("s3fs.S3FileSystem.glob", return_value=FAKE_AVAILS_LIST)
def test_GOES16_fetch_ch(mglob, data_bytes, dataset):
    buff = data_bytes(
        "GOES16",
        "OR_ABI-L2-CMIPF-M3C03_G16_s20190040600363_e20190040611130_c20190040611199.nc",  # noqa
    )

    with mock.patch("s3fs.S3FileSystem.open", return_value=buff) as mopen:
        result = goes.GOES16("ABI-L1b-RadF", 3).fetch(
            "25/jun/2010 00:02", tzone="UTC"
        )

    # Llama al directory donde estan todos los archivos, para comparar fechas
    mglob.assert_called_once_with(
        "s3://noaa-goes16/ABI-L1b-RadF/2010/176/00/OR_ABI-L1b-RadF-M3C03_G16*"
    )

    expected = dataset(
        "GOES16",
        "OR_ABI-L2-CMIPF-M3C03_G16_s20190040600363_e20190040611130_c20190040611199.nc",  # noqa
        "h5netcdf",
    )
    mopen.assert_called_once_with(
        "noaa-goes16/ABI-L1b-RadF/2010/176/00/OR_ABI-L1b-RadF-M3C03_G16_s20101760000363_e20190040611130_c20190040611199.nc",  # noqa
        "rb",
    )
    xa.testing.assert_allclose(result.data, expected)

    assert isinstance(result, metadatatools.SatelliteData)
    assert isinstance(result.data, xa.Dataset)  # new
    assert buff.closed


# tests without channel
@mock.patch("s3fs.S3FileSystem.glob", return_value=FAKE_AVAILS_LIST_noCH)
def test_GOES16_fetch_noch(mglob, data_bytes, dataset):
    buff = data_bytes(
        "GOES16",
        "OR_ABI-L2-ACHTF-M6_G16_s20200091200211_e20200091209519_c20200091211458.nc",  # noqa
    )

    with mock.patch("s3fs.S3FileSystem.open", return_value=buff) as mopen:
        result = goes.GOES16("ABI-L2-ACHTF", 3).fetch(
            "25/jun/2010 00:02", tzone="UTC"
        )

    # Llama al directory donde estan todos los archivos, para comparar fechas
    mglob.assert_called_once_with(
        "s3://noaa-goes16/ABI-L2-ACHTF/2010/176/00/OR_ABI-L2-ACHTF-M3_G16*"
    )

    expected = dataset(
        "GOES16",
        "OR_ABI-L2-ACHTF-M6_G16_s20200091200211_e20200091209519_c20200091211458.nc",  # noqa
        "h5netcdf",
    )
    mopen.assert_called_once_with(
        "noaa-goes16/ABI-L2-ACHTF/2010/176/00/OR_ABI-L2-ACHTF-M3_G16_s20101760000363_e20190040611130_c20190040611199.nc",  # noqa
        "rb",
    )

    xa.testing.assert_allclose(result.data, expected)

    assert isinstance(result, metadatatools.SatelliteData)
    assert isinstance(result.data, xa.Dataset)  # new
    assert buff.closed
