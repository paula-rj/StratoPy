import datetime
import os

import attr

from netCDF4 import Dataset

import numpy as np

import pandas as pd

from pyorbital import astronomy

from pyspectral.near_infrared_reflectance import Calculator

from scipy import interpolate

from . import core

path = os.path.abspath(os.path.dirname(__file__))


def read_nc(file_path):
    """
    Reads netCDF files through the netCDF4 library.

    Parameters
    ----------
    file_path: ``str tuple``
        Contains a file path of one or all three paths of
        channels 3, 7 and 13 of the CMIPF GOES-16 product.

    Returns
    -------
    result: ``CloudFrame``
        File variables.

    Examples
    --------
    For only channel
        >>> nc_file = read_nc((PATH_CHANNEL_3,))

    For three channels
    >>> PATH_CHANNEL_3 = (
        "data/GOES16/"
        "OR_ABI-L2-CMIPF-M3C03_G16_s20190021800363_e20190021811129_\
        c20190021811205.nc"
    )
    >>> PATH_CHANNEL_7 = (
        "data/GOES16/"
        "OR_ABI-L2-CMIPF-M3C07_G16_s20190021800363_e20190021811141_"
        "c20190021811202.nc"
    )
    >>>PATH_CHANNEL_13 = (
        "data/GOES16/"
        "OR_ABI-L2-CMIPF-M3C13_G16_s20190021800363_e20190021811141_"
        "c20190021811221.nc"
    )

    >>> FILE_PATH = (PATH_CHANNEL_3, PATH_CHANNEL_7, PATH_CHANNEL_13)

    >>> nc_file = read_nc(FILE_PATH)

    """
    # Open netcdf file and extract variables

    if len(file_path) == 3:
        # Check for date and product consistency
        files_date = [
            band_path.split("s20", 1)[1].split("_", 1)[0]
            for band_path in file_path
        ]

        # Create boolean for consistency evaluation
        eq_dates = all(date == files_date[0] for date in files_date)
        eq_product = all("L2-CMIPF" in path for path in file_path)

        if not eq_dates:
            raise ValueError("Start date's from all files should be the same.")
        elif not eq_product:
            raise ValueError("Files must be from the same product.")

    elif len(file_path) == 1:
        pass

    else:
        raise ValueError(
            "File path must be a tuple of length 1 or 3 (in case of RGB)."
        )

    for paths in file_path:
        data = Dataset(paths, "r")
        result = data.variables
        # Falta ver acá como lo devolvemos,
        # Creo que lo mejor es un dict

    return TreatGOES(result)


@attr.s(frozen=True, repr=False)
class GoesDataFrame:
    """Generates an object containing de Day Microphysics state
    according to GOES-16 manual.

    Parameters
    ----------
    data: data from netcdf file. Dataset(file_path).variables
    """

    _df = attr.ib(
        validator=attr.validators.instance_of(pd.DataFrame),
        converter=pd.DataFrame,
    )

    def __getattr__(self, a):
        return getattr(self._df, a)

    def __dir__(self):
        return super().__dir__() + dir(self._df)

    def __getitem__(self, slice):
        return self._df.__getitem__(slice)

    def __repr__(self):
        # original = repr(self._df)
        time_delta = datetime.timedelta(
            seconds=int(self._df["t"][:].data)
        )  # img date in sec
        date0 = datetime.datetime(year=2000, month=1, day=1, hour=12)
        img_date = (date0 + time_delta).strftime("%d/%m/%y-%H:%M")
        return f"GoesDataFrame -- {img_date} "

    def _repr_html_(self):
        original = self._df._repr_html_()
        footer = "<b>-- GoesDataFrame</b>"
        return f"<div>{original}{footer}</div>"


class TreatGOES:
    def __init__(
        self, data, rows=2891, cols=1352, lat_sup=10.0, lon_west=-80.0
    ):
        self._data = data
        self.rows = rows
        self.cols = cols
        self.lat_sup = lat_sup
        self.lon_west = lon_west

    def _trim_coord(_data, lat_sup, lon_west, cols, rows):
        # Extract all the variables
        metadata = _data

        # satellite height
        h = metadata["goes_imager_projection"].perspective_point_height
        semieje_may = metadata["goes_imager_projection"].semi_major_axis
        semieje_men = metadata["goes_imager_projection"].semi_minor_axis
        lon_cen = metadata[
            "goes_imager_projection"
        ].longitude_of_projection_origin
        image = np.asarray(metadata["CMI"][:].data)

        pto_sup_izq = core.latlon2scan(
            lat_sup,
            lon_west,
            lon_cen,
            Re=semieje_may,
            Rp=semieje_men,
            h=h,
        )
        x0 = pto_sup_izq[1] * h
        y0 = pto_sup_izq[0] * h

        psize = 2000  # Pixel size in meters
        N = 5424  # Image size for psize=2000 m
        esc = N / image.shape[0]

        # Goes trimed image size
        Nx = int(cols / esc)  # Number of points in x
        Ny = int(rows / esc)  # Number of points in y
        r0 = int(
            (-y0 / psize + N / 2 - 1.5) / esc
        )  # fila del angulo superior izquierdo
        # columna del angulo superior izquierdo
        c0 = int((x0 / psize + N / 2 + 0.5) / esc)
        r1 = int(r0 + Ny)  # fila del angulo inferior derecho
        c1 = int(c0 + Nx)  # columna del angulo inferior derecho
        return r0, r1, c0, c1

    def trim(self, for_RGB=True):
        """
        This function trims a GOES CMI image according to the width, height
        max west longitude and upper latitude specified on the parameters.
        Default parameters are set to return a Southamerica image

        Parameters
        ----------
        data_path: ``str``
            Path to GOES CMI image.
        rows: ``int``
            Height of the trimmed image in pixels.
            0<rows<5424
        cols: ``int``
            Height of the trimmed image in pixels.
            0<cols<5424
        lon_west: ``float``
            Maximum longitude to the west.
        lat_sup: ``float``
            Maximum upper latitude.

        Returns
        -------
        trim_img: ``numpy.array`` containing the trimmed image.

        """
        metadata = self._data
        band = int(metadata["band_id"][:].data[0])  # Channel number
        # Extract image to np.array
        image = np.asarray(metadata["CMI"][:].data)
        N = 5424  # Image size for psize=2000 m
        esc = N / image.shape[0]
        r0, r1, c0, c1 = TreatGOES._trim_coord(
            self._data, self.lat_sup, self.lon_west, self.cols, self.rows
        )
        trim_img = image[r0:r1, c0:c1]

        # Rescale channels with psize = 1000 m
        if for_RGB and band == 3:
            x = range(0, trim_img.shape[1])
            y = range(0, trim_img.shape[0])
            f = interpolate.interp2d(x, y, trim_img, kind="cubic")
            xnew = np.arange(x[0], x[-1], (x[1] - x[0]) / esc)
            ynew = np.arange(y[0], y[-1], (y[1] - y[0]) / esc)
            trim_img = f(xnew, ynew)

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
        r0, r1, c0, c1 = TreatGOES._trim_coord(
            self._data, self.lat_sup, self.lon_west, self.cols, self.rows
        )
        lat = np.load(path / "lat_vec.npy")[r0:r1]
        lon = np.load(path / "lon_vec.npy")[c0:c1]

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

    def RGB(self, rec03, rec07, rec13, masked=False):
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
        masked: bool
            If True, returns a masked RGB
            according to day MP quick guide

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

        # Choose the gamma -> STANDARIZED
        gamma_R = 1
        gamma_G = 2.5
        gamma_B = 1

        # Normalize the data and copying
        R = ((R - Rmin) / (Rmax - Rmin)) ** (1 / gamma_R)
        G = ((G - Gmin) / (Gmax - Gmin)) ** (1 / gamma_G)
        B = ((B - Bmin) / (Bmax - Bmin)) ** (1 / gamma_B)

        RR = np.copy(R)
        BB = np.copy(B)
        GG = np.copy(G)

        RR[RR < 0] = 0.0
        RR[RR > 1] = 1.0
        BB[BB < 0] = 0.0
        BB[BB > 1] = 1.0
        GG[GG < 0] = 0.0
        GG[GG > 1] = 1.0

        # Create the norm RGB
        RRGB = np.stack([RR, GG, BB], axis=2)

        return RRGB

    def to_dataframe(self):
        """Returns a GOES dataframe containing Latitude and Longitude for
        every pixel of a GOES full disk image, and the value of the pixel,
        from a numpy array.

        Parameters
        ----------
        None

        Returns
        -------
        rgb_df: Pandas DataFrame

        """
        return GoesDataFrame(self.RGB)


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
