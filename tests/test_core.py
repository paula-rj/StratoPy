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
