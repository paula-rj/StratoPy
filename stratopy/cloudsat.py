import getpass
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


def read_hdf(path, layer="CloudLayerType", convert=False):
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
    except Exception as e:
        raise e
    else:
        # Read sd data
        file_path = SD(path)
        cld_layertype = file_path.select(layer)[:]
        layers_df = {"Longitude": lon, "Latitude": lat}
        for i, v in enumerate(np.transpose(cld_layertype)):
            layers_df[f"capa_{i}"] = v
        cld_df = CloudDataFrame(layers_df)
    finally:
        vs.end()
    if convert:
        return convert_coordinates(cld_df)
    return cld_df


def convert_coordinates(hdf_df, projection=None):
    """
    Parameters
    ----------
    layers_df: ``pandas.DataFrame``, optional (default=None)
    projection: ``str``, optional (default=geostationary, GOES-R)
        The reprojection that the user desires.

    """
    if projection is None:
        projection = """+proj=geos +h=35786023.0 +lon_0=-75.0
            +x_0=0 +y_0=0 +ellps=GRS80 +units=m +no_defs +sweep=x"""

    geo_df = gpd.GeoDataFrame(
        hdf_df,
        geometry=gpd.points_from_xy(hdf_df["Longitude"], hdf_df["Latitude"]),
    )
    # EPSG 4326 corresponds to coordinates in latitude and longitude
    geo_df.crs = "EPSG:4326"

    # Reprojecting into GOES16 geostationary projection
    geodf_to_proj = geo_df.to_crs(projection)
    return geodf_to_proj


@attr.s(frozen=True, repr=False)
class CloudDataFrame:
    """[summary]"""

    cld_df = attr.ib(
        validator=attr.validators.instance_of(pd.DataFrame),
        converter=pd.DataFrame,
    )

    def __getitem__(self, slice):
        sliced = self.cld_df.__getitem__(slice)
        return CloudDataFrame(cld_df=sliced)

    def __dir__(self):
        return super().__dir__() + dir(self.cld_df)

    def __getattr__(self, a):
        return getattr(self.cld_df, a)

    def __repr__(self) -> (str):
        """repr(x) <=> x.__repr__()."""
        with pd.option_context("display.show_dimensions", False):
            df_body = repr(self.cld_df).splitlines()
        df_dim = list(self.cld_df.shape)
        sdf_dim = f"{df_dim[0]} rows x {df_dim[1]} columns"
        footer = f"\nCloudSatDataFrame - {sdf_dim}"
        cloudsat_cldcls_repr = "\n".join(df_body + [footer])
        return cloudsat_cldcls_repr

    def __repr_html__(self) -> str:
        ad_id = id(self)

        with pd.option_context("display.show_dimensions", False):
            df_html = self.cld_df.__repr_html__()
        rows = f"{self.cld_df.shape[0]} rows"
        columns = f"{self.cld_df.shape[1]} columns"

        footer = f"CloudSatDataFrame - {rows} x {columns}"

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
        df = self.cld_df
        if not area:
            cld_layertype = df[df.Latitude < 0]
        elif len(area) == 4:
            latitude_min = area[0]
            latitude_max = area[1]
            longitude_min = area[2]
            longitude_max = area[3]
            cld_layertype = df[
                df["Latitude"].between(latitude_min, latitude_max)
            ]
            cld_layertype = cld_layertype[
                cld_layertype["Longitude"].between(
                    longitude_min, longitude_max
                )
            ]
        else:
            raise TypeError(
                "Spected list. "
                "For example:\n"
                "[lat_min, lat_max, lon_min, lon_max]"
            )

        return cld_layertype


def fetch_cloudsat(dirname, path=DEFAULT_CACHE_PATH):
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
        user = input("login user name:")
        passwd = getpass.getpass(prompt="login password: ")
        ftp.login(user, passwd)

        buffer_file = io.BytesIO()
        ftp.retrbinary(f"RETR {dirname}", buffer_file.write)
        result = buffer_file.getvalue()

        cache.set(id_, result, tag="stratopy-cloudsat")

    with tempfile.TemporaryDirectory() as tmpdirname:
        fname = os.path.join(tmpdirname, id_)

        with open(fname, "wb") as fp:
            fp.write(result)

        df = CloudDataFrame(fname)

    return df
