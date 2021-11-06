# from stratopy import goes
# from netCDF4 import Dataset

# path_channel_3 = (
#     "data/GOES16/"
#     "OR_ABI-L2-CMIPF-M3C03_G16_s20190021800363_e20190021811129_\
# c20190021811205.nc"
# )
# path_channel_7 = (
#     "data/GOES16/"
#     "OR_ABI-L2-CMIPF-M3C07_G16_s20190021800363_e20190021811141_"
#     "c20190021811202.nc"
# )
# path_channel_13 = (
#     "data/GOES16/"
#     "OR_ABI-L2-CMIPF-M3C13_G16_s20190021800363_e20190021811141_"
#     "c20190021811221.nc"
# )
# ds = Dataset(path_channel_13)

# def test_repr():
#     data = goes.GoesDataFrame(ds)
#     repr_val = data.__repr__()
#     assert isinstance(repr_val, str)


# def test_shape():
#   data = goes.DayMicro(path_goes)
#  assert isinstance(dir(data), list)
# assert isinstance(data.read_nc, Dataset)
# assert isinstance(data._repr_html_(), str)
