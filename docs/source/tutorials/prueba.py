# %%
import pytz
from stratopy.extractors import ebase
from stratopy.extractors import cloudsat
from stratopy.extractors import goes
from stratopy.transformers import mergers, scalers
from dateutil import parser
from pandas import Timestamp
import matplotlib.pyplot as plt
from stratopy import metadatatools
from unittest import mock

# %%
csat_obj = cloudsat.CloudSat(
    product_type="2B-CLDCLASS.P1_R05",
    username="paula.romero@mi.unc.edu.ar",
    keypass="2022",
)
csat_data = csat_obj.fetch("09/jan/2019 15:29", tzone="UTC")
# %%
goes_obj = goes.GOES16("ABI-L2-CMIPF", channel=9)
goesdata = goes_obj.fetch("2019 jan 9 16:00")

# %%
scanx, scany = coord_change.latlon2scan(
    csat_data["lat"].to_numpy(), csat_data["lon"].to_numpy()
)

cols, rows = coord_change.scan2colfil(scanx, scany)

# %%

time_selected = "2019 jan 9 16:00"
dt_selected = parser.parse(time_selected)

# %%
# Checks if selected time is within cloudsat pass range
first_time = (
    Timestamp(csat_data.time.to_numpy()[0]).to_pydatetime().replace(tzinfo=pytz.UTC)
)
last_time = (
    Timestamp(csat_data.time.to_numpy()[-1]).to_pydatetime().replace(tzinfo=pytz.UTC)
)

if dt_selected < first_time or dt_selected > last_time:
    raise ebase.NothingHereError("Time out of range")

# %%
csat_data["time"][0].to_numpy()


# %%
def gen_vect(col, row, image):
    # key_list = list(band_dict.keys())

    brows, bcols = image.shape

    if col > bcols or row > brows:
        raise ValueError("Input column or row larger than image size")
    # band_vec = np.zeros((3, 3, N))

    # cut
    band_vec = image[
        row - 1 : row + 2,
        col - 1 : col + 2,
    ].copy()

    return band_vec


# %%
import xarray as xa

img = goesdata.CMI.to_numpy()  # Esto tarda
# %%
imlist = []
for i in range(len(cols)):
    imlist.append(gen_vect(cols[i], rows[i], img))

# %%
merged_ds = csat_data.concat(imlist, dim="cloudsat_trace")

# %%
import numpy as np

_TRACE = np.arange(36950, dtype=np.int32)

# other = xr.Dataset({"bar": ("x", [1, 2, 3, 4]),
#                    "x": list("abcd")})
da = xa.DataArray(
    imlist,
    dims=("cloudsat_trace", "ancho", "alto"),
    coords={
        "cloudsat_trace": _TRACE.copy(),
        "ancho": np.arange(0, 3, 1),
        "alto": np.arange(0, 3, 1),
    },
)

# %%
ds = xa.Dataset({"goes": da})
# %%
from stratopy.transformers import transform

result = transform.merge(
    csat_data,
    time_selected="2019 jan 9 16:00",
    goes_prod_type="ABI-L2-CMIPF",
    band=9,
)
# %%
parser.parse(
    "2019 jan 9 16:00",
)

# %%
from copy import deepcopy


class const(object):
    def __setattr__(self, name, value):
        if self.__dict__.__contains__(name):
            print(
                "NO WAY this is a const"
            )  # put here anything you want(throw exc and etc)
            return deepcopy(self.__dict__[name])
        self.__dict__[name] = value

    def __getattr__(self, name, value):
        if self.__dict__.has_key(name):
            return deepcopy(self.__dict__[name])

    def __delattr__(self, item):
        if self.__dict__.has_key(item):
            print("NOOOOO")  # throw exception if needed


CONST = const()
CONST.Constant1 = 111
CONST.Constant1 = 12
# print(a.Constant1)  # 111
CONST.Constant2 = "tst"
CONST.Constant2 = "tst1"
# print(a.Constant2)  # 'tst'
# %%

mobj = mergers.MergePolarGeos("2019 jan 9 16:00")

# %%
scaled_goes = scalers.MinMaxNormalize().transform(goesdata)
# %%
mdata = mobj.transform(csat_data, scaled_goes)

# %%
import os


@mock.patch("paramiko.SSHClient.open_sftp")
@mock.patch("paramiko.SSHClient.connect")
@mock.patch("paramiko.RSAKey.from_private_key_file", return_value="pkey")
def test_SFTPMixin_download(from_private_key_file, connect, open_sftp):
    class TestSFTP(ebase.SFTPMixin, ebase.ConnectorABC):
        def get_endpoint(cls):
            return "endpoint"

        def _makequery(self, endpoint, pdate):
            return "dir/pattern.*"

        def _parse_result(self, response):
            # response.append("_parse_result")
            return cloudsat.read_hdf4(response)

        @classmethod
        def get_orbit_type(cls):
            return metadatatools.POLAR

        def get_platform(self):
            return metadatatools.GOES

        def get_instrument_type(self):
            return metadatatools.RADARS

        def get_product_type_key(self):
            return "some product"

    conn = TestSFTP("host", "port", "zaraza@coso.com", keyfile="algo")
    sat_path = "../../../tests/data/CloudSat/2019002175851_67551_CS_2B-CLDCLASS_GRANULE_P1_R05_E08_F03.hdf"
    coso = cloudsat.read_hdf4(sat_path)
    from_private_key_file.assert_called_once_with("algo", password=None)
    connect.assert_called_once_with(
        "host", port="port", username="zaraza@coso.com", pkey="pkey"
    )

    # mock listdir
    listdir = open_sftp.return_value.__enter__.return_value.listdir
    listdir.return_value = [sat_path]

    get = open_sftp.return_value.__enter__.return_value.get
    get.return_value = "value"

    response = conn.fetch("27/07/1981", force=True)

    listdir.assert_called_once_with("dir")

    get.assert_called_once()
    get.call_args.kwargs["remotepath"] == "dir/pattern.ext"
    # localpath is a randomstring

    assert os.path.basename(response).startswith("stpy_")

    del conn  # to check coverage


# %%
