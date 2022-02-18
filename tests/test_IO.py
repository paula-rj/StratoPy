import io
import os
import pathlib
from unittest import mock

from diskcache.core import ENOVAL

from stratopy import IO, merger
from stratopy.cloudsat import CloudSatFrame, read_hdf
from stratopy.goes import Goes, read_nc

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
    "2019002175851_67551_CS_2B-CLDCLASS_GRANULE_P1_R05_E08_F03.hdf"
)

CLOUDSAT_SERVER_DIR = (
    "2B-CLDCLASS.P1_R05/2019/002/"
    "2019002175851_67551_CS_2B-CLDCLASS_GRANULE_P1_R05_E08_F03.hdf"
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
            "2019002175851", default=ENOVAL, retry=True
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
def test_fetch_cloudsat_patched(mock_buffer, mock_cache, mock_ftp_constructor):
    mock_ftp = mock_ftp_constructor.return_value

    # open cloudsat file and store binary
    with open(PATH_CLOUDSAT, "rb") as binary_stream:
        cls_binary = binary_stream.read()

    # Mock memory buffered binary stream from server
    mock_buffer.return_value.getvalue.return_value = cls_binary

    # Call function with mocked connection and cache
    cloudsat_frame = IO.fetch_cloudsat(
        CLOUDSAT_SERVER_DIR, user=None, passwd=None
    )

    # Check if mocked instances were called
    mock_ftp.connect.assert_called_with(host="ftp.cloudsat.cira.colostate.edu")
    mock_ftp.login.assert_called_with(None, None)
    mock_cache.assert_called()

    assert isinstance(
        cloudsat_frame,
        CloudSatFrame,
    )


@mock.patch("s3fs.S3FileSystem")
@mock.patch("diskcache.Cache.set")
def test_fetch_goes_patched(mock_cache, mock_s3):
    # Mock open method of s3 module
    mock_s3.return_value.open.return_value = open(PATH_GOES, "rb")

    # Call function with mocked connection and cache
    goes_frame = IO.fetch_goes(GOES_SERVER_DIR)

    # Check if mocked instances were called
    mock_s3.return_value.open.assert_called_with(GOES_SERVER_DIR, "rb")
    mock_cache.assert_called()

    assert isinstance(goes_frame, Goes)


#@mock.patch("stratopy.IO.fetch_goes")
#@mock.patch("stratopy.IO.fetch_cloudsat")
# def test_fetch(mock_cloudsat, mock_goes):
#     # Mock calls to fetch with goes and cloudsat objects
#     mock_goes.return_value = read_nc((PATH_GOES,))
#     mock_cloudsat.return_value = read_hdf(PATH_CLOUDSAT)

#     # Call function with mocked clients
#     stratoframe = IO.fetch(CLOUDSAT_SERVER_DIR, GOES_SERVER_DIR)

#     # Assert calls to individual fetchs
#     mock_goes.assert_called_with(GOES_SERVER_DIR)
#     mock_cloudsat.assert_called_with(CLOUDSAT_SERVER_DIR)

#     assert isinstance(stratoframe, merger.StratoFrame)
