import geopandas as gpd

from stratopy import cloudsat
from stratopy import core

path = "data/CloudSat/\
2019003151948_67564_CS_2B-CLDCLASS_GRANULE_P1_R05_E08_F03.hdf"


def test_hdf_read():
    dado = cloudsat.read_hdf(path)
    assert isinstance(dado, core.StratoPyDataFrame)


def test_day_night():
    path_hdf = cloudsat.CloudClass(path)
    assert "day" == path_hdf.day_night()
    path2 = "data/CloudSat/\
2019003051948_67564_CS_2B-CLDCLASS_GRANULE_P1_R05_E08_F03.hdf"
    path_hdf = cloudsat.CloudClass(path2)
    assert "night" == path_hdf.day_night()


def test_cut():
    path_hdf = cloudsat.read_hdf(path)
    corte = cloudsat.CloudClass(path).cut()
    assert corte.shape < path_hdf.shape
    assert cloudsat.CloudClass(path).cut(sur=False) is None


def test_cloudsat_repr():
    path_hdf = cloudsat.CloudClass(path)
    repr_val = path_hdf.__repr__()
    assert isinstance(repr_val, str)


def test_convert_coverage():
    path_hdf = cloudsat.read_hdf(path)
    ej = cloudsat.CloudClass(path)
    geo_df = ej.convert_coordinates(path_hdf.model_df)
    assert isinstance(geo_df, gpd.GeoDataFrame)
