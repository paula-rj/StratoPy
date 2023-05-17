#!/usr/bin/env python
# -*- coding: utf-8 -*-
# License: MIT (https://tldrlegal.com/license/mit-license)
# Copyright (c) 2022, Paula Romero Jure et al.
# All rights reserved.
import numpy as np

import pytest

from stratopy.extractors import cloudsat
from stratopy.extractors import ebase
from stratopy.transformers import mergers

import xarray as xa

pytest.skip(allow_module_level=True)

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
        mergers.gen_vect(wrong, ok, FAKE_GOES, (3, 3))
    with pytest.raises(ValueError):
        mergers.gen_vect(wrong, ok, FAKE_GOES, (3, 3))


# Raise error if time selected out of range for csat track
def test_time_out():
    csat_data = cloudsat.read_hdf4(CSAT_PATH)
    with pytest.raises(ebase.NothingHereError):
        mergers.merge(
            csat_obj=csat_data,
            time_selected="2019 jan 2 17:00",
            goes_obj="any",
            band=13,
        )


def test_gen_vect():
    iexpected_shape = (3, 3)
    pexpected_shape = (7, 7)
    result_impar = mergers.gen_vect(2500, 2500, FAKE_GOES, (3, 3))
    result_par = mergers.gen_vect(2500, 2500, FAKE_GOES, (6, 6))
    assert result_impar.shape == iexpected_shape
    assert result_par.shape == pexpected_shape


def test_wrong_check_time():
    sat0_data = cloudsat.read_hdf4(CSAT_PATH)
    merged_obj = mergers.Merge_Cloudsat_GOES("2019 jan 2 22:30")
    with pytest.raises(ebase.NothingHereError):
        merged_obj.check_time(sat0_data)


def test_transform():
    cldsat = cloudsat.read_hdf4(CSAT_PATH)
    result = mergers.merge(
        cldsat,
        time_selected="2019 jan 2 18:30",
        goes_obj="ABI-L2-CMIPF",
        band=9,
    )
    # Check trace dim
    assert isinstance(result, xa.Dataset)
