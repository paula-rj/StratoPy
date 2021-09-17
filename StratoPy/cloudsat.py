import os
import datetime
import numpy as np
import matplotlib.pyplot as plt

# from pyhdf.HDF import * creo que esto esta mal segun PEP8
# from pyhdf.VS import *


# import cartopy.crs as ccrs

import pandas as pd
import geopandas as gpd

# import seaborn as sns

from pyhdf.SD import *
from pyhdf.HDF import *
from pyhdf.VS import *

# Para ftp
from ftplib import FTP, error_perm
import getpass


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

    # la idea es que lea el hdf y lo devuelva en formato DF de pandas
    # Read v data
    hdf_file = HDF(path, HC.READ)
    vs = hdf_file.vstart()
    # vdata = (
    #     vs.vdatainfo()
    # )  # es una lista de tuplas de 9 elementos cada una.
    # acá estan lat y long y cloud layers

    vd_lat = vs.attach("Latitude", write=0)
    lat = np.array(vd_lat[:]).flatten()
    vd_lat.detach

    vd_lon = vs.attach("Longitude", write=0)
    lon = np.array(vd_lon[:]).flatten()
    vd_lon.detach

    vs.end()
    # hdf_file.close()

    # latitud = np.array(lat).flatten()
    # longitud = np.array(lon).flatten()

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
        # Yo no pondría el path en el init ya que
        # sacamos la función de read fuera de la clase.
        # Queremos que la clase opere sobre los CloudDataFrame
        # pero no que los cree (segun lo que dijo juan).
        # tal vez lo que debería recibir es un CloudDataFrame
        # (por ponerle un nombre)
        self.path = hdf_path
        self.file_name = os.path.split(self.path)[-1]
        self.date = self.file_name.split("_")[0]
        # self.year = self.date[:4]
        # self.julian_day = self.date[4:7]
        self.hour_utc = self.date[7:9]
        self.light = ""
        if int(self.hour_utc) > 10:
            self.light = "day"
        else:
            self.light = "night"

    # def __getattr__(self, a):
    #     return self[a]
    # def __doc__(self):
    #     return f'{self.read_hdf}'

    def __repr__(self):
        # la idea es que retorne un obj clodcclass con fecha y hora
        date_time = datetime.datetime.strptime(self.date,
                                               "%Y%j%H%M%S")
        rep = ("Start collect --> "
               f"{date_time.strftime('%Y %B %d Time %H:%M:%S')}")
        # rep = f'''Year: {self.year:>10s}
        # \nJulian Day: {self.julian_day:>4s}\nHour:
        # {self.hour_utc: >10s}'''
        return rep

    def read_hdf(self):
        readHDF = read_hdf(self.path)
        return readHDF


    def cut(self, df, sur=True):
        # la idea es que recorte la pasada segun
        #  elija el usuario
        # quizas habria que ponerla junto con read?
        # como está ahora lo que hace es cortarla en
        # sudamérica si sur=True
        # Otra idea: ver si puede cortar donde es de dia
        #  y donde es de noche

        # start_point = 0
        # end_point = 36951
        # if sur == True:
        #     if self.light == "night":
        #         end_point = 6000
        #     else:
        #         end_point = 20000
        # if self.hour_utc == (15):
        #     start_point = 6000
        # else:  # 16,17,18 utc
        #     start_point = 10000

        # latitud = latitud[start_point:end_point]
        # longitud = longitud[start_point:end_point]

        # .iloc([start_point:end_point]) #creo que era asi
        cld_layertype = df
        return cld_layertype

    def convert_coordinates(
        self, layers_df, projection="+proj=geos +h=35786023.0 +lon_0=-75.0"
    ):

        # la idea es que retorne un geopandas dataframe con
        # la conversion de coordenadas
        # que elija el usuario
        # hay que ver si no conviene que desde el principio,
        #  osea desde read, retorne un geopd df
        """
        Parameters
        ----------
        layers_df: pandas DataFrame
        projection: str
            the reprojection that the user desires
            Default: geostationary, GOES-R
        """
        geo_df = gpd.GeoDataFrame(
            layers_df,
            geometry=gpd.points_from_xy(
                layers_df.Longitude, layers_df.Latitude
            ),
        )
        geo_df.crs = {
            "init": "epsg:4326"
        }  # EPSG 4326 corresponds to coordinates in latitude and longitude
        # Reprojecting into GOES16 geostationary projection
        # geodf_GOESproj = geo_df.to_crs(projection)
        return geo_df



class ftp_cloudsat:
    def __init__(self, file=None, server="ftp.cloudsat.cira.colostate.edu"):
        """Established FTP connection to Cloudsat server"""

        user_name = input("login user name:")
        pwd = getpass.getpass(prompt="login password: ")
        self.ftp = FTP(server)
        self.ftp.login(user_name, pwd)

        if file is not None:
            if ".hdf" in file:
                hdf = file.split("/")[-1]
                folder = file[: -len(hdf)]
                self.cd(folder)
                self.download(hdf)
            else:
                print("not an .hdf file. Please navigate to file")
        else:
            pass

    @property
    def ls(self):
        """List current directory files"""
        return self.ftp.dir()

    def cd(self, dir):
        """Allows to navigate in ftp host to file"""
        self.ftp.cwd(dir)
        return self.ftp.dir()

    def download(self, file):
        """Downloads specific file"""
        print("Starting download")
        downloaded = self.ftp.retrbinary(f"RETR {file}",
                                         open(file, "wb").write)
        print("Finished download")
        return downloaded

    def quit(self):
        """Close connection with the server"""
        print("Closing connection with the server")
        self.ftp.quit()
        print("Connection closed")
        return None

    def explore(self, date, product="2B-CLDCLASS", release="P1_R05"):
        """ Access product directory and show files of a desire date.
        Parameters
        ----------
        date: ``int tuple``
            Tuple that contains date of observation in format (YYYY, MM, DD).
        product: ``str``, optional (defalult='2B-CLDCLASS')
            Cloudsat product.
        release: ``str``, optional (defalult='P1_R05')
            Cloudsat product version.

        Returns
        -------
        dirname: ``str``
            String containing the directory address of the input product
            and date.
        """
        str_date = datetime.date(*date).strftime("%Y/%j")
        dirname = f"{product}.{release}/{str_date}/"

        try:
            self.ftp.cwd(dirname)
            return self.ftp.dir()
        except error_perm as error:
            print(error)
            print("File not found. Try with other date or navigate to file.")
