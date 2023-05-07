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

CSAT_PATH = (
    "tests/data/CloudSat/"
    "2019002175851_67551_CS_2B-CLDCLASS_GRANULE_P1_R05_E08_F03.hdf"
)

FAKE_GOES = np.random.randn(5424, 5424)


def test_larger_img():
    cols_wrong = np.array([11234, 11235])
    rows_wrong = np.array([11234, 11235])
    cols_ok = np.array([5000, 5000])
    rows_ok = np.array([5000, 5000])
    with pytest.raises(ValueError):
        transform.gen_vect(cols_wrong, rows_ok, FAKE_GOES)
    with pytest.raises(ValueError):
        transform.gen_vect(rows_wrong, cols_ok, FAKE_GOES)


# Raise error if time selected out of range for csat track
def test_time_out():
    csat_data = cloudsat.read_hdf4(CSAT_PATH)
    with pytest.raises(base.NothingHereError):
        transform.merge(
            csat_data=csat_data,
            time_selected="2019 jan 2 17:00",
            prod_type="any",
            ch=13,
        )


def test_transform():
    pass
