import geopandas as gpd

import pandas as pd

from stratopy import cloudsat

path = "data/CloudSat/\
2019003151948_67564_CS_2B-CLDCLASS_GRANULE_P1_R05_E08_F03.hdf"


def test_hdf_read():
    dado = cloudsat.read_hdf(path)
    assert isinstance(dado, pd.DataFrame)


def test_day_night():
    path_hdf = cloudsat.CloudClass(path)
    assert "day" == path_hdf.day_night_
    #     path2 = "data/CloudSat/\
    # 2019003051948_67564_CS_2B-CLDCLASS_GRANULE_P1_R05_E08_F03.hdf"
    path_hdf2 = cloudsat.CloudClass(path)
    assert "night" != path_hdf2.day_night_


def test_cut():
    path_hdf = cloudsat.read_hdf(path)
    corte = cloudsat.CloudClass(path).cut()
    assert corte.shape < path_hdf.shape
    # assert cloudsat.CloudClass(path).cut() is None


def test_cloudsat_repr():
    path_hdf = cloudsat.CloudClass(path)
    repr_val = path_hdf.__repr__()
    assert isinstance(repr_val, str)


def test_convert_coverage():
    path_hdf = cloudsat.read_hdf(path)
    geo_df = cloudsat.convert_coordinates(path_hdf)
    assert isinstance(geo_df, gpd.GeoDataFrame)
