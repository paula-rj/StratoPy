import io
import os
import pathlib

from diskcache import Cache

import pytest

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


@pytest.fixture
def memory_buffer():
    def make(file_path):
        # In memory buffer to store binary
        buffer = io.BytesIO()

        # open file and store
        with open(file_path, "rb") as binary_stream:
            buffer.write(binary_stream.read())

        return buffer.getvalue()

    return make


def test_cache_cloudsat(memory_buffer):
    # Generates cache id
    file_name = os.path.split(PATH_CLOUDSAT)[-1]
    id_ = file_name.split("_")[0]

    # Brings binary from file
    binary = memory_buffer(PATH_CLOUDSAT)

    # Initialize cache and store binary
    cache = Cache(DEFAULT_CACHE_PATH)  # HAY QUE MOCKEAR ESTO
    cache.set(id_, binary, tag="stratopy-cloudsat")

    # Try to fetch file with wrong username and password
    assert isinstance(
        IO.fetch_cloudsat(CLOUDSAT_SERVER_DIR, user=None, passwd=None),
        CloudSatFrame,
    )
