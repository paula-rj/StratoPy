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

PATH = os.path.abspath(os.path.dirname(__file__))


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
        result: ``netCDF4.Dataset``
        File variables.
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

    elif len(file_path) != 1 and len(file_path) != 3:

        raise ValueError(
            "File path must be a tuple of length 1 or 3 (in case of RGB)."
        )

    data = dict()
    for paths in file_path:
        channel = paths.split("-")[3].split("_")[0]
        data[channel] = Dataset(paths, "r").variables

    return Goes(data)


@attr.s(frozen=True, repr=False)
class Goes:

    """Generates an object containing de Day Microphysics state
    according to GOES-16 manual.

    Parameters
    ----------
    data: ``netCDF4.Dataset.variables dict``
        Dictionary with variables data from each channel of the
        GOES Day Microphysics product.
    coordinates: ``tuple``  (default: cut will be south hemisphere)
        (lat_inf, lat_sup, lon_east, lon_west) where:
            lat_inf, latitude of minimal position
            lat_sup, latitude of maximal position
            lon_east, longitude of
            lon_west, longitude of
    """

    _data = attr.ib(validator=attr.validators.instance_of(dict))
    coordinates = attr.ib(default=(-40.0, 10.0, -37.0, -80.0))
    _trim_coord = attr.ib(init=False)
    RGB = attr.ib(init=False)
    img_date = attr.ib(init=False)

    def __repr__(self):
        img_date = self.img_date.strftime("%d/%m/%y-%H:%M")
        bands = [int(band.split("C")[1]) for band in self._data.keys()]
        if len(bands) == 1:
            return f"GOES Object -- {img_date}, CH={bands[0]}"
        else:
            return (
                f"GOES Object -- {img_date}, "
                f"CH={bands[0]}, {bands[1]} and {bands[2]}"
            )

    def _repr_html_(self):
        img_date = self.img_date.strftime("%d/%m/%y-%H:%M")
        bands = [int(band.split("C")[1]) for band in self._data.keys()]
        footer = "<b>-- Goes Object</b>"
        if len(bands) == 1:
            return f"<div>{img_date}, , CH={bands[0]} {footer}</div>"
        else:
            return (
                f"<div>{img_date}, , "
                f"CH={bands[0]}, {bands[1]} and {bands[2]} {footer}</div>"
            )

    @img_date.default
    def img_date_default(self):
        # Using existing channel date (same for all)
        channel_data = list(self._data.values())[0]

        # Img date in sec
        time_delta = datetime.timedelta(seconds=int(channel_data["t"][:].data))
        date_0 = datetime.datetime(year=2000, month=1, day=1, hour=12)
        return date_0 + time_delta

    @_trim_coord.default
    def _trim_coord_default(self):
        # Coordinates in deegres
        lat_inf, lat_sup, lon_east, lon_west = self.coordinates

        trim_coordinates = dict()
        for ch_id, dataset in self._data.items():
            # Extract all the variables
            metadata = dataset

            # satellite height
            h = metadata["goes_imager_projection"].perspective_point_height
            semieje_may = metadata["goes_imager_projection"].semi_major_axis
            semieje_men = metadata["goes_imager_projection"].semi_minor_axis
            lon_cen = metadata[
                "goes_imager_projection"
            ].longitude_of_projection_origin
            scale_factor = metadata["x"].scale_factor
            offset = np.array(
                [metadata["x"].add_offset, metadata["y"].add_offset]
            )

            pto_sup_izq = core.latlon2scan(
                lat_sup,
                lon_west,
                lon_cen,
                Re=semieje_may,
                Rp=semieje_men,
                h=h,
            )

            pto_inf_der = core.latlon2scan(
                lat_inf,
                lon_east,
                lon_cen,
                Re=semieje_may,
                Rp=semieje_men,
                h=h,
            )

            c0, r0 = core.scan2colfil(
                pto_sup_izq[1],
                pto_sup_izq[0],
                offset[0],
                offset[1],
                scale_factor,
                1,
            )
            c1, r1 = core.scan2colfil(
                pto_inf_der[1],
                pto_inf_der[0],
                offset[0],
                offset[1],
                scale_factor,
                1,
            )

            trim_coordinates[ch_id] = (r0, r1, c0, c1)

        return trim_coordinates

    def trim(self, for_RGB=True):
        """
        This function trims a GOES CMI image according to the width, height
        max west longitude and upper latitude specified on the parameters.
        Default parameters are set to return a South America image.
        Parameters
        ----------

        Returns
        -------
        trim_img: ``numpy.array`` containing the trimmed image.
        """
        trim_img = dict()
        for ch_id, dataset in self._data.items():
            image = np.array(
                dataset["CMI"][:].data
            )  # Extract image to np.array
            N = 5424  # Image size for psize=2000 m
            esc = N / image.shape[0]
            r0, r1, c0, c1 = self._trim_coord[ch_id]
            trim_img[ch_id] = image[r0:r1, c0:c1]

            # Rescale channels with psize = 1000 m
            if for_RGB and ch_id == "M3C03":
                x = range(0, trim_img[ch_id][:].shape[1])
                y = range(0, trim_img[ch_id][:].shape[0])
                f = interpolate.interp2d(x, y, trim_img[ch_id], kind="cubic")
                xnew = np.arange(x[0], x[-1] + 1, (x[1] - x[0]) / esc)
                ynew = np.arange(y[0], y[-1], (y[1] - y[0]) / esc)
                trim_img[ch_id] = f(xnew, ynew)

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
        Returns
        -------
        data2b: ``numpy.array``
            Zenith calculation for every pixel.
        """
        # Construct paths
        latitude_path = os.path.join(PATH, "lat_vec.npy")
        longitude_path = os.path.join(PATH, "lon_vec.npy")

        #
        r0, r1, c0, c1 = self._trim_coord["M3C07"]
        lat = np.load(latitude_path)[r0:r1]
        lon = np.load(longitude_path)[c0:c1]

        # Calculate the solar zenith angle
        utc_time = datetime.datetime(2019, 1, 2, 18, 00)
        LON, LAT = np.meshgrid(lon, lat)
        zenith = astronomy.sun_zenith_angle(utc_time, LON, LAT)
        refl39 = Calculator(
            platform_name="GOES-16", instrument="abi", band="ch7"
        )
        data2b = refl39.reflectance_from_tbs(zenith, ch7, ch13)
        return data2b

    @RGB.default
    def _RGB_default(self, masked=False):
        """
        This function creates an RGB image that represents the day microphysics
        according to the GOES webpage manual.

        goes_obj.RGB() tira la imagen en np array recortada, corregida

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
        # Starts with all channels trimmed images
        trimmed_img = self.trim()

        if len(trimmed_img) == 1:
            return trimmed_img.values()
        else:
            # Asign color to bands and make zenith correction on band 7.
            R = trimmed_img["M3C03"]
            G = self.solar7(trimmed_img["M3C07"], trimmed_img["M3C13"])
            B = trimmed_img["M3C13"]

            # Minimuns and Maximuns
            Rmin = 0
            Rmax = 1

            Gmin = 0
            Gmax = 0.6

            Bmin = 203
            Bmax = 323

            # Normalize the data and copying
            R = (R - Rmin) / (Rmax - Rmin)
            G = ((G - Gmin) / (Gmax - Gmin)) ** 0.4
            B = (B - Bmin) / (Bmax - Bmin)

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

            if masked is True:
                RRGB = mask(RRGB)

            return RRGB

    def to_dataframe(self, goes_obj, **kwargs):
        # NO estoy segura que deberia tomar,
        # creo que nada! directamente que a un goes recortado lo trasforme a df
        # Tendria que probarlo para ver bien
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

        rgb_df = pd.DataFrame(goes_obj)

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
