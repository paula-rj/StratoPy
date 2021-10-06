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
    if path is None:
        raise FileNotFoundError(
            "The enter path is wrong"
            "Try with the complete path!"
            "E.g. /home/user/data/CloudSat/..."
        )

    hdf_file = HDF(path, HC.READ)
    vs = VS(hdf_file)

    vd_lat = vs.attach("Latitude", write=0)
    lat = np.array(vd_lat[:]).flatten()
    vd_lat.detach

    vd_lon = vs.attach("Longitude", write=0)
    lon = np.array(vd_lon[:]).flatten()
    vd_lon.detach

    vs.end()

    # Read sd data
    file = SD(path)
    cld_layertype = file.select(layer)[:]
    layers_df = pd.DataFrame(
        {
            "Latitude": lat,
            "Longitude": lon,
            "capa0": cld_layertype[:, 0],
            "capa1": cld_layertype[:, 1],
            "capa2": cld_layertype[:, 2],
            "capa3": cld_layertype[:, 3],
            "capa4": cld_layertype[:, 4],
            "capa5": cld_layertype[:, 5],
            "capa6": cld_layertype[:, 6],
            "capa7": cld_layertype[:, 7],
            "capa8": cld_layertype[:, 8],
            "capa9": cld_layertype[:, 9],
        }
    )
    if convert:
        return convert_coordinates(layers_df)
    else:
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
        if int(self.hour_utc) > 10:
            return "day"
        return "night"

    def __repr__(self):
        date_time = datetime.datetime.strptime(self.date, "%Y%j%H%M%S")
        rep = (
            "CloudSat Dataset:\n"
            "Start collect --> "
            f"{date_time.strftime('%Y %B %d Time %H:%M:%S')}"
        )
        return rep

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
