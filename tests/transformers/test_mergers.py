#!/usr/bin/env python
# -*- coding: utf-8 -*-
# License: MIT (https://tldrlegal.com/license/mit-license)
# Copyright (c) 2022, Paula Romero Jure et al.
# All rights reserved.
import numpy as np

import pytest

from stratopy import metadatatools
from stratopy.extractors import cloudsat
from stratopy.extractors import ebase
from stratopy.transformers import mergers, scalers

import xarray as xa

# pytest.skip(allow_module_level=True)
cldsat = cloudsat.read_as_SatelliteData(
    "tests/data/CloudSat/"
    "2019002175851_67551_CS_2B-CLDCLASS_GRANULE_P1_R05_E08_F03.hdf",
    product="2B-CLDCLASS.P1_R05"
)
GOES_PATH = (
    "tests/data/GOES16/"
    "OR_ABI-L2-CMIPF-M3C13_G16_s20190040600363_e20190040611141_c20190040611220.nc"  # noqa
)

csat_data = cldsat

GOES_DS = xa.open_dataset(GOES_PATH, engine="h5netcdf")

FAKE_GOES = np.random.randn(5424, 5424)
FAKE_GOES_MULTI = np.random.randn(1, 5424, 5424)
FAKE_DS = xa.Dataset(
    data_vars=dict(CMI=(["ancho", "alto"], FAKE_GOES)),
    coords=dict(
        ancho=("ancho", np.arange(5424)),
        alto=("alto", np.arange(5424)),
    ),
)


def test_larger_img():
    wrong = 11234
    ok = 5000
    with pytest.raises(ValueError):
        mergers.gen_vect(wrong, ok, FAKE_GOES, (3, 3))
    with pytest.raises(ValueError):
        mergers.gen_vect(wrong, ok, FAKE_GOES, (3, 3))


# Raise error if time selected out of range for csat track
def test_check_time():
    mobj = mergers.MergePolarGeos("2019 jan 2 18:30")
    assert mobj.check_time(csat_data) == True  # noqa


def test_wrong_check_time():
    merged_obj = mergers.MergePolarGeos("2019 jan 2 22:30")
    with pytest.raises(ebase.NothingHereError):
        merged_obj.check_time(csat_data)


def test_gen_vect():
    result_impar = mergers.gen_vect(2500, 2500, FAKE_GOES, (3, 3))
    result_par = mergers.gen_vect(2500, 2500, FAKE_GOES, (6, 6))
    multi_impar = mergers.gen_vect(2500, 2500, FAKE_GOES_MULTI, (3, 3))
    multi_par = mergers.gen_vect(2500, 2500, FAKE_GOES_MULTI, (7, 7))
    assert result_impar.shape == (3, 3)
    assert result_par.shape == (7, 7)
    assert multi_impar.shape == (1, 3, 3)
    assert multi_par.shape == (1, 7, 7)


def test_gen_vec_larger():
    with pytest.raises(ValueError):
        mergers.gen_vect(6000, 6000, FAKE_GOES, (3, 3))


def test_wrong_orbit():
    GOES_DS_WITHATRRS = metadatatools.SatelliteData.from_values(
        FAKE_DS,
        orbits_types=metadatatools.POLAR,
        platforms=metadatatools.GOES,
        instruments_types=metadatatools.RADIOMETERS,
        products_keys="CMI",
        times_starts=0, times_ends=1
    )
    mobj = mergers.MergePolarGeos("2019 jan 2 18:25")
    with pytest.raises(ValueError):
        mobj.transform(csat_data, GOES_DS_WITHATRRS)


def test_get_image():
    GOES_DS_WITHATRRS = metadatatools.SatelliteData.from_values(
        FAKE_DS,
        orbits_types=metadatatools.GEOSTATIONARY,
        platforms=metadatatools.GOES,
        instruments_types=metadatatools.RADARS,
        products_keys="CMI",
        times_starts=0, times_ends=1
    )
    mobj = mergers.MergePolarGeos("2019 jan 2 18:25")
    with pytest.raises(ValueError):
        mobj.get_image(GOES_DS_WITHATRRS)


def test_transform():

    GOES_DS_WITHATRRS = metadatatools.SatelliteData.from_values(
        GOES_DS,
        orbits_types=metadatatools.GEOSTATIONARY,
        platforms=metadatatools.GOES,
        instruments_types=metadatatools.RADIOMETERS,
        products_keys="CMI",
        times_starts=0, times_ends=1
    )

    goesnorm = scalers.MinMaxNormalize().transform(GOES_DS_WITHATRRS)

    mobj = mergers.MergePolarGeos("2019 jan 2 18:30")
    result1 = mobj.transform(csat_data, goesnorm)
    result2 = mobj.transform(goesnorm, csat_data)
    # Check trace dim
    assert isinstance(result1, xa.Dataset)
    assert isinstance(result2, xa.Dataset)
