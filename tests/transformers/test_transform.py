#!/usr/bin/env python
# -*- coding: utf-8 -*-
# License: MIT (https://tldrlegal.com/license/mit-license)
# Copyright (c) 2022, Paula Romero Jure et al.
# All rights reserved.
import numpy as np

import pytest

from stratopy.extractors import base
from stratopy.extractors import cloudsat
from stratopy.transformers import transform

import xarray as xa

CSAT_PATH = (
    "tests/data/CloudSat/"
    "2019002175851_67551_CS_2B-CLDCLASS_GRANULE_P1_R05_E08_F03.hdf"
)

GOES_PATH = (
    "tests/data/GOES16/",
    "OR_ABI-L2-CMIPF-M3C03_G16_s20190040600363_e20190040611130_c20190040611199.nc",  # noqa
)

FAKE_GOES = np.random.randn(5424, 5424)


def test_larger_img():
    wrong = 11234
    ok = 5000
    with pytest.raises(ValueError):
        transform.gen_vect(wrong, ok, FAKE_GOES, (3, 3))
    with pytest.raises(ValueError):
        transform.gen_vect(wrong, ok, FAKE_GOES, (3, 3))


# Raise error if time selected out of range for csat track
def test_time_out():
    csat_data = cloudsat.read_hdf4(CSAT_PATH)
    with pytest.raises(base.NothingHereError):
        transform.merge(
            csat_data=csat_data,
            time_selected="2019 jan 2 17:00",
            goes_prod_type="any",
            band=13,
        )


def test_gen_vect():
    iexpected_shape = (3, 3)
    pexpected_shape = (7, 7)
    result_impar = transform.gen_vect(2500, 2500, FAKE_GOES, (3, 3))
    result_par = transform.gen_vect(2500, 2500, FAKE_GOES, (6, 6))
    assert result_impar.shape == iexpected_shape
    assert result_par.shape == pexpected_shape


def test_transform():
    cldsat = cloudsat.read_hdf4(CSAT_PATH)
    result = transform.merge(
        cldsat,
        time_selected="2019 jan 2 18:30",
        goes_prod_type="ABI-L2-CMIPF",
        band=9,
    )
    # Check trace dim
    assert isinstance(result, xa.Dataset)
