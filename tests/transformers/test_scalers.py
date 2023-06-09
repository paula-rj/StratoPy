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
    GOES_DS_WITHATTRS = metadatatools.add_metadata(
        GOES_DS,
        orbit_type=metadatatools.GEOSTATIONARY,
        platform=metadatatools.CLOUDSAT,
        instrument_type=metadatatools.RADIOMETERS,
        product_key="CMI",
    )
    result = scalers.MinMaxNormalize().transform(sat0=GOES_DS_WITHATTRS)
    img_result = result.CMI.to_numpy()
    assert np.nanmax(img_result, axis=(2, 1), keepdims=True) < 1.1


def test_min_max_normalize_ds():
    FAKE_MULTI_DS_attrs = metadatatools.add_metadata(
        FAKE_GOES_MULTI,
        orbit_type=metadatatools.POLAR,
        platform=metadatatools.CLOUDSAT,
        instrument_type=metadatatools.RADIOMETERS,
        product_key=["ch1", "ch2"],
    )
    result = scalers.MinMaxNormalize().transform(sat0=FAKE_MULTI_DS_attrs)
    img_result = result.to_array().to_numpy()
    assert np.max(img_result) < 1.1


def test_raise_err():
    FAKE_MULTI_DS_attrs = metadatatools.add_metadata(
        FAKE_MULTI_DS,
        orbit_type=metadatatools.POLAR,
        platform=metadatatools.CLOUDSAT,
        instrument_type=metadatatools.RADARS,
        product_key="the_img",
    )
    with pytest.raises(ValueError):
        scalers.MinMaxNormalize().transform(sat0=FAKE_MULTI_DS_attrs)
