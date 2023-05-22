# %%
import pytz
from stratopy.extractors import base
from stratopy.extractors import cloudsat
from stratopy.extractors import goes
from stratopy.transformers import coord_change
from dateutil import parser
from pandas import Timestamp
import matplotlib.pyplot as plt

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
# dt_selected = parser.parse(time_selected)

# %%
# Checks if selected time is within cloudsat pass range
first_time = (
    Timestamp(csat_data.time.to_numpy()[0]).to_pydatetime().replace(tzinfo=pytz.UTC)
)
last_time = (
    Timestamp(csat_data.time.to_numpy()[-1]).to_pydatetime().replace(tzinfo=pytz.UTC)
)

if dt_selected < first_time or dt_selected > last_time:
    raise base.NothingHereError("Time out of range")

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
