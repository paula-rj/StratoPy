import os
import numpy as np
import matplotlib.pyplot as plt

#from pyhdf.HDF import * creo que esto esta mal segun PEP8
#from pyhdf.VS import *

import cartopy.crs as ccrs

import pandas as pd
import geopandas as gpd
# import seaborn as sns

from pyhdf.SD import SD, SDC
from pyhdf.HDF import HDF, HC
from pyhdf.VS import VS


class CloudClass:
    def __init__(self, hdf_path):
        self.path = hdf_path
        self.file_name = os.path.split(self.path)[-1]
        date = self.file_name.split('_')[0]
        self.year = date[:4]
        self.julian_day = date[4:7]
        self.hour_utc = date[7:9]
        self.light = ''
        if int(self.hour_utc) > 10:
            self.light = 'day'
        else:
            self.light = 'night'

    # def __getattr__(self, a):
    #     return self[a]

    def __repr__(self):
        #la idea es que retorne un obj clodcclass con fecha y hora
        pass

    def read(self):
        #la idea es que lea el hdf y lo devuelva en formato DF de pandas

        #Read v data
        hdf_file = HDF(self.path, HC.READ)
        vs = hdf_file.vstart()
        vdata = vs.vdatainfo(
        )  #es una lista de tuplas de 9 elementos cada una. acá estan lat y long y cloud layers

        vd_lat = vs.attach('Latitude', write=0)
        lat = vd_lat[:]
        vd_lat.detach

        vd_lon = vs.attach('Longitude', write=0)
        lon = vd_lon[:]
        vd_lon.detach

        vs.end()
        # hdf_file.close()

        latitud = np.array(lat).flatten()
        longitud = np.array(lon).flatten()

        #Read sd data
        file = SD(self.path, SDC.READ)
        cld_layertype = file.select('CloudLayerType')[:]
        self.layers_df = pd.DataFrame({
            'Longitude': longitud,
            'Latitude': latitud,
            'capa0': cld_layertype[:, 0],
            'capa1': cld_layertype[:, 1],
            'capa2': cld_layertype[:, 2],
            'capa3': cld_layertype[:, 3],
            'capa4': cld_layertype[:, 4],
            'capa5': cld_layertype[:, 5],
            'capa6': cld_layertype[:, 6],
            'capa7': cld_layertype[:, 7],
            'capa8': cld_layertype[:, 8],
            'capa9': cld_layertype[:, 9]
        })
        return self.layers_df

    def plot_statistics(self):
        self.read()
        df = self.layers_df
        for i, capa in enumerate([f'capa{i}' for i in range(0, 10)]):
            plt.subplot(2, 5, i + 1)
            df[capa].loc[df[capa] != -99].hist()
            plt.title(capa)
        plt.show()

        def cut(self, df, sur=True):
            #la idea es que recorte la pasada segun elija el usuario
            # quizas habria que ponerla junto con read?
            #como está ahora lo que hace es cortarla en sudamérica si sur=True
            #Otra idea: ver si puede cortar donde es de dia y donde es de noche
            start_point = 0
            end_point = 36951
            if sur == True:
                if self.light == 'night':
                    end_point = 6000
                else:
                    end_point = 20000
            if self.hour_utc == (15):
                start_point = 6000
            else:  #16,17,18 utc
                start_point = 10000
            latitud = latitud[start_point:end_point]
            longitud = longitud[start_point:end_point]

            cld_layertype = df  #.iloc([start_point:end_point]) #creo que era asi

            return cld_layertype

        def convert_coordinates(
                self,
                layers_df,
                projection="+proj=geos +h=35786023.0 +lon_0=-75.0"):
            #la idea es que retorne un geopandas dataframe con la conversion de coordenadas
            #que elija el usuario
            #hay que ver si no conviene que desde el principio, osea desde read, retorne un geopd df
            """
            Parameters
            ----------
            layers_df: pandas DataFrame
            projection: str
                the reprojection that the user desires
                Default: geostationary, GOES-R

            """
            geo_df = gpd.GeoDataFrame(layers_df,
                                      geometry=gpd.points_from_xy(
                                          layers_data.Longitude,
                                          layers_data.Latitude))
            geo_df.crs = {
                'init': 'epsg:4326'
            }  # EPSG 4326 corresponds to coordinates in latitude and longitude
            #Reprojecting into GOES16 geostationary projection
            geodf_GOESproj = geo_df.to_crs(projection)
            return geo_df

        def plot_layers(self):
            #plotea height vs latitud o longitud y el tipo de nube en cada capa
            #ver https://moonbooks.org/Codes/Plot-cldclass-lidar-granule-vertical-profile-using-python-3/
            #para esta hay que extraer otros datos del hdf que estan en la parte de SD
            #como layer_TOP, layer_bottom

            #Read SD
            file = SD(self.hdf_path, SDC.READ)
            cld_layertype = np.array(file.select('CloudLayerType')[:])
            layer_base = np.array(file.select('CloudLayerBase')[:])
            layer_top = np.array(file.select('CloudLayerTop')[:])
            height = np.array(file.select('Height')[:])

            pass

        def plot_layers_3D(self):
            #lo mismo que el anterior pero altura vs lat vs lon osea en 3d
            pass

        def plot_latlon(self, layers_df, layer):
            """Plots Latitude vs Longitude and the type of clouds along the CloudSat orbit for every (lon,lat) point
            Parameters
            ----------
            layers_df: Pandas DataFrame
                DataFrame que contiene latitud, longitud, tipo de nube en cada capa
            layer: int
                number of layer #el usuario elige que capa quiere plotear 
            Returns
            -------
            imagen? 
            VER SI CONVIENE QUE RETORNE Y GUARDE PNG O JPG O ALGO ASI
            """

            dic_LayerType = {
                0: 'no',
                1: 'Ci',
                2: 'As',
                3: 'Ac',
                4: 'St',
                5: 'Sc',
                6: 'Cu',
                7: 'Ns',
                8: 'DC'
            }
            fig_dims = (8, 8)
            fig, ax = plt.subplots(figsize=fig_dims)
            sns.scatterplot(
                x='Longitude',
                y='Latitude',
                data=tipo_capa.assign(
                    tipos_capa0=tipo_capa.capa0.map(dic_LayerType)),
                hue='tipos_capa0',
                palette='bright',
                marker='o',
                s=1)

            ax.set_xlabel('Longitude')
            ax.set_ylabel('Latitude')
            plt.show()

        def plot_projection(self, geodf, layer):
            """Dibuja la capa layer de la pasada sobre el mapa con la reproyeccion que eligio el usuario 
            Parameters:
            ----------
            geopd: Geopandass DataFrame
            layer: int
                chosen layer to plot

            Returns:
            -------
            Imagen?
            """
            layer_str = 'capa' + str(layer)
            crs = ccrs.Geostationary(central_longitude=-75.0,
                                     satellite_height=35786023.0
                                     )  #proyeccion geoestacionaria para Goes16
            fig_dims = (10, 10)
            fig, axis = plt.subplots(figsize=fig_dims)
            axis = plt.axes(projection=crs)
            axis.gridlines
            axis.coastlines(resolution='10m', color='blue')
            sns.scatterplot(x='Longitude',
                            y='Latitude',
                            data=geodf,
                            hue=layer_str,
                            palette='bright',
                            s=2,
                            transform=ccrs.PlateCarree())
            axis.set_title(
                f"year {self.year}; day {self.julian_day}; hour {self.hour_utc}; {self.light}"
            )
            plt.show()
