import pandas as pd

from stratopy import cloudsat

path = "data/CloudSat/\
2019003151948_67564_CS_2B-CLDCLASS_GRANULE_P1_R05_E08_F03.hdf"


def test_hdf_read():
    dado = cloudsat.read_hdf(path)
    assert isinstance(dado, pd.DataFrame)


def test_day_night():
    path_hdf = cloudsat.CloudClass(path)
    assert "day" == path_hdf.day_night_()


def test_cut():
    path_hdf = cloudsat.read_hdf(path)
    corte = cloudsat.CloudClass(path).cut()
    assert corte.shape < path_hdf.shape
