#!/usr/bin/env python
# -*- coding: utf-8 -*-
# License: MIT (https://tldrlegal.com/license/mit-license)
# Copyright (c) 2022, Paula Romero Jure et al.
# All rights reserved.
import numpy as np

import pytest

from stratopy.transformers import scalers
from stratopy import metadatatools

import xarray as xa

FAKE_IMG = np.random.randint(0, 255, size=(16, 3, 3))
FAKE_DS = xa.Dataset(
    data_vars=dict(the_img=(["bands", "ancho", "alto"], FAKE_IMG)),
    coords=dict(
        bands=("bands", np.arange(1, 17, 1)),
        ancho=("ancho", np.arange(1, 4, 1)),
        alto=("alto", np.arange(1, 4, 1)),
    ),
)
FAKE_DS_WITHATTRS = metadatatools.add_metadata(
    FAKE_DS,
    orbit_type=metadatatools.POLAR,
    platform=metadatatools.CLOUDSAT,
    instrument_type=metadatatools.RADIOMETERS,
    product_key="the_img",
)

FAKE_DS_radar = metadatatools.add_metadata(
    FAKE_DS,
    orbit_type=metadatatools.POLAR,
    platform=metadatatools.CLOUDSAT,
    instrument_type=metadatatools.RADARS,
    product_key="the_img",
)


def test_raise_err():
    with pytest.raises(ValueError):
        result0 = scalers.MinMaxNormalize().transformer(sat0=FAKE_DS_radar)


def test_min_max_normalize():
    result = scalers.MinMaxNormalize().transformer(sat0=FAKE_DS_WITHATTRS)
    np.testing.assert_array_less(result, 1.1)
