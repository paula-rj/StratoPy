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
def test_cut():
    path_hdf = cloudsat.read_hdf(path)
    corte = path_hdf.cut()
    assert corte.shape < path_hdf.shape
    # assert cloudsat.CloudClass(path).cut() is None
