import datetime
import os

import geopandas as gpd

import numpy as np

import pandas as pd

from pyhdf.HDF import HC, HDF
from pyhdf.SD import SD
from pyhdf.VS import VS

# type: ignore


def read_hdf(path, layer="CloudLayerType", convert=True):
    """
    Read a hdf file

    Args:
        path (str): string of path file
        layer (str, optional): select any layer of the
        hdf file. Defaults to 'CloudLayerType'.

    Returns:
        dataframe: contain Latitude, Longitude and 10 layers
                   separated in columns.
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
        layers_df = pd.DataFrame(data=np.c_[lon, lat, cld_layertype])
        layers_df.columns = ["Longitude", "Latitude"] + [
            f"capa_{i}" for i in range(10)
        ]
    finally:
        vs.end()
    if convert:
        return convert_coordinates(layers_df)
    return layers_df


def convert_coordinates(df, layers_df=None, projection=None):
    """
    Parameters
    ----------
    layers_df: pandas DataFrame
    projection: str
        the reprojection that the user desires
        Default: geostationary, GOES-R
    """
    if projection is None:
        projection = """+proj=geos +h=35786023.0 +lon_0=-75.0
            +x_0=0 +y_0=0 +ellps=GRS80 +units=m +no_defs +sweep=x"""

    if layers_df is None:
        layers_df = df

    geo_df = gpd.GeoDataFrame(
        layers_df,
        geometry=gpd.points_from_xy(layers_df.Longitude, layers_df.Latitude),
    )
    geo_df.crs = "EPSG:4326"
    # EPSG 4326 corresponds to coordinates in latitude and longitude
    # Reprojecting into GOES16 geostationary projection
    geodf_to_proj = geo_df.to_crs(projection)
    return geodf_to_proj


class CloudClass:
    """[summary]"""

    def __init__(self, hdf_path):
        """
        doc
        """
        self.path = hdf_path
        self.hdf_file = read_hdf(hdf_path)
        self.file_name = os.path.split(self.path)[-1]
        self.date = self.file_name.split("_")[0]
        self.hour_utc = self.date[7:9]

    @property
    def day_night_(self):
        date_time = datetime.datetime.strptime(self.date, "%Y%j%H%M%S")
        desc = (
            "Start collect: " f"{date_time.strftime('%Y %B %d Time %H:%M:%S')}"
        )
        if int(self.hour_utc) > 10:

            return desc + " day"
        else:
            return desc + " night"

    def __repr__(self) -> (str):
        """repr(x) <=> x.__repr__()."""
        with pd.option_context("display.show_dimensions", False):
            df_body = repr(self.hdf_file).splitlines()
        df_dim = list(self.hdf_file.shape)
        sdf_dim = f"{df_dim[0]} rows x {df_dim[1]} columns"
        footer = f"\nCloudSatDataFrame - {sdf_dim}"
        cloudsat_cldcls_repr = "\n".join(df_body + [footer])
        return cloudsat_cldcls_repr

    def __repr_html__(self) -> str:
        ad_id = id(self)

        with pd.option_context("display.show_dimensions", False):
            df_html = self.hdf_file.__repr_html__()
        rows = f"{self.hdf_file.shape[0]} rows"
        columns = f"{self.hdf_file.shape[1]} columns"

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
        Parameters:
            area = [lat_0, lat_1, lon_0, lon_1]
            where:
                lat_0, latitude of minimal position
                lat_1, latitude of maximal position
                lon_0, longitude of minimal position
                lon_1, longitude of maximal position
            Default:
                the cut will be south hemisphere
        """
        df = self.hdf_file
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


# # cdf = stpy.read_goes(....)
# # sdf = stpy.read_csat(...)

# # stpy.merge(sdf, cdf)

# # df = stpy.StratropyDataframe(goes=gds, cloudsat=cdf, ...)

# # def repr(...):
# #     '''Deberia retornar algunas cosas que queremos,
# #     - cantidad de datos
# #     - satelites
# #     - ....
# #     '''
