import re
from datetime import datetime

from netCDF4 import Dataset

import numpy as np

import pandas as pd

from pyorbital import astronomy

from pyspectral.near_infrared_reflectance import Calculator

from scipy import interpolate

from . import core


def read_nc(file_path):

    """
    Reads netCDF files.
    Parameters
    ----------
    file_path: ``str tuple``
        Tuple of length three containing the paths of the channels 3, 7
        and 13 of the CMIPF GOES-16 product.

    Returns
    -------
    metadat: File variables.

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
        This function trims a GOES CMI image according to the width, height
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
        trim_img: ``numpy.array`` containing the trimmed image.

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

        pto_sup_izq = core.latlon2scan(
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
        Ny = int(rows / esc)  # numero de puntos del recorte en y
        self.f0 = int(
            (-y0 / psize + N / 2 - 1.5) / esc
        )  # fila del angulo superior izquierdo
        self.c0 = int(
            (x0 / psize + N / 2 + 0.5) / esc
        )  # columna del angulo superior izquierdo
        self.f1 = int(self.f0 + Ny)  # fila del angulo inferior derecho
        self.c1 = int(self.c0 + Nx)  # columna del angulo inferior derecho

        trim_img = image[self.f0:self.f1, self.c0:self.c1]
        return trim_img

    def solar7(self, ch7, ch13):
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
        lat = np.load(
            "/home/pola/.virtualenvs/stratopy/StratoPy/stratopy/lat_vec.npy"
        )[self.f0:self.f1]
        lon = np.load(
            "/home/pola/.virtualenvs/stratopy/StratoPy/stratopy/lat_vec.npy"
        )[self.c0:self.c1]

        zenith = np.zeros((ch7.shape[0], ch7.shape[1]))
        # Calculate the solar zenith angle
        utc_time = datetime(self.julian_date[:4], 1, 2, self.utc_hour, 00)
        for x in range(len(self.lat)):
            for y in range(len(self.lon)):
                zenith[x, y] = astronomy.sun_zenith_angle(
                    utc_time, lon[y], lat[x]
                )
        refl39 = Calculator(
            platform_name="GOES-16", instrument="abi", band="ch7"
        )
        data2b = refl39.reflectance_from_tbs(zenith, ch7, ch13)
        return data2b

    def RGB(self, rec03, rec07, rec13):
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
        self.RRGB = np.stack([RR, GG, BB], axis=2)
        print(RGB.shape)
        return self.RRGB

    def to_dataframe(self, rec):

        """Returns a pandas dataframe containing Latitude and Longitude for
        every pixel of a GOES full disk image, and the value of the pixel,
        from a numpy array.

        Parameters
        ----------
        None

        Returns
        -------
        rgb_df: Pandas DataFrame

        """
        lat = np.load(
            "/home/pola/.virtualenvs/stratopy/StratoPy/stratopy/lat_vec.npy"
        )[self.f0:self.f1]
        lon = np.load(
            "/home/pola/.virtualenvs/stratopy/StratoPy/stratopy/lat_vec.npy"
        )[self.c0:self.c1]

        rgb_df = pd.DataFrame({"Latitude": lat, "Longitude": lon})

        return rgb_df


def mask(rgb):
    """This function returns a labeled-by-color image according to
    the interpretation of the product Day Microphysics
    (https://weather.msfc.nasa.gov/sport/training/quickGuides/
    rgb/QuickGuide_DtMicroRGB_NASA_SPoRT.pdf)

    Parameters:
    -----------
    rgb: numpy array
    Numpy Array object containig the Day Microphysics RGB product

    Returns:
    -------
    img_mask: numpy array
    Masked RGB

    """

    img_mask = np.zeros(rgb.shape)

    # Large drops, Low clouds-> pink/magenta
    lc_rfilter = rgb[:, :, 0] > 0.7  # R>0.8
    lc_gfilter = rgb[:, :, 1] < 0.4  # G
    lc_bfilter = rgb[:, :, 2] > 0.6  # B
    lc_filter = lc_rfilter * lc_gfilter * lc_bfilter
    # Mask= magenta
    img_mask[lc_filter, 0] = 1.0
    img_mask[lc_filter, 1] = 0.0
    img_mask[lc_filter, 2] = 1.0

    # Stratus/Stratoculumus (small drops, low clouds) -> bright green/blue
    st_rfilter = (rgb[:, :, 0] > 0.3) * (rgb[:, :, 0] < 0.45)  # R
    st_gfilter = (rgb[:, :, 1] > 0.5) * (rgb[:, :, 1] < 0.8)  # G
    st_bfilter = rgb[:, :, 2] < 0.7
    st_filter = st_rfilter * st_gfilter * st_bfilter
    # Mask=Light blue
    img_mask[st_filter, 0] = 0.0
    img_mask[st_filter, 1] = 1.0
    img_mask[st_filter, 2] = 1.0

    # CumuloNimbis (high clouds) -> red, dark orange
    cb_rfilter = rgb[:, :, 0] > 0.7  # R
    cb_gfilter = rgb[:, :, 1] < 0.3  # G
    cb_bfilter = rgb[:, :, 2] < 0.3  # B
    cb_filter = cb_rfilter * cb_gfilter * cb_bfilter
    # Mask=Red
    img_mask[cb_filter, 0] = 1.0
    img_mask[cb_filter, 1] = 0.0
    img_mask[cb_filter, 2] = 0.0

    # Cirrus (high clouds)-> green, dark green
    cr_rfilter = rgb[:, :, 0] < 0.3  # R
    cr_gfilter = rgb[:, :, 1] > 0.7  # G
    cr_bfilter = rgb[:, :, 2] < 0.3  # B
    cr_filter = cr_rfilter * cr_gfilter * cr_bfilter
    # Mask= Green
    img_mask[cr_filter, 0] = 0.0
    img_mask[cr_filter, 1] = 1.0
    img_mask[cr_filter, 2] = 0.0

    # supercooled clouds Thick, small drops, medium clouds-> yellow
    super_rfilter = rgb[:, :, 0] > 0.8
    super_gfilter = rgb[:, :, 1] > 0.8
    super_bfilter = rgb[:, :, 2] < 0.2  # amarillo
    super_filter = super_rfilter * super_gfilter * super_bfilter
    # Mask=Yellow
    img_mask[super_filter, 0] = 1.0
    img_mask[super_filter, 1] = 1.0
    img_mask[super_filter, 2] = 0.0

    return img_mask[:, :, [0, 1, 2]]
