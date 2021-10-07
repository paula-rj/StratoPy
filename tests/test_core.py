from stratopy import cloudsat
from stratopy import core

"""
para escribir tests devemos tener en mente,

Metodologia (GWT)
- given -> dado
- when  -> cuando
- then  -> entonces

-- arange -> ordena
-- act    -> acciona el test
-- assert -> acierta

TDD kant beck - One-step Test
"""

path = "data/CloudSat/\
2019003151948_67564_CS_2B-CLDCLASS_GRANULE_P1_R05_E08_F03.hdf"


def test_shape():
    data = cloudsat.read_hdf(path)
    assert data.shape == data.shape
    assert isinstance(dir(data), list)
    assert isinstance(data.__repr__(), str)
    assert isinstance(data._repr_html_(), str)


def test_metadata():
    metadata = core.MetaData({"a": 1, "b": 2})
    assert isinstance(metadata.__repr__(), str)
    assert metadata.a == 1
    assert len(metadata) == 2


# def test_fetch_cloudsat(monkeypatch):
#     monkeypatch.setattr('builtins.input', lambda _: "jose.stratopy")
    
#     df = core.fetch_cloudsat(path)
#     assert isinstance(df, cloudsat.CloudClass)
#     assert df.date.isnumeric()
#     assert df.hour_utc.isnumeric()


# ejemplo del uso del fetch
# path = '2B-CLDCLASS-LIDAR.P1_R05/2019/180/\
# 2019180235812_70156_CS_2B-CLDCLASS-LIDAR_GRANULE_P1_R05_E08_F03.hdf'
# path2 = '/2B-CLDCLASS-LIDAR.P1_R05/2019/180/\
# 2019180154532_70151_CS_2B-CLDCLASS-LIDAR_GRANULE_P1_R05_E08_F03.hdf'
# df = core.fetch_cloudsat(path)
