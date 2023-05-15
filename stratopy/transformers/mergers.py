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
from ..extractors.ebase import NothingHereError
from . import tbase

CH_LIST = [
    "CMI_C01",
    "CMI_C02",
    "CMI_C03",
    "CMI_C04",
    "CMI_C05",
    "CMI_C06",
    "CMI_C07",
    "CMI_C08",
    "CMI_C09",
    "CMI_C10",
    "CMI_C11",
    "CMI_C12",
    "CMI_C13",
    "CMI_C14",
    "CMI_C15",
    "CMI_C16",
]


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
    brows, bcols = image.shape

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
    """Merger.

    Args
    ----
        time_selected : str
            Time selected for downloading GOES16 object.
            It must be withing the range of the cloudsat granule start-end.
            Not inclute time zone within the str.

        time_zone : str
            Time zone.

    Methods
    -------
    transformer
        Merges sat 0 = cloudsat obj + sat 1 = goes obj.
    """

    def __init__(self, time_selected, time_zone="UTC"):
        usr_date = parser.parse(time_selected)
        zone = pytz.timezone(time_zone)
        date_in_zone = zone.localize(usr_date)
        dt_selected = date_in_zone.astimezone(pytz.UTC)
        self.dt_selected = dt_selected

    def __repr__(self) -> str:
        """Representation for merged object."""
        return super().__repr__()

    def transformer(self, sat0, sat1, trim_size=(3, 3), norm=True):
        """Merge data from Cloudsat with co-located data from GOES-16.

        Parameters
        ----------
        sat0: ``extractors.cloudsat.CloudSat``
            Stratopy CloudSat fetched file.

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
        The maximum extention for img_size, ie, for how many pixels of an ABI image
        (around the central pixel) is a CPR classificatcan a CloudSat CPR
        classification accurate. However, in current works, the image size is
        squared and with a shape = (3,3).
        """
        csat_data = sat0.fetch(self.dt_selected)

        # Checks if selected time is within cloudsat track range
        first_time = (
            Timestamp(csat_data.time.to_numpy()[0])
            .to_pydatetime()
            .replace(tzinfo=pytz.UTC)
        )
        last_time = (
            Timestamp(csat_data.time.to_numpy()[-1])
            .to_pydatetime()
            .replace(tzinfo=pytz.UTC)
        )

        if (self.dt_selected < first_time) or (self.dt_selected > last_time):
            raise NothingHereError(
                f"{self.dt_selected} out of range for this CloudSat track [{first_time}: {last_time}]."  # noqa
            )
        else:
            goesdata = sat1.fetch(self.dt_selected)

        if sat1.product_type == "ABI-L2-MCMIPF":
            img = goesdata[CH_LIST].to_array().to_numpy()
        else:
            img = goesdata.CMI.to_numpy().reshape(
                1, img.shape[0], img.shape[1]
            )

        # Normalize data
        if norm:
            img = scalers.min_max_norm(img)

        # TODO: Cortar cloudsat mas alla de los 10-15 min del time selected
        # TODO: Cortar algo de goes alrededor del cloudsat
        # t:(lat,lon) -> (col,row)
        scanx, scany = coord_change.latlon2scan(
            csat_data.lat.to_numpy(), csat_data.lon.to_numpy()
        )
        cols, rows = coord_change.scan2colfil(scanx, scany)

        # Merge
        imlist = []
        for i in range(len(cols)):
            imlist.append(gen_vect(cols[i], rows[i], img, trim_size))

        _TRACE = np.arange(36950, dtype=np.int32)
        da = xa.DataArray(
            imlist,
            dims=("cloudsat_trace", "ancho", "alto"),
            coords={
                "cloudsat_trace": _TRACE.copy(),
                "ancho": np.arange(0, 3, 1),
                "alto": np.arange(0, 3, 1),
            },
        )
        goes_ds = xa.Dataset({"goes": da})
        merged_ds = csat_data.merge(goes_ds)

        return merged_ds
