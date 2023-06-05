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

FAKE_IMG = np.random.randint(0, 255, size=(16, 3, 3))
FAKE_DS = xa.Dataset(
    data_vars=dict(the_img=(["bands", "ancho", "alto"], FAKE_IMG)),
    coords=dict(
        bands=("bands", np.arange(1, 17, 1)),
        ancho=("ancho", np.arange(1, 4, 1)),
        alto=("alto", np.arange(1, 4, 1)),
    ),
)


def test_min_max_normalize_ds():
    FAKE_DS_WITHATTRS = metadatatools.add_metadata(
        FAKE_DS,
        orbit_type=metadatatools.POLAR,
        platform=metadatatools.CLOUDSAT,
        instrument_type=metadatatools.RADIOMETERS,
        product_key="the_img",
    )
    result = scalers.MinMaxNormalize().transform(sat0=FAKE_DS_WITHATTRS)
    img_result = result.the_img.to_numpy()
    np.testing.assert_array_less(img_result, 1.1)


def test_min_max_normalize_da():
    FAKE_DA_WITHATTRS = metadatatools.add_metadata(
        FAKE_DS,
        orbit_type=metadatatools.POLAR,
        platform=metadatatools.CLOUDSAT,
        instrument_type=metadatatools.RADIOMETERS,
        product_key="the_img",
    ).to_array()
    result = scalers.MinMaxNormalize().transform(sat0=FAKE_DA_WITHATTRS)
    img_result = result.the_img.to_numpy()
    np.testing.assert_array_less(img_result, 1.1)


def test_raise_err():
    FAKE_DS_radar = metadatatools.add_metadata(
        FAKE_DS,
        orbit_type=metadatatools.POLAR,
        platform=metadatatools.CLOUDSAT,
        instrument_type=metadatatools.RADARS,
        product_key="the_img",
    )
    with pytest.raises(ValueError):
        scalers.MinMaxNormalize().transform(sat0=FAKE_DS_radar)
