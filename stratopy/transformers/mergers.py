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

import pytz

import xarray as xa

from . import coord_change
from . import tbase
from ..extractors.ebase import NothingHereError
from stratopy import metadatatools

_TRACE = np.arange(36950, dtype=np.int32)


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
    band_vec = image[
        :,
        row - rsize : row + rsize + 1,
        col - csize : col + csize + 1,
    ].copy()

    return band_vec


class MergePolarGeos(tbase.BinaryTransformerABC):
    """
    Merges product from Polar satellite with product from a Geostationary one.

    Args
    ----
        time_selected : str
            Time selected for mergin products.
            It must be withing the range of aquisition of both instruments.

        time_zone : str
            Time zone for time selected.
            Default: UTC.

        trim_size: tuple
            Size of the 2D image to be trimmed around the central pixel.
            Default: (3,3)

        norm: bool
            If True, normalizes all GOES channels [0,1].
            Default:True

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
        time_selected,
        time_zone="UTC",
        trim_size=(3, 3),
    ):
        self.time_selected = time_selected
        self.time_zone = time_zone
        self.trim_size = trim_size

    def __repr__(self):
        """Representation for merged object."""
        return f"Mergin for {self.time_selected} at {self.time_zone}."

    def check_time(self, sat):
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
        If selected time for merging is out of bounds for Polar satellite data.
        """
        usr_date = parser.parse(self.time_selected)
        zone = pytz.timezone(self.time_zone)
        date_in_zone = zone.localize(usr_date)
        dt_selected = date_in_zone.astimezone(pytz.UTC)

        first_time = parser.parse(sat.time_coverage_start)
        last_time = parser.parse(sat.time_coverage_end)

        if (dt_selected < first_time) or (dt_selected > last_time):
            raise NothingHereError(
                f"{self.time_selected} out of range for this CloudSat track [{first_time}: {last_time}]."  # noqa
            )
        else:
            return True

    def transform(self, sat0, sat1):
        """Merge data from Cloudsat with co-located data from GOES-16.

        Parameters
        ----------
        sat0: ``xarray DataArray``
            DataArray of a file from satellite 0.

        sat1: ``xarray DataArray``
            DataArray of a file from satellite 1.
        """
        # Check type of orbit
        orb0 = metadatatools.orbit_type(sat0)
        orb1 = metadatatools.orbit_type(sat1)

        if orb0 == "polar" and orb1 == "geostationary":
            # Checks if temporal collocation is possible for usr time
            if self.check_time(sat0):
                # Products to collocate
                prodPolar = sat0
                img = sat1[metadatatools.product_key].to_numpy()
        elif orb0 == "geostationary" and orb1 == "polar":
            if self.check_time(sat0):
                prodPolar = sat1
                img = sat0[metadatatools.product_key].to_numpy()
        else:
            raise ValueError("This transformer is for geos and polar orbits.")

        # TODO: Cortar cloudsat mas alla de los 10-15 min del time selected

        # t:(lat,lon) -> (col,row)
        scanx, scany = coord_change.latlon2scan(
            prodPolar.lat.to_numpy(), prodPolar.lon.to_numpy()
        )
        cols, rows = coord_change.scan2colfil(scanx, scany)

        # Merge
        imlist = []
        for i in range(len(cols)):
            imlist.append(gen_vect(cols[i], rows[i], img, self.trim_size))

        da = xa.DataArray(
            imlist,
            dims=("cloudsat_trace", "nbands", "img_wide", "img_height"),
            coords={
                "cloudsat_trace": _TRACE.copy(),
                "nbands": np.arange(
                    1, imlist[0].shape[0] + 1, 1, dtype=np.int8
                ),
                "img_wide": np.arange(
                    1, imlist[0].shape[1] + 1, 1, dtype=np.int8
                ),
                "img_height": np.arange(
                    1, imlist[0].shape[2] + 1, 1, dtype=np.int8
                ),
            },
        )
        geos_ds = xa.Dataset({"geos": da})
        merged_ds = prodPolar.merge(geos_ds)

        return merged_ds
