import pandas as pd

import pytest

from stratopy import cloudsat

PATH = (
    "data/CloudSat/"
    "2019003151948_67564_CS_2B-CLDCLASS_GRANULE_P1_R05_E08_F03.hdf"
)

HDF_FILE = cloudsat.read_hdf(PATH)


def test_hdf_read():
    assert isinstance(HDF_FILE, cloudsat.CloudSatFrame)


def test_hdf_read_exception():
    with pytest.raises(Exception):
        cloudsat.read_hdf("non_existing_file.hdf")


def test_CloudDataFrame():
    assert not isinstance(cloudsat.CloudSatFrame, pd.DataFrame)


def test_cut():
    trimmed_file = HDF_FILE.cut()
    assert trimmed_file.shape < HDF_FILE.shape


def test_cut_with_area():
    area_list = [-0.04492, 0.043348, 156.887802, 132.272720]
    trimmed_file = HDF_FILE.cut(area=area_list)
    assert trimmed_file.shape < HDF_FILE.shape


def test_cut_with_area_exception():
    area_list = [-0.04492, 0.043348]
    with pytest.raises(ValueError):
        HDF_FILE.cut(area=area_list)


def test_convert_coordinates():
    converted_file = HDF_FILE.convert_coordinates()
    assert len(HDF_FILE.columns) < len(converted_file.columns)
