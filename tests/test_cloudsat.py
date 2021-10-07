import geopandas as gpd

import pandas as pd

from stratopy import cloudsat

path = "data/CloudSat/\
2019003151948_67564_CS_2B-CLDCLASS_GRANULE_P1_R05_E08_F03.hdf"
df = cloudsat.CloudClass(path)

def test_hdf_read():
    dado = cloudsat.read_hdf(path)
    assert isinstance(dado, pd.DataFrame)


def test_day_night():
    assert "day" == df.day_night_
    # path2 = "data/CloudSat/\
    # 2019003051948_67564_CS_2B-CLDCLASS_GRANULE_P1_R05_E08_F03.hdf"
    # path_hdf2 = cloudsat.CloudClass(path)
    assert "night" != df.day_night_


def test_cut():
    corte = df.cut()
    assert corte.shape < df.hdf_file.shape
    # assert cloudsat.CloudClass(path).cut() is None


def test_cloudsat_repr():
    repr_val = df.__repr__()
    assert isinstance(repr_val, str)


def test_convert_coverage():
    geo_df = cloudsat.convert_coordinates(df.hdf_file)
    assert isinstance(geo_df, gpd.GeoDataFrame)


# path = '2B-CLDCLASS-LIDAR.P1_R05/2019/180/
# 2019180235812_70156_CS_2B-CLDCLASS-LIDAR_GRANULE_P1_R05_E08_F03.hdf'
