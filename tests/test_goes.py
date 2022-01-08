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


def test_read_nc():
    assert isinstance(goes.read_nc((PATH_CHANNEL_7,)), goes.Goes)
    assert isinstance(goes.read_nc(FILE_PATH), goes.Goes)


def test_read_nc_date():
    with pytest.raises(ValueError):
        goes.read_nc((PATH_CHANNEL_3, PATH_CHANNEL_7, FAKE_DATE))


def test_read_nc_product():
    with pytest.raises(ValueError):
        goes.read_nc((PATH_CHANNEL_3, PATH_CHANNEL_7, FAKE_PRODUCT))


def test_read_nc_len():
    with pytest.raises(ValueError):
        goes.read_nc((PATH_CHANNEL_3, PATH_CHANNEL_7))


def test_repr():
    pdf = goes.read_nc((PATH_CHANNEL_7,))
    pdf_image = pdf.img_date.strftime("%d/%m/%y-%H:%M")
    bands = [int(band.split("C")[1]) for band in pdf._data.keys()]
    if len(bands) == 1:
        expected = f"GOES Object -- {pdf_image}, CH={bands[0]}"
    else:
        expected = (
            f"GOES Object -- {pdf_image}, "
            f"CH={bands[0]}, {bands[1]} and {bands[2]}"
        )
    assert repr(pdf) == expected


def test_repr_html_():
    pdf = goes.read_nc((PATH_CHANNEL_7,))
    img_date = pdf.img_date.strftime("%d/%m/%y-%H:%M")
    bands = [int(band.split("C")[1]) for band in pdf._data.keys()]
    footer = "<b>-- Goes Object</b>"
    if len(bands) == 1:
        expected = f"<div>{img_date}, , CH={bands[0]} {footer}</div>"
    else:
        expected = (
            f"<div>{img_date}, , "
            f"CH={bands[0]}, {bands[1]} and {bands[2]} {footer}</div>"
        )
    assert pdf._repr_html_() == expected
