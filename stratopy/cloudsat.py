import datetime

import geopandas as gpd

import numpy as np

import pandas as pd

import os

from pyhdf.HDF import HC, HDF
from pyhdf.SD import SD
from pyhdf.VS import VS

# type: ignore


def read_hdf(path, layer="CloudLayerType"):
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
    return layers_df


class CloudClass:
    """[summary]"""

    def __init__(self, hdf_path):
        """Yo no pondría el path en el init ya que
        sacamos la función de read fuera de la clase.
        Queremos que la clase opere sobre los CloudDataFrame
        pero no que los cree (segun lo que dijo juan).
        tal vez lo que debería recibir es un CloudDataFrame
        (por ponerle un nombre)
        """
        self.path = hdf_path
        self.file_name = os.path.split(self.path)[-1]
        self.date = self.file_name.split("_")[0]
        self.hour_utc = self.date[7:9]

    @property
    def day_night_(self):
        if int(self.hour_utc) > 10:
            return "day"
        else:
            return "night"

    def __repr__(self):
        date_time = datetime.datetime.strptime(self.date, "%Y%j%H%M%S")
        rep = (
            "Start collect --> "
            f"{date_time.strftime('%Y %B %d Time %H:%M:%S')}"
        )
        return rep

    def read_hdf(self):
        readHDF = read_hdf(self.path)
        return readHDF

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
        df = self.convert_coordinates()
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

    def convert_coordinates(self, layers_df=None, projection=None):
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
            layers_df = self.read_hdf()
        
        geo_df = gpd.GeoDataFrame(
            layers_df,
            geometry=gpd.points_from_xy(
                layers_df.Longitude, layers_df.Latitude
            ),
        )
        geo_df.crs = 'cyl' #"EPSG:4326"
        # EPSG 4326 corresponds to coordinates in latitude and longitude
        # Reprojecting into GOES16 geostationary projection
        geodf_to_proj = geo_df.to_crs(projection)
        return geodf_to_proj


# class Ftp_cloudsat:
#     def __init__(self, file=None, server="ftp.cloudsat.cira.colostate.edu"):
#         """Established FTP connection to Cloudsat server"""

#         user_name = input("login user name:")
#         pwd = getpass.getpass(prompt="login password: ")
#         self.ftp = FTP(server)
#         self.ftp.login(user_name, pwd)

#         if file is not None:
#             if ".hdf" in file:
#                 hdf = file.split("/")[-1]
#                 folder = file[: -len(hdf)]
#                 self.cd(folder)
#                 self.download(hdf)
#             else:
#                 print("not an .hdf file. Please navigate to file")
#         else:
#             pass

#     @property
#     def ls(self):
#         """List current directory files"""
#         return self.ftp.dir()

#     def cd(self, dir):
#         """Allows to navigate in ftp host to file"""
#         self.ftp.cwd(dir)
#         return self.ftp.dir()

#     def download(self, file):
#         """Downloads specific file"""
#         print("Starting download")
#         downloaded = self.ftp.retrbinary(
#             f"RETR {file}", open(file, "wb").write
#         )
#         print("Finished download")
#         return downloaded

#     def quit(self):
#         """Close connection with the server"""
#         print("Closing connection with the server")
#         self.ftp.quit()
#         print("Connection closed")
#         return None

#     def explore(self, date, product="2B-CLDCLASS", release="P1_R05"):
#         """Access product directory and show files of a desire date.
#         Parameters
#         ----------
#         date: ``int tuple``
#             Tuple that contains date of observation in format (YYYY, MM, DD).
#         product: ``str``, optional (defalult='2B-CLDCLASS')
#             Cloudsat product.
#         release: ``str``, optional (defalult='P1_R05')
#             Cloudsat product version.

#         Returns
#         -------
#         dirname: ``str``
#             String containing the directory address of the input product
#             and date.
#         """
#         str_date = datetime.date(*date).strftime("%Y/%j")
#         dirname = f"{product}.{release}/{str_date}/"

#         try:
#             self.ftp.cwd(dirname)
#             return self.ftp.dir()
#         except error_perm as error:
#             print(error)
#             print("File not found. Try with other date or navigate to file.")


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
