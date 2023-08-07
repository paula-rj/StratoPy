#!/usr/bin/env python
# -*- coding: utf-8 -*-
# License: MIT (https://tldrlegal.com/license/mit-license)
# Copyright (c) 2022, Paula Romero Jure et al.
# All rights reserved.
import numpy as np

import pytest

from stratopy import metadatatools
from stratopy.transformers import scalers

import xarray as xa

GOES_PATH = "tests/data/GOES16/\
OR_ABI-L2-CMIPF-M3C13_G16_s20190040600363_e20190040611141_c20190040611220.nc"

GOES_DS = xa.open_dataset(GOES_PATH, engine="h5netcdf")
GOES_DS_WITHATTRS = metadatatools.SatelliteData.from_values(
    GOES_DS,
    products_keys=("CMI",),
    instruments_types=(metadatatools.RADIOMETERS,),
    platforms=(metadatatools.GOES,),
    orbits_types=(metadatatools.GEOSTATIONARY,),
    times_starts=(0,),
    times_ends=(1,),
    notes=("a",),
)

FAKE_GOES_MULTI = xa.Dataset(
    data_vars=dict(
        ch1=(["ancho", "alto"], np.random.randint(0, 255, size=(10, 10))),
        ch2=(["ancho", "alto"], np.random.randint(0, 255, size=(10, 10))),
    ),
    coords=dict(
        ancho=("ancho", np.arange(1, 11, 1)),
        alto=("alto", np.arange(1, 11, 1)),
    ),
)

FAKE_IMG = np.random.randint(0, 255, size=(16, 3, 3))
FAKE_MULTI_DS = xa.Dataset(
    data_vars=dict(the_img=(["bands", "ancho", "alto"], FAKE_IMG)),
    coords=dict(
        bands=("bands", np.arange(1, 17, 1)),
        ancho=("ancho", np.arange(1, 4, 1)),
        alto=("alto", np.arange(1, 4, 1)),
    ),
)


def test_min_max_normalize_da():
    result = scalers.MinMaxNormalize().transform(sat0=GOES_DS_WITHATTRS)
    img_result = result.data.CMI.to_numpy()
    assert np.nanmax(img_result, axis=(2, 1), keepdims=True) < 1.1


def test_min_max_normalize_ds():
    FAKE_MULTI_DS_attrs = metadatatools.SatelliteData.from_values(
        data=FAKE_GOES_MULTI,
        orbits_types=(metadatatools.POLAR,),
        platforms=(metadatatools.CLOUDSAT,),
        instruments_types=(metadatatools.RADIOMETERS,),
        products_keys=(["ch1", "ch2"],),
        times_starts=(0,),
        times_ends=(1,),
    )
    result = scalers.MinMaxNormalize().transform(sat0=FAKE_MULTI_DS_attrs)
    img_result = result.data.to_array().to_numpy()
    assert np.max(img_result) < 1.1


def test_raise_err():
    FAKE_MULTI_DS_attrs = metadatatools.SatelliteData.from_values(
        data=FAKE_MULTI_DS,
        orbits_types=(metadatatools.POLAR,),
        platforms=(metadatatools.CLOUDSAT,),
        instruments_types=(metadatatools.RADARS,),
        products_keys=("the_img",),
        times_ends=(1,),
        times_starts=(0,),
    )
    with pytest.raises(ValueError):
        scalers.MinMaxNormalize().transform(sat0=FAKE_MULTI_DS_attrs)
