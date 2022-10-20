from pdb import set_trace
from unittest import mock

import pytest

from stratopy.remote_access import goes

import xarray as xa


@pytest.mark.parametrize("ptype", goes.GOES16._PRODUCT_TYPES_PARSERS)
def test_GOES_get_endpoint(ptype):
    goes_obj = goes.GOES16(ptype)
    assert goes_obj.get_endpoint() == f"s3://noaa-goes16/{ptype}"


@mock.patch("s3fs.S3FileSystem.glob", return_value=["fake/path/test"])
def test_GOES16_fetch(mglob, data_bytes, dataset):

    buff = data_bytes(
        "GOES16",
        "OR_ABI-L2-CMIPF-M3C03_G16_s20190040600363_e20190040611130_c20190040611199.nc",
    )

    with mock.patch("s3fs.S3FileSystem.open", return_value=buff) as mopen:
        result = goes.GOES16("L1b-RadF").fetch("25/jun/2010")

    mglob.assert_called_once_with(
        "s3://noaa-goes16/L1b-RadF/2010/176/00/"
        "OR_L1b-RadF-M6C03_G16_s20101760000*"
    )

    expected = dataset(
        "GOES16",
        "OR_ABI-L2-CMIPF-M3C03_G16_s20190040600363_e20190040611130_c20190040611199.nc",
        "h5netcdf",
    )
    mopen.assert_called_once_with("fake/path/test", "rb")
    xa.testing.assert_allclose(result, expected)
    
    assert buff.isclosed()
    import ipdb;ipdb set_trace
