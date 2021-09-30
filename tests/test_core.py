from stratopy.cloudsat import read_hdf


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
    data = read_hdf(path)
    assert data.shape == data.shape
