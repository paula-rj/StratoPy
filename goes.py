# %%
# Librerias generales
import sys
from scipy import interpolate
import numpy as np
import pprint
import pandas as pd
import time as t
# %%%%%%%
# PyHDF
import pyhdf
from pyhdf.HDF import *
from pyhdf.VS import *
from pyhdf.SD import SD, SDC
# %%
# Librerias geo
import cartopy
import cartopy.crs as ccrs
import cartopy.io.shapereader as shpreader
# %%
from netCDF4 import Dataset
# Librerias para calcular zenith
# %%
import calendar
import logging
from datetime import datetime
# %%
from pyorbital import astronomy
from pyspectral.near_infrared_reflectance import Calculator
# Librerias para graficar
import matplotlib.pyplot as plt
import seaborn as sns

# %%
# Recorte


class GoesClass:

    def __init__(self, file_path):
        self.file_path = file_path

    def __repr__(self):
        pass

    def muestreo(x, y, z, esc=1, kind='cubic'):  # requiere numpy y scipy
        """ 
        Función necesaria para remuestrar la banda 3 del GOES, 
        que tiene tamaño de pixel 1000 m a diferencia del resto que tiene tamaño de pixel 2000 m.

        Parameters
        ----------
        x:  range_like
          range(0,ancho o cantidad de columnas de la imagen)
        y:  range_like
          range(0,alto o cantidad de filas de la imagen)
        z: array_like
          matriz de la imagen original
        esc: int
          escala
        kind: str
          tipo de interpolación

        Returns:
        -------
        f: array_like
          imagen con el nuevo tamaño """

        f = interpolate.interp2d(x, y, z, kind='cubic')
        xnew = np.arange(x[0], x[-1], (x[1]-x[0])/esc)
        ynew = np.arange(y[0], y[-1], (y[1]-y[0])/esc)
        return f(xnew, ynew)

            def recorte(data_path, x0=-555469.8930323641, y0=0.0):

        # lat =  0. -> y0
        # lon = -80. -> x0
        """
        Funcion que recorta la una imagen tipo CMI de GOES.
        Parameters
        ----------
        data_path: str. 
        Direccion de los datos GOES.
        x0: float. 
        Coordenada x del limite superior izquierdo en m.
        y0: float. 
        Coordenada y del limite superior izquierdo en m.

        Returns
        -------
        im_rec: matriz con los elementos del recorte

        Example
        -------
        """
        data = Dataset(data_path)
        metadato = data.variables
        banda = metadato['band_id'][:].data[0]
        print('banda =', banda)
        image = np.array(metadato['CMI'][:].data)

        # Parámetros para el recorte
        filas = 1440  # filas del recorte para la de referencia
        columnas = 1440  # filas del recorte para la de referencia

        if int(banda) == 3:
            image = muestreo(range(0, 10848), range(0, 10848), image, esc=0.5)
            psize = 2000
            N = 5424  # esc da 1
            print(f"Tamaño banda 3 pre-recorte = {image.shape}")
        else:  # bandas 7 y 13
            psize = 2000  # tamaño del pixel en km
            N = 5424  # esc da 1

        img_extentr = [x0, x0+columnas*psize, y0 -
                       filas*psize, y0]  # en proyeccion goes
        print('extent rec en proyeccion goes:', img_extentr)

        esc = int(N/image.shape[0])
        Nx = int(columnas/esc)  # numero de puntos del recorte en x
        Ny = int(filas/esc)  # numero de puntos del recorte en x
        f0 = int((-y0/psize+N/2-1.5)/esc)  # fila del angulo superior izquierdo
        # columna del angulo superior izquierdo
        c0 = int((x0/psize+N/2+.5)/esc)
        f1 = int(f0+Ny)  # fila del angulo inferior derecho
        c1 = int(c0+Nx)  # columna del angulo inferior derecho
        print('coordenadas filas, col: ', f0, c0, f1, c1)

        im_rec = image[f0:f1, c0:c1]
        return im_rec


# %%
rec03 = recorte("C:\Users\Paula\Documents\stratopy\StratoPy\data\GOES16\OR_ABI-L2-CMIPF-M3C03_G16_s20190021800363_e20190021811129_c20190021811205.nc")
rec07 = recorte("C:\Users\Paula\Documents\stratopy\StratoPy\data\GOES16\OR_ABI-L2-CMIPF-M3C07_G16_s20190021800363_e20190021811141_c20190021811202.nc")
rec13 = recorte("C:\Users\Paula\Documents\stratopy\StratoPy\data\GOES16\OR_ABI-L2-CMIPF-M3C13_G16_s20190021800363_e20190021811141_c20190021811221.nc")

# %%
# Calculamos zenith para banda 7


def solar_7(ch7, ch13, latlon_extent):
    """"
    Parameters
    ----------
    ch7: matriz (recortada) del canal 7
    ch13: matriz (recortada) del canal 13
    latlon_extent: list
    Lista [x1,y1,x2,y2] de los bordes de la imagen en latitud, longitud donde
        x1=longitud de más al oeste 
        y1=latitud de más al sur (punto y inferior)
        x2 = longitud de más al este
        y2=latitud de más al norte (punto y superior)

    Returns
    -------
    data2b: matriz con el cálculo de zenith pixel a pixel
    """
# Calculo del ángulo del sol para banda 7
    # NOTAR que esto está mal. Está calulando una latitud y longitud equiespaciadas.
    # Tengo el codigo para hacerlo bien, ya lo voy a subir.
    lat = np.linspace(latlon_extent[3], latlon_extent[1], ch7.shape[0])
    lon = np.linspace(latlon_extent[0], latlon_extent[2], ch7.shape[1])
    print(lat.shape)
    print(lon.shape)

    zenith = np.zeros((ch7.shape[0], ch7.shape[1]))
    # Calculate the solar zenith angle
    utc_time = datetime(2019, 1, 2, 18, 00)
    for x in range(len(lat)):
        for y in range(len(lon)):
            zenith[x, y] = astronomy.sun_zenith_angle(utc_time, lon[y], lat[x])
    refl39 = Calculator(platform_name='GOES-16', instrument='abi', band='ch7')
    data2b = refl39.reflectance_from_tbs(zenith, ch7, ch13)
    return data2b

# %%


def day_microphysicsRGB(rec03, rec07b, rec13):
    # RGB Components
    R = rec03  # banda3
    G = rec07b  # banda7 zenith
    B = rec13  # banda13

    # Minimuns and Maximuns
    Rmin = 0
    Rmax = 1

    Gmin = 0
    Gmax = 0.6

    Bmin = 203
    Bmax = 323

    #R[R.max] = Rmax
    #G[G.max] = Gmax
    #B[B.max] = Bmax

    # Choose the gamma -> STANDARIZADAS
    gamma_R = 1
    gamma_G = 2.5
    gamma_B = 1

    # Normalize the data
    R = ((R - Rmin) / (Rmax - Rmin)) ** (1/gamma_R)
    G = ((G - Gmin) / (Gmax - Gmin)) ** (1/gamma_G)
    B = ((B - Bmin) / (Bmax - Bmin)) ** (1/gamma_B)

    RR = np.copy(R)
    BB = np.copy(B)
    GG = np.copy(G)

    RR[RR < 0] = 0.
    RR[RR > 1] = 1.
    BB[BB < 0] = 0.
    BB[BB > 1] = 1.
    GG[GG < 0] = 0.
    GG[GG > 1] = 1.

# Create the RGB
    RGB = np.stack([R, G, B], axis=2)
    # el axis está para que el shape sea fil col dim y no dim col fil
    RRGB = np.stack([RR, GG, BB], axis=2)
    print(RGB.shape)
    return RRGB


# %%
# %%
rec03 = recorte("C:\Users\Paula\Documents\stratopy\StratoPy\data\GOES16\OR_ABI-L2-CMIPF-M3C03_G16_s20190021800363_e20190021811129_c20190021811205.nc")
rec07 = recorte("C:\Users\Paula\Documents\stratopy\StratoPy\data\GOES16\OR_ABI-L2-CMIPF-M3C07_G16_s20190021800363_e20190021811141_c20190021811202.nc")
rec13 = recorte("C:\Users\Paula\Documents\stratopy\StratoPy\data\GOES16\OR_ABI-L2-CMIPF-M3C13_G16_s20190021800363_e20190021811141_c20190021811221.nc")


latlon_extent = [-80, -30, -50, 0]  # lat y longs del recorte
rec07b = solar_7(rec07, rec13, latlon_extent)
rec07b.shape

RRGB = day_microphysicsRGB(rec03, rec07b, rec13)

plt.figure()
plt.imshow(RRGB)
plt.show()
