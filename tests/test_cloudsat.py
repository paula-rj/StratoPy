import pandas as pd

import pytest

from stratopy import cloudsat

path = (
    "data/CloudSat/"
    "2019003151948_67564_CS_2B-CLDCLASS_GRANULE_P1_R05_E08_F03.hdf"
)


def test_hdf_read():
    assert isinstance(cloudsat.read_hdf(path), cloudsat.CloudSat)


def test_hdf_read_exception():
    with pytest.raises(Exception):
        cloudsat.read_hdf("non_existing_file.hdf")


def test_CloudDataFrame():
    assert not isinstance(cloudsat.CloudSat, pd.DataFrame)


def test_cut():
    hdf_file = cloudsat.read_hdf(path)
    trimmed_file = hdf_file.cut()
    assert trimmed_file.shape < hdf_file.shape


def test_cut_with_area():
    hdf_file = cloudsat.read_hdf(path)
    area_list = [-0.04492, 0.043348, 156.887802, 132.272720]
    trimmed_file = hdf_file.cut(area=area_list)
    assert trimmed_file.shape < hdf_file.shape


def test_cut_with_area_exception():
    hdf_file = cloudsat.read_hdf(path)
    area_list = [-0.04492, 0.043348]
    with pytest.raises(ValueError):
        hdf_file.cut(area=area_list)
