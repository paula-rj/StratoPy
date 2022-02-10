import io
import os
import pathlib
from unittest import mock

from diskcache.core import ENOVAL

from stratopy import IO
from stratopy.cloudsat import CloudSatFrame
from stratopy.goes import Goes

DEFAULT_CACHE_PATH = pathlib.Path(
    os.path.expanduser(os.path.join("~", "stratopy_cache"))
)

PATH_GOES = (
    "data/GOES16/"
    "OR_ABI-L2-CMIPF-M3C03_G16_s20190021800363_e20190021811129_"
    "c20190021811205.nc"
)

PATH_CLOUDSAT = (
    "data/CloudSat/"
    "2019003151948_67564_CS_2B-CLDCLASS_GRANULE_P1_R05_E08_F03.hdf"
)

CLOUDSAT_SERVER_DIR = (
    "2B-CLDCLASS.P1_R05/2019/003/"
    "2019003151948_67564_CS_2B-CLDCLASS_GRANULE_P1_R05_E08_F03.hdf"
)

GOES_SERVER_DIR = (
    "noaa-goes16/ABI-L2-CMIPF/2019/002/18/"
    "OR_ABI-L2-CMIPF-M3C03_G16_s20190021800363_e20190021811129_"
    "c20190021811205.nc"
)


def test_cache_cloudsat():
    # In memory buffer to store binary
    buffer = io.BytesIO()

    # open file and store
    with open(PATH_CLOUDSAT, "rb") as binary_stream:
        buffer.write(binary_stream.read())

    with mock.patch(
        "diskcache.Cache.get", return_value=buffer.getvalue()
    ) as cache_get:
        cls_frame = IO.fetch_cloudsat(
            CLOUDSAT_SERVER_DIR, user=None, passwd=None
        )
        cache_get.assert_called_with(
            "2019003151948", default=ENOVAL, retry=True
        )

    assert isinstance(
        cls_frame,
        CloudSatFrame,
    )


def test_cache_goes():
    # In memory buffer to store binary
    buffer = io.BytesIO()

    # open file and store
    with open(PATH_GOES, "rb") as binary_stream:
        buffer.write(binary_stream.read())

    with mock.patch(
        "diskcache.Cache.get", return_value=buffer.getvalue()
    ) as cache_get:
        goes_frame = IO.fetch_goes(GOES_SERVER_DIR)
        cache_get.assert_called_with(
            "20190021800363", default=ENOVAL, retry=True
        )

    assert isinstance(
        goes_frame,
        Goes,
    )


@mock.patch("stratopy.IO.FTP")
@mock.patch("diskcache.Cache.set")
@mock.patch("io.BytesIO")
def test_fetch_cloudsat_patched(mock_buffer, mock_cache, mock_ftp_constrctor):
    mock_ftp = mock_ftp_constrctor.return_value

    # open cloudsat file and store binary
    with open(PATH_CLOUDSAT, "rb") as binary_stream:
        cls_binary = binary_stream.read()

    # Mock memory buffered binary stream from server
    mock_buffer.return_value.getvalue.return_value = cls_binary

    # Call function with mocked connection and cache
    cloudsat_frame = IO.fetch_cloudsat(
        CLOUDSAT_SERVER_DIR, user=None, passwd=None
    )

    mock_ftp.connect.assert_called_with(host="ftp.cloudsat.cira.colostate.edu")
    mock_ftp.login.assert_called_with(None, None)
    mock_cache.assert_called()

    assert isinstance(
        cloudsat_frame,
        CloudSatFrame,
    )
