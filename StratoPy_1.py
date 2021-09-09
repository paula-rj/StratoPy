#%%
# #Importamos varias librerías necesarias
import numpy as np
import pyhdf
from pyhdf.HDF import *
from pyhdf.VS import *
from pyhdf.SD import SD, SDC
import matplotlib.pyplot as plt
import pprint
import os
import sys
# from mpl_toolkits.basemap import Basemap
import matplotlib.pyplot as plt
import matplotlib.cm as cm
from pylab import linspace
from scipy import interpolate
import pandas as pd
import geopandas as gpd
import seaborn as sns
import cartopy.crs as ccrs  # Plot maps

print('--- Importo todo ---')


# %%


class StratoPyDataFrame:

    def __init__(self, geopdf) -> None:
        self._df = geopdf

    def __getattr__(self, a):
        return getattr(self.df, a)

    def __geoitem__(self, k):
        return self._df.__getitem__(k)

def capas_dataframe(longitud, latitud, nombre_capa):
    """[summary]

    Args:
        longitud ([type]): [description]
        latitud ([type]): [description]
        capas ([type]): [description]
    """
    # verificamos que los numeros menores a 0 sean reemplazados por 0
    nombre_capa = np.where(nombre_capa>0, nombre_capa, 0) 
    datafm = pd.DataFrame({'Longitude': longitud, 'Latitude': latitud, 
                       'capa0': nombre_capa[:, 0], 'capa1': nombre_capa[:, 1], 'capa2': nombre_capa[:, 2],
                       'capa3': nombre_capa[:, 3], 'capa4': nombre_capa[:, 4], 'capa5': nombre_capa[:, 5],
                       'capa6': nombre_capa[:, 6], 'capa7': nombre_capa[:, 7], 'capa8': nombre_capa[:, 8],
                       'capa9': nombre_capa[:, 9]})
    return datafm

class CldClass:
    """[summary]
    """

    def __init__(self, path_total):
        self.path_total = path_total
        self.file_name = os.path.split(self.path_total)[-1]
        date = self.file_name.split('_')[0]
        self.year = date[:4]
        self.julian_day = date[4:7]
        self.hour_utc = date[7:9]
        self.light = ''
        if int(self.hour_utc) > 10:
            self.light = 'day'
        else:
            self.light = 'night'
    
    
    def open_cldclass(self, sur=True):
        """
        Función que toma un path donde debe estar el archivo CLDCLASS de Cloudsat y devuelve un dataframe de Pandas
        con los datos del archivo cldclass guardados en columnas del dataframe: latitud, longitud, capa0, capa1,..., capa9;
        con cada tipo de nube segun cada capa.
        Parameters:
        -----------
        sur : Bool. Si se quiere abrir solo la parte de sudamerica. Default=True.

        Returns:
        -----------
        layers_df: Pandas Dataframe lat, lon, tipo de nube en cada una de las capas (son 10)
        """
        # Read v data
        self.hdf_file = HDF(self.path_total, HC.READ)
        vs = self.hdf_file.vstart()
        # vdata = vs.vdatainfo()  # es una lista de tuplas. acá estan lat y long y cloud layers

        self.latitude = vs.attach('Latitude', write=0)[:]
        # self.latitude.detach

        self.longitude = vs.attach('Longitude', write=0)[:]
        # self.longitude.detach
        vs.end()
        # hdf_file.close()
        
        # Read sd data
        self.file = SD(self.path_total, SDC.READ)
        return self.file
        
    def get_latitude(self):
        """[summary]

        Returns:
            [type]: [description]
        """
        latitud = np.array(self.latitude).flatten()
        return latitud
        
    def get_longitude(self):
        """[summary]

        Returns:
            [type]: [description]
        """
        longitud = np.array(self.longitude).flatten()
        return longitud
        
    def get_cloud_type(self):
        """[summary]

        Returns:
            [type]: [description]
        """
        cld_type = self.file.select('CloudLayerType')[:]
        layer_type = capas_dataframe(longitud=self.longitude, latitud=self.latitude, nombre_capa=cld_type)
        return layer_type
    
    def get_cloud_base(self):
        """[summary]

        Returns:
            [type]: [description]
        """
        cld_base = self.file.select('CloudLayerBase')[:]
        layer_base = capas_dataframe(longitud=self.longitude, latitud=self.latitude, nombre_capa=cld_base)
        return layer_base

    def get_cloud_top(self):
        """[summary]

        Returns:
            [type]: [description]
        """
        cld_top = self.file.select('CloudLayerTop')[:]
        layer_top = capas_dataframe(longitud=self.longitud, latitud=self.latitude, nombre_capa=cld_top)
        return layer_top
        
    def plot_cldclass_geos(self, layers_data, capa_n):
        """
        Función que grafica los tipos de nubes en la capa asignada en la pasada del Cloudsat.
        Parameters:
        -----------
        layers_data : Pandas Dataframe.
        Dataframe de Pandas que contiene Latitud,Longitud,y la capa que se quiere graficar.
        capa_n : int
        Numero de capaque se quiere graficar. Van de 0 a 9.

        Returns:
        -----------
        Plot. Tipo de nube en la capa 9 con órbita proyectada en proyeccion geoestacionaria de GOES16,
        con mapa de costas de fondo.
        """
        capa_str = 'capa' + str(capa_n)

        # Generamos geodataframe a partir del pd dataframe de entrada
        geo_df = gpd.GeoDataFrame(layers_data.loc[:, ['Longitude', 'Latitude', capa_str]],
                                geometry=gpd.points_from_xy(layers_data.Longitude, layers_data.Latitude))
        # EPSG 4326 corresponds to coordinates in latitude and longitude
        geo_df.crs = {'init': 'epsg:4326'}
        # Reprojecting into GOES16 geostationary projection
        geodf_GOESproj = geo_df.to_crs("+proj=geos +h=35786023.0 +lon_0=-75.0")
        # proyeccion geoestacionaria para Goes16
        crs = ccrs.Geostationary(central_longitude=-75.0,
                                satellite_height=35786023.0)
        fig_dims = (10, 10)
        fig, axis = plt.subplots(figsize=fig_dims)
        axis = plt.axes(projection=crs)
        axis.gridlines
        axis.coastlines(resolution='10m', color='blue')
        sns.scatterplot(x='Longitude', y='Latitude', data=geodf_GOESproj, hue=capa_str,
                        palette='bright', s=2, transform=ccrs.PlateCarree())
        axis.set_title("""year {}; day {}; hour {}; {}""".format(
            self.year, self.julian_day, self.hour_utc, self.light))
        plt.show()

    def plotlatlon_cld(self, capa_n, layers_data_df):
        """
        Grafica la capa capa_n con latitud en el eje y y longitud en el eje x, sin ninguna proyeccion
            Parameters
            ----------
            capa_n : int
                El numero de capa que quiero dibujar. Entre 0 y 9.
            layers_data_df : pandas DataFrame
                DataFrame de Pandas o Geopandas que incluya latitud, longitud y la capa que vamos a dibujar.
            Returns
            ----------
            Plot."""

        capa_str = 'capa' + str(capa_n)
        fig_dims = (6, 6)
        fig, ax = plt.subplots(figsize=fig_dims)
        sns.scatterplot(x='Longitude', y='Latitude', data=layers_data_df,
                        hue='capa2', palette='bright', marker='o', s=1)
        ax.set_xlabel('Longitude')
        ax.set_ylabel('Latitude')
        plt.show()


# %%
# NO usé esta funcion pero la dejo por si sirve

def cmap_discretize(cmap, n):
 """
    Return a discrete colormap from the continuous colormap cmap.

  Args:
  cmap: colormap instance, eg. cm.jet.
  n: number of colors.

  Example:
  x = resize(arange(100), (5,100))
  djet = cmap_discretize(cm.jet, 5)
  imshow(x, cmap=djet)
 """

 cdict = cmap._segmentdata.copy()
 # n colors
 colors_i = linspace(0, 1., n)
 # n+1 indices
 indices = linspace(0, 1., n+1)
 for key in ('red', 'green', 'blue'):
  # Find the n colors
  D = np.array(cdict[key])
  I = interpolate.interp1d(D[:, 0], D[:, 1])
        colors = I(colors_i)
        # Place these colors at the correct indices.
        A = np.zeros((n+1, 3), float)
        A[:, 0] = indices
        A[1:, 1] = colors
        A[:-1, 2] = colors
        # Create a tuple for the dictionary.
        L = []
        for l in A:
   L.append(tuple(l))
        cdict[key] = tuple(L)
 # Return colormap object.
 return LinearSegmentedColormap('colormap', cdict, 1024)


# %%
# Path del archivo CLDCLASS
# https: // moonbooks.org/Articles/How-to-read-a-MODIS-HDF-file-using-python-/

path = 'data/CloudSat/2019003183652_67566_CS_2B-CLDCLASS_GRANULE_P1_R05_E08_F03.hdf'

cloud = CldClass(path)
cloud.open_cldclass()
cloud.get_cloud_base()


# %%
corte_min, corte_max = 12346,12446
fig, ax = plt.subplots(figsize=(16, 9))
dado = ax.imshow(cld_layertype[corte_min: corte_max, :].T,
                 vmin=0, vmax=10, origin='lower', cmap='rainbow')
# plt.colorbar(dado)
# norm = mpl.colors.Normalize(vmin=0, vmax=10)
# plt.colorbar(mpl.cm.ScalarMappable(norm=norm, cmap='rainbow'),
#              cax=ax, orientation='horizontal', )



tipo_capa = capas_dataframe(longitud=longitud, latitud=latitud, capas=cld_layertype)

base = capas_dataframe(longitud=longitud, latitud=latitud, capas=layer_base)

top = capas_dataframe(longitud=longitud, latitud=latitud, capas=layer_top)

# Comprobamos que haya algun valor distinto de -99 que es missing value en Layer Base
for i in range(layer_base.shape[0]):
    nb_cloud_layer = np.where(layer_base[i, :] < 0)

