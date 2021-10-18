import re
from datetime import datetime

from netCDF4 import Dataset

import numpy as np

from pyorbital import astronomy

from pyspectral.near_infrared_reflectance import Calculator

from scipy import interpolate

from . import latlon2geos


def read_nc(file_path):
    """Function for reading GOES16 files, with extension ".nc".
    It works the same for level L1 and L2.

    Parameters
    ----------
    file_path: ``str tuple``
        Tuple of length three containing the paths of the channels 3, 7
        and 13 of the CMIPF GOES-16 product.

    Returns
    -------
    im_rec: ``netCDF4.Dataset`` object.


    """
    # Open netcdf file and extract variables
    data = Dataset(file_path, "r")
    result = data.variables
    return result


class GoesDataFrame:
    """Generates an object containing de Day Microphysics state
    according to GOES-16 manual.

    Parameters
    ----------
    path_channel_3: ``str``
        String containing the path to "nc" file for channel 3 of the
        CMIPF GOES-16 product.
    path_channel_7: ``str``
        String containing the path to "nc" file for channel 7 of the
        CMIPF GOES-16 product.
    path_channel_13: ``str``
        String containing the path to "nc" file for channel 13 of the
        CMIPF GOES-16 product.
    """

    def __init__(self, path_channel_3, path_channel_7, path_channel_13):
        self.file_path = (path_channel_3, path_channel_7, path_channel_13)
        self.metadata = read_nc(self.file_path[0])

        # Check for date and product consistency
        files_date = [
            band_path.split("s20", 1)[1].split("_", 1)[0]
            for band_path in self.file_path
        ]
        assert all(
            date == files_date[0] for date in files_date
        ), "Start date's from all files should be the same."
        assert all(
            "L2-CMIPF" in path for path in self.file_path
        ), "Files must be from the same product."

        # Saves from level L1 or L2
        find_numbers = re.findall(r"\d+", self.file_path[0])
        self.julian_date = find_numbers[5][:-1]
        start_date = datetime.strptime(self.julian_date, "%Y%j%H%M%S")
        self.sam_date = start_date.strftime("%d-%m-%y")
        self.utc_hour = start_date.hour

    def __repr__(self):
        return f"GOES object. Date: {self.sam_date}; {self.utc_hour} UTC "

    def recorte(self, rows=2891, cols=1352, lat_sup=10.0, lon_west=-80.0):

        """
        This function trim a GOES CMI image according to the width, height
        max west longitude and upper latitude specified on the parameters.

        Parameters
        ----------
        data_path: ``str``
            Path to GOES CMI image.
        rows: ``int``
            Height of the trimmed image in pixels.
        cols: ``int``
            Height of the trimmed image in pixels.
        lon_west: ``float``
            Maximum longitude to the west.
        lat_sup: ``float``
            Maximum upper latitude.

        Returns
        -------
        im_rec: ``numpy.array`` containing the trimmed image.

        """

        psize = 2000  # Tamaño del pixel en m
        N = 5424  # Tamaño de imagen con psize=2000 m

        metadata = self.metadata  # Extraigo todas las variables
        banda = metadata["band_id"][:].data[0]  # Extraigo el nro de banda
        # altura del satelite
        h = metadata["goes_imager_projection"].perspective_point_height
        semieje_may = metadata["goes_imager_projection"].semi_major_axis
        semieje_men = metadata["goes_imager_projection"].semi_minor_axis
        lon_cen = metadata[
            "goes_imager_projection"
        ].longitude_of_projection_origin

        pto_sup_izq = latlon2geos.latlon2scan(
            lat_sup, lon_west, lon_cen, Re=semieje_may, Rp=semieje_men, h=h
        )
        x0 = pto_sup_izq[1] * h
        y0 = pto_sup_izq[0] * h

        # Extraigo la imagen y la guardo en un array de np
        image = np.array(metadata["CMI"][:].data)

        if int(banda) == 3:
            esc = 0.5
            # escala es 1/2 porque tamaño de pixel de banda 3 = 1 km
            # y tamaño pixel del resto = 2 km
            x = range(0, 10848)
            y = range(0, 10848)
            f = interpolate.interp2d(x, y, image, kind="cubic")
            xnew = np.arange(x[0], x[-1], (x[1] - x[0]) / esc)
            ynew = np.arange(y[0], y[-1], (y[1] - y[0]) / esc)
            image = f(xnew, ynew)

        # tamaño del recorte en proyeccion goes
        # img_extentr = [x0, x0+columnas*psize, y0 -filas*psize, y0]

        esc = int(N / image.shape[0])
        Nx = int(cols / esc)  # numero de puntos del recorte en x
        Ny = int(rows / esc)  # numero de puntos del recorte en x
        f0 = int(
            (-y0 / psize + N / 2 - 1.5) / esc
        )  # fila del angulo superior izquierdo
        # columna del angulo superior izquierdo
        c0 = int((x0 / psize + N / 2 + 0.5) / esc)
        f1 = int(f0 + Ny)  # fila del angulo inferior derecho
        c1 = int(c0 + Nx)  # columna del angulo inferior derecho
        # print('coordenadas filas, col: ', f0, c0, f1, c1)

        im_rec = image[f0:f1, c0:c1]
        return im_rec

    def solar_7(self, ch7, ch13, latlon_extent):
        """
        This function does a zenith angle correction to channel 7.
        This correction is needed for daylight images.

        Parameters
        ----------
        ch7: ``numpy.array``
            Trimmed image of channel 7.
        ch13: ``numpy.array``
            Trimed image of channel 13.
        latlon_extent: ``list``
            List containing the borders of the image in latitude and
            longitude [x1,y1,x2,y2] where:
                x1, further west longitude
                y1, further south latitude
                x2, further east longitude
                y2, further north latitude

        Returns
        -------
        data2b: ``numpy.array``
            Zenith calculation for every pixel.
        """
        # Calculo del ángulo del sol para banda 7
        # NOTAR que esto está mal. Está calulando una latitud
        # y longitud equiespaciadas.
        # Tengo el codigo para hacerlo bien, ya lo voy a subir.
        lat = np.linspace(
            self.latlon_extent[3], self.latlon_extent[1], ch7.shape[0]
        )
        lon = np.linspace(
            self.latlon_extent[0], self.latlon_extent[2], ch7.shape[1]
        )
        print(lat.shape)
        print(lon.shape)

        zenith = np.zeros((ch7.shape[0], ch7.shape[1]))
        # Calculate the solar zenith angle
        utc_time = datetime(2019, 1, 2, 18, 00)
        for x in range(len(lat)):
            for y in range(len(lon)):
                zenith[x, y] = astronomy.sun_zenith_angle(
                    utc_time, lon[y], lat[x]
                )
        refl39 = Calculator(
            platform_name="GOES-16", instrument="abi", band="ch7"
        )
        data2b = refl39.reflectance_from_tbs(zenith, ch7, ch13)
        return data2b

    def RGBdmp(self, rec03, rec07, rec13):
        """
        This function creates an RGB image that represents the day microphysics
        according to the GOES webpage manual.

        Parameters
        ----------
        rec03: ``numpy.array``
            Processed image of channel 3.
        rec07b: ``numpy.array``
            Processed image of channel 7.
        rec13: ``numpy.array``
            Processed image of channel 13.

        Returns
        -------
        RGB: ``numpy.array``
            RGB day microphysics image.
        """

        # Correccion del zenith
        lat = np.linspace(
            self.latlon_extent[3], self.latlon_extent[1], rec07.shape[0]
        )
        lon = np.linspace(
            self.latlon_extent[0], self.latlon_extent[2], rec07.shape[1]
        )
        zenith = np.zeros((rec07.shape[0], rec07.shape[1]))
        # Calculate the solar zenith angle
        utc_time = datetime(2019, 1, 2, 18, 00)
        for x in range(len(lat)):
            for y in range(len(lon)):
                zenith[x, y] = astronomy.sun_zenith_angle(
                    utc_time, lon[y], lat[x]
                )
        # refl39 = Calculator(
        #     platform_name="GOES-16", instrument="abi", band="ch7"
        # )
        # data07b = refl39.reflectance_from_tbs(zenith, ch7, ch13)

        R = rec03  # banda3
        G = rec07  # banda7 con corrección zenith
        B = rec13  # banda13

        # Minimuns and Maximuns
        Rmin = 0
        Rmax = 1

        Gmin = 0
        Gmax = 0.6

        Bmin = 203
        Bmax = 323

        # Choose the gamma -> STANDARIZADAS
        gamma_R = 1
        gamma_G = 2.5
        gamma_B = 1

        # Normalize the data
        R = ((R - Rmin) / (Rmax - Rmin)) ** (1 / gamma_R)
        G = ((G - Gmin) / (Gmax - Gmin)) ** (1 / gamma_G)
        B = ((B - Bmin) / (Bmax - Bmin)) ** (1 / gamma_B)

        # Normalizamos (matplotlib lo normaliza de todas formas)
        RR = np.copy(R)
        BB = np.copy(B)
        GG = np.copy(G)

        RR[RR < 0] = 0.0
        RR[RR > 1] = 1.0
        BB[BB < 0] = 0.0
        BB[BB > 1] = 1.0
        GG[GG < 0] = 0.0
        GG[GG > 1] = 1.0

        # Create the RGB
        RGB = np.stack([R, G, B], axis=2)
        # el axis está para que el shape sea fil col dim y no dim col fil
        RRGB = np.stack([RR, GG, BB], axis=2)
        print(RGB.shape)
        return RRGB
