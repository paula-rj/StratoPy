import io
import os
import pathlib
import tempfile
from ftplib import FTP

import attr

from diskcache import Cache
from diskcache.core import ENOVAL

import geopandas as gpd

import numpy as np

import pandas as pd

from pyhdf.HDF import HC, HDF
from pyhdf.SD import SD
from pyhdf.VS import VS

# type: ignore
DEFAULT_CACHE_PATH = pathlib.Path(
    os.path.expanduser(os.path.join("~", "stratopy_cache"))
)


def read_hdf(path, layer="CloudLayerType"):
    """
    Function for reading CloudSat data files, with extension ".hdf".

    Parameters
    ----------
    file_path: ``str``
        String containing path to file.
    layer: ``str``, optional (default="CloudLayerType")
        Select any layer of the hdf file.

    Returns
    -------
    ``pandas.DataFrame``:
        Dataframe containing Latitude, Longitude and
        10 layers separated in columns.
    """
    try:
        hdf_file = HDF(path, HC.READ)
        vs = VS(hdf_file)
        vd_lat = vs.attach("Latitude", write=0)
        lat = np.array(vd_lat[:]).flatten()
        vd_lat.detach
        vd_lon = vs.attach("Longitude", write=0)
        lon = np.array(vd_lon[:]).flatten()
        vd_lon.detach
    except Exception as error:
        raise error
    else:
        # Read sd data
        file_path = SD(path)
        cld_layertype = file_path.select(layer)[:]
        layers_df = {"Longitude": lon, "Latitude": lat}
        for i, v in enumerate(np.transpose(cld_layertype)):
            layers_df[f"capa_{i}"] = v
        cld_df = CloudSatFrame(layers_df)
        vs.end()

    return cld_df


@attr.s(frozen=True, repr=False)
class CloudSatFrame:
    """[summary]"""

    _df = attr.ib(
        validator=attr.validators.instance_of(pd.DataFrame),
        converter=pd.DataFrame,
    )

    def __getitem__(self, slice):
        return self._df.__getitem__(slice)

    def __dir__(self):
        return super().__dir__() + dir(self._df)

    def __getattr__(self, a):
        return getattr(self._df, a)

    def __repr__(self) -> (str):
        """repr(x) <=> x.__repr__()."""
        with pd.option_context("display.show_dimensions", False):
            df_body = repr(self._df).splitlines()
        df_dim = list(self._df.shape)
        sdf_dim = f"{df_dim[0]} rows x {df_dim[1]} columns"
        footer = f"\nCloudSatFrame - {sdf_dim}"
        cloudsat_cldcls_repr = "\n".join(df_body + [footer])
        return cloudsat_cldcls_repr

    def __repr_html__(self) -> str:
        ad_id = id(self)

        with pd.option_context("display.show_dimensions", False):
            df_html = self._df.__repr_html__()
        rows = f"{self._df.shape[0]} rows"
        columns = f"{self._df.shape[1]} columns"

        footer = f"CloudSatFrame - {rows} x {columns}"

        parts = [
            f'<div class="stratopy-data-container" id={ad_id}>',
            df_html,
            footer,
            "</div>",
        ]
        html = "".join(parts)
        return html

    def cut(self, area=None):
        """
        Parameters
        ----------
            area: ``list``, optional (default: cut will be south hemisphere)
                [lat_0, lat_1, lon_0, lon_1] where:
                    lat_0, latitude of minimal position
                    lat_1, latitude of maximal position
                    lon_0, longitude of minimal position
                    lon_1, longitude of maximal position

        """
        if not area:
            return CloudSatFrame(
                self._df.loc[
                    (self._df.Latitude < 0) & (self._df.Longitude < 0)
                ]
            )
        elif len(area) == 4:
            latitude_min = area[0]
            latitude_max = area[1]
            longitude_min = area[2]
            longitude_max = area[3]

            return CloudSatFrame(
                self._df.loc[
                    self._df["Latitude"].between(latitude_min, latitude_max)
                    & self._df["Longitude"].between(
                        longitude_min, longitude_max
                    )
                ]
            )
        else:
            raise ValueError("area must have length four")

    def convert_coordinates(self):
        """
        Parameters
        ----------
        ndf: ``pandas.DataFrame``, optional (default=None)
        projection: ``str``, optional (default=geostationary, GOES-R)
            The reprojection that the user desires.

        """

        projection = (
            "+proj=geos +h=35786023.0 +lon_0=-75.0 "
            "+x_0=0 +y_0=0 +ellps=GRS80 +units=m +no_defs +sweep=x"
        )

        geo_df = gpd.GeoDataFrame(
            self._df.values,
            columns=self._df.columns,
            index=self._df.index,
            geometry=gpd.points_from_xy(
                self._df["Longitude"], self._df["Latitude"]
            ),
        )
        # EPSG 4326 corresponds to coordinates in latitude and longitude
        geo_df.crs = "EPSG:4326"

        # Reprojecting into GOES16 geostationary projection
        geodf_to_proj = geo_df.to_crs(projection)
        return CloudSatFrame(geodf_to_proj)


def fetch_cloudsat(dirname, user, passwd, path=DEFAULT_CACHE_PATH):
    """Fetch files of a certain date from cloudsat server and
    stores in a local cache.
    """
    cache = Cache(path)

    # Transform dirname into cache id
    id_ = os.path.split(dirname)[-1]

    # Search in local cache
    cache.expire()
    result = cache.get(id_, default=ENOVAL, retry=True)

    if result is ENOVAL:

        ftp = FTP()
        ftp.connect(host="ftp.cloudsat.cira.colostate.edu")
        ftp.login(user, passwd)

        buffer_file = io.BytesIO()
        ftp.retrbinary(f"RETR {dirname}", buffer_file.write)
        result = buffer_file.getvalue()

        cache.set(id_, result, tag="stratopy-cloudsat")

    with tempfile.TemporaryDirectory() as tmpdirname:
        fname = os.path.join(tmpdirname, id_)

        with open(fname, "wb") as fp:
            fp.write(result)

        df = CloudSatFrame(fname)

    return df
