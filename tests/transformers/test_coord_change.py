#!/usr/bin/env python
# -*- coding: utf-8 -*-
# License: MIT (https://tldrlegal.com/license/mit-license)
# Copyright (c) 2022, Paula Romero Jure et al.
# All rights reserved.
import numpy as np
import numpy.ma as ma

import pytest

from stratopy.transformers import coord_change

arr = np.array([35786023.0, -0.0, 0.0])
MASKED_SAT = arr.view(ma.MaskedArray)


def test_scan2sat():
    np.testing.assert_equal(MASKED_SAT, coord_change.scan2sat(0.0, 0.0))


def test_sat2latlon():
    sx, sy, sz = coord_change.scan2sat(0.0, 0.0)
    np.testing.assert_equal((0.0, -75.0), coord_change.sat2latlon(sx, sy, sz))


def test_latlon2scan():
    np.testing.assert_equal((0.0, 0.0), coord_change.latlon2scan(0.0, -75.0))


def test_colfil2scan():
    np.testing.assert_equal(
        (-0.151844, 0.151844), coord_change.colfil2scan(0.0, 0.0)
    )


def test_scan2colfil():
    col_int, row_int = coord_change.scan2colfil(0.0, 0.0, tipo=1)
    assert isinstance(col_int, np.int64)
    assert isinstance(row_int, np.int64)
    col_fl, row_fl = coord_change.scan2colfil(0.0, 0.0, tipo=0)
    assert isinstance(col_fl, float)
    assert isinstance(row_fl, float)
    np.testing.assert_equal((2712, 2712), coord_change.scan2colfil(0.0, 0.0))
    with pytest.raises(TypeError):
        coord_change.scan2colfil(0.0, 0.0, tipo=2)
