import geopandas as gpd

from stratopy import cloudsat

path = (
    "data/CloudSat/"
    "2019003151948_67564_CS_2B-CLDCLASS_GRANULE_P1_R05_E08_F03.hdf"
)


def test_hdf_read(monkeypatch):
    monkeypatch.setattr(cloudsat, "read_hdf", lambda x: 4)
    dado = cloudsat
    assert dado.read_hdf(path) == 4


# @pytest.mark.slow
def test_day_night(monkeypatch):
    monkeypatch.setattr(cloudsat.CloudClass, "day_night_", "day")
    path_hdf = cloudsat
    assert "day" == path_hdf.CloudClass(path).day_night_
    assert "night" != path_hdf.CloudClass(path).day_night_


# @pytest.mark.slow
def test_cut():
    path_hdf = cloudsat.read_hdf(path)
    corte = cloudsat.CloudClass(path).cut()
    assert corte.shape < path_hdf.shape
    # assert cloudsat.CloudClass(path).cut() is None


# def test_cloudsat_repr():
#     path_hdf = cloudsat.CloudClass(path)
#     with pd.option_context('display.show_dimensions', False):
#         df_body = repr(path_hdf)
#     # assert repr(path_hdf) ==


def test_convert_coverage():
    path_hdf = cloudsat.read_hdf(path)
    geo_df = cloudsat.convert_coordinates(path_hdf)
    assert isinstance(geo_df, gpd.GeoDataFrame)
