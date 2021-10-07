from stratopy import goes

path_goes = "data/GOES16/\
OR_ABI-L1b-RadF-M6C13_G16_s20191400530366_e20191400540086_c20191400540143.nc"


def test_metadata():
    data = goes.DayMicro(path_goes)
    repr_val = data.__repr__()
    assert isinstance(repr_val, str)


# def test_shape():
#   data = goes.DayMicro(path_goes)
#  assert isinstance(dir(data), list)
# assert isinstance(data.read_nc, Dataset)
# assert isinstance(data._repr_html_(), str)
