import io
import os
import pathlib
from unittest import mock

from diskcache.core import ENOVAL

from stratopy import IO
from stratopy.cloudsat import CloudSatFrame

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


# def test_fetch_cloudsat_patched():
# In memory buffer to store binary
#    buffer = io.BytesIO()

# open file and store
#   with open(PATH_CLOUDSAT, "rb") as binary_stream:
#       buffer.write(binary_stream.read())

#    with mock.patch("buffer_file.getvalue", return_value=buffer.read()):
#        result = IO.fetch_cloudsat(CLOUDSAT_SERVER_DIR, user=None, passwd=None

#    assert isinstance(result, CloudSatFrame)
