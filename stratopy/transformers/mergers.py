#!/usr/bin/env python
# -*- coding: utf-8 -*-
# License: MIT (https://tldrlegal.com/license/mit-license)
# Copyright (c) 2022, Paula Romero Jure et al.
# All rights reserved.

r"""Contains methods to perform transformation operations on loaded images."""

# =============================================================================
# IMPORTS
# =============================================================================
from dateutil import parser

import numpy as np

from pandas import Timestamp

import pytz

import xarray as xa

from . import coord_change
from . import scalers
from . import tbase
from ..constants import STRATOPY_METADATA_KEY
from ..extractors.ebase import NothingHereError


# =============================================================================
# Collocations
# =============================================================================
def gen_vect(col, row, image, trim_shape):
    """For a given (col,row) coordinate, generates a matrix of size 3x3xN.

    The central pixel is the one located in (col, fil) coordinate.
    N should be 1 if the goes object contains one band CMI,
    N should be 3 if the goes object contains three band CMI,
    N should be 16 if goes object is a multi-band CMI.

    Parameters
    ----------
    col : int
        Column coordinate from ABI image related to CloudSat footprint.
    row : int
        Row coordinate from ABI image related to CloudSat footprint.
    img : ``numpy.array``
        ABI image as np.array.
    trim_size: tuple
        Shape of trim size arround central pixel at (row,col).

    Returns
    -------
    array-like
        Band vector.
    """
    nbands, brows, bcols = image.shape

    if col > bcols or row > brows:
        raise ValueError("Input column or row larger than image size")

    # Size of tile
    rsize = int(trim_shape[0] / 2)
    csize = int(trim_shape[1] / 2)

    # Trim
    # for i in range(image.shape[0])
    band_vec = image[  # i,
        row - rsize : row + rsize + 1,
        col - csize : col + csize + 1,
    ].copy()

    return band_vec


class Merge_Cloudsat_GOES(tbase.BinaryTransformerABC):
    """

    Args
    ----
        time_selected : str
            Time selected for downloading GOES16 object.
            It must be withing the range of the cloudsat granule start-end.
            Not inclute time zone within the str.

        time_zone : str
            Time zone.

                time_selected : str
            Time selected for downloading GOES16 object.
            It must be withing the range of the cloudsat granule start-end.
            Not inclute time zone within the str.

        trim_size: tuple
            Size of the 2D image to be trimmed around the central pixel.
            Default = (3,3)

        norm: bool
            If True, normalizes all GOES channels [0,1].
            Default:True

        Returns
        -------
        Xarray.Dataset
            Dataset containing merged data.

        Notes
        -----
        The maximum extention for img_size, ie, for how many pixels of an ABI
        image (around the central pixel) is a CPR classificatcan a CloudSat CPR
        classification accurate. However, in current works, the image size is
        squared and with a shape = (3,3).

    Methods
    -------
    transformer
        Merges sat 0 = cloudsat obj + sat 1 = goes obj.
    """

    def __init__(
        self,
        sat_xarr_0,
        sat_xarr_1,
        time_selected,
        time_zone="UTC",
        trim_size=(3, 3),
        norm=True,
    ):
        self.time_selected = time_selected
        self.time_zone = time_zone
        self.trim_size = trim_size
        self.norm = norm
        self.sat_xarr0 = sat_xarr_0
        self.sat_xarr1 = sat_xarr_1

    def __repr__(self):
        """Representation for merged object."""
        return f"{self.sat_xarr0.platform_ID}-{self.sat_xarr1.platform_ID} merged \
            for {self.time_selected}"

    def check_time(self, sat_data):
        """Checks if selected time is in cloudsat track range.

        Parameters
        ----------
        sat_data: xarray.DataArray
            Cloudsat data as a DataArray.
            To generate it: csat_obj.read_hdf4() or
            csat_obj.fetch("date and time")

        Returns
        -------
        bool

        Raise
        -----
        NothingHereError
        """
        usr_date = parser.parse(self.time_selected)
        zone = pytz.timezone(self.time_zone)
        date_in_zone = zone.localize(usr_date)
        dt_selected = date_in_zone.astimezone(pytz.UTC)

        first_time = (
            Timestamp(sat_data.time.to_numpy()[0])
            .to_pydatetime()
            .replace(tzinfo=pytz.UTC)
        )
        last_time = (
            Timestamp(sat_data.time.to_numpy()[-1])
            .to_pydatetime()
            .replace(tzinfo=pytz.UTC)
        )

        if (dt_selected < first_time) or (dt_selected > last_time):
            raise NothingHereError(
                f"{self.time_selected} out of range for this CloudSat track [{first_time}: {last_time}]."  # noqa
            )
        else:
            return True

    def transformer(self, sat0, sat1):
        """Merge data from Cloudsat with co-located data from GOES-16.

        Parameters
        ----------
        sat0: ``xarray DataArray``
            DataArray of a file from satellite 0.

        sat1: ``xarray DataArray``
            DataArray of a file from satellite 1.
        """
        # Determines if collocation is possible
        # Check type of orbit
        orb0 = self.sat_xarr0.attrs[STRATOPY_METADATA_KEY].orbit_type
        orb1 = self.sat_xarr1.attrs[STRATOPY_METADATA_KEY].orbit_type

        # Check if temporal collocation possible

        # Esto va en goes
        # if sat1.product_type == "ABI-L2-MCMIPF":
        #    img = goesdata[CH_LIST].to_array().to_numpy()
        # else:
        #    img = goesdata.CMI.to_numpy()
        #    img = img.reshape(1, img.shape[0], img.shape[1])

        # Normalize data
        if self.norm:
            img = scalers.Min_Max_Normalize(self.sat_xarr1).transformer(sat0="a")
        else:
            img = self.sat_xarray[self.sat_xarr1._STRATOPY_.prod_key].to_numpy()

        # Products to collocate
        prod0 = self.sat_xarray[self.sat_xarr0._STRATOPY_.prod_key].to_numpy()

        # TODO: Cortar cloudsat mas alla de los 10-15 min del time selected

        # t:(lat,lon) -> (col,row)
        scanx, scany = coord_change.latlon2scan(
            prod0.lat.to_numpy(), prod0.lon.to_numpy()
        )
        cols, rows = coord_change.scan2colfil(scanx, scany)

        # Merge
        imlist = []
        for i in range(len(cols)):
            imlist.append(gen_vect(cols[i], rows[i], img, self.trim_size))

        _TRACE = np.arange(36950, dtype=np.int32)
        da = xa.DataArray(
            imlist,
            dims=("cloudsat_trace", "ancho", "alto"),
            coords={
                "cloudsat_trace": _TRACE.copy(),
                "img_wide": np.arange(0, 3, 1),  # ancho
                "img_height": np.arange(0, 3, 1),  # alto
            },
        )
        goes_ds = xa.Dataset({"goes": da})
        merged_ds = prod0.merge(goes_ds)

        return merged_ds
