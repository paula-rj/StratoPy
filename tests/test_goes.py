import pytest

from stratopy import goes

PATH_CHANNEL_3 = (
    "data/GOES16/"
    "OR_ABI-L2-CMIPF-M3C03_G16_s20190021800363_e20190021811129_\
c20190021811205.nc"
)
PATH_CHANNEL_7 = (
    "data/GOES16/"
    "OR_ABI-L2-CMIPF-M3C07_G16_s20190021800363_e20190021811141_"
    "c20190021811202.nc"
)
PATH_CHANNEL_13 = (
    "data/GOES16/"
    "OR_ABI-L2-CMIPF-M3C13_G16_s20190021800363_e20190021811141_"
    "c20190021811221.nc"
)

FILE_PATH = (PATH_CHANNEL_3, PATH_CHANNEL_7, PATH_CHANNEL_13)

FAKE_DATE = (
    "data/GOES16/"
    "OR_ABI-L2-CMIPF-M3C13_G16_s20191801800363_e20190021811141_"
    "c20190021811221.nc"
)

FAKE_PRODUCT = (
    "data/GOES16/"
    "OR_ABI-L1b-RadF-M3C13_G16_s20190021800363_e20190021811141_"
    "c20190021811221.nc"
)


# def test_read_nc():
#    assert isinstance(goes.read_nc((PATH_CHANNEL_7,)), goes.Goes)
#    assert isinstance(goes.read_nc(FILE_PATH), goes.Goes)


def test_read_nc_date():
    with pytest.raises(ValueError):
        goes.read_nc((PATH_CHANNEL_3, PATH_CHANNEL_7, FAKE_DATE))


def test_read_nc_product():
    with pytest.raises(ValueError):
        goes.read_nc((PATH_CHANNEL_3, PATH_CHANNEL_7, FAKE_PRODUCT))


def test_read_nc_len():
    with pytest.raises(ValueError):
        goes.read_nc((PATH_CHANNEL_3, PATH_CHANNEL_7))
