import pandas as pd

from stratopy import cloudsat

path = (
    "data/CloudSat/"
    "2019003151948_67564_CS_2B-CLDCLASS_GRANULE_P1_R05_E08_F03.hdf"
)


def test_hdf_read():
    assert isinstance(cloudsat.read_hdf(path), cloudsat.CloudDataFrame)


def test_CloudDataFrame():
    assert not isinstance(cloudsat.CloudDataFrame, pd.DataFrame)


def test_cut():
    path_hdf = cloudsat.read_hdf(path)
    corte = path_hdf.cut()
    assert corte.shape < path_hdf.shape
