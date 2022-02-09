import numpy as np
import numpy.ma as ma

from stratopy import core

arr = np.array(35786023.0, -0.0, 0.0)
masked_sat = arr.view(ma.MaskedArray)


def test_scan2sat():
    np.testing.assert_equal(masked_sat, core.scan2sat(0.0, 0.0))


def test_sat2latlon():
    sx, sy, sz = core.scan2sat(0.0, 0.0)
    np.testing.assert_equal((0.0, -75.0), core.sat2latlon(sx, sy, sz))


def test_latlon2scan():
    np.testing.assert_equal((0.0, 0.0), core.latlon2scan(0.0, -75.0))


def test_colfil2scan():
    np.testing.assert_equal((-0.151844, 0.151844), core.colfil2scan(0.0, 0.0))


def test_scan2colfil():
    col_int, row_int = core.scan2colfil((0.0, 0.0), tipo=1)
    assert isinstance(col_int, int)
    assert isinstance(row_int, int)
    col_fl, row_fl = core.scan2colfil((0.0, 0.0), tipo=0)
    assert isinstance(col_fl, float)
    assert isinstance(row_fl, float)
    np.testing.assert_equal((2712, 2712), core.scan2colfil((0.0, 0.0)))
