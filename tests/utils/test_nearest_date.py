#!/usr/bin/env python
# -*- coding: utf-8 -*-
# License: MIT (https://tldrlegal.com/license/mit-license)
# Copyright (c) 2022, Paula Romero Jure et al.
# All rights reserved.

# =============================================================================
# IMPORTS
# =============================================================================
import dateutil

import numpy as np
import numpy.ma as ma

import pytest

from stratopy.utils import util_funcs


DATE = dateutil.parser.parse("2019 jan 09 16:00")

fake_files_list = [
    "2019009155049_67652_CS_2B-CLDCLASS_GRANULE_P1_R05_E08_F03.hdf",
    "2019009150042_67652_CS_2B-CLDCLASS_GRANULE_P1_R05_E08_F03.hdf",
    "2019009161802_67652_CS_2B-CLDCLASS_GRANULE_P1_R05_E08_F03.hdf",
]


def test_closest_datetime():
    pattern_to_search = DATE.strftime("%Y%j%H%M")
    tested = util_funcs.closest_datetime(fake_files_list, pattern_to_search)
    assert tested == 0


arr = np.array([35786023.0, -0.0, 0.0])
MASKED_SAT = arr.view(ma.MaskedArray)


def test_scan2sat():
    np.testing.assert_equal(MASKED_SAT, util_funcs.scan2sat(0.0, 0.0))


def test_sat2latlon():
    sx, sy, sz = util_funcs.scan2sat(0.0, 0.0)
    np.testing.assert_equal((0.0, -75.0), util_funcs.sat2latlon(sx, sy, sz))


def test_latlon2scan():
    np.testing.assert_equal((0.0, 0.0), util_funcs.latlon2scan(0.0, -75.0))


def test_colfil2scan():
    np.testing.assert_equal(
        (-0.151844, 0.151844), util_funcs.colfil2scan(0.0, 0.0)
    )


def test_scan2colfil():
    col_int, row_int = util_funcs.scan2colfil(0.0, 0.0, tipo=1)
    assert isinstance(col_int, np.int64)
    assert isinstance(row_int, np.int64)
    col_fl, row_fl = util_funcs.scan2colfil(0.0, 0.0, tipo=0)
    assert isinstance(col_fl, float)
    assert isinstance(row_fl, float)
    np.testing.assert_equal((2712, 2712), util_funcs.scan2colfil(0.0, 0.0))
    with pytest.raises(TypeError):
        util_funcs.scan2colfil(0.0, 0.0, tipo=2)
