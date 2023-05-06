#!/usr/bin/env python
# -*- coding: utf-8 -*-
# License: MIT (https://tldrlegal.com/license/mit-license)
# Copyright (c) 2022, Paula Romero Jure et al.
# All rights reserved.

r"""Contains methods to perform transformation operations on loaded images."""

# =============================================================================
# IMPORTS
# =============================================================================
from datetime import datetime

from dateutil import parser, tz

import numpy as np

import xarray as xa

from ..extractors.base import NothingHereError
from ..extractors.goes import GOES16
from ..utils import nearest_date


# =============================================================================
# Collocations
# =============================================================================
def gen_vect(col, row, goesdata):
    """For a given (col,row) coordinate, generates a matrix of size 3x3xN.

    The central pixel is the one located in (col, fil) coordinate.
    N should be 1 if the goes object contains one band CMI,
    N should be 3 if the goes object contains three band CMI,
    N should be 16 if goes object is a multi-band CMI.

    Parameters
    ----------
    col_row : tuple
        Column and row coordinates given as (col, row).
    band_dict : dict
        Dictionary where bands are defined.

    Returns
    -------
    array-like
        Band vector.
    """
    # key_list = list(band_dict.keys())
    image = goesdata["CMI"].to_numpy()
    brows, bcols = image.shape

    if col[0] > bcols or row[0] > brows:
        raise ValueError("Input column or row larger than image size")
    # band_vec = np.zeros((3, 3, N))

    # cut
    band_vec = image[
        row - 1 : row + 2,
        col - 1 : col + 2,
    ].copy()

    return band_vec


def merge(
    csat_data,
    time_selected,
    prod_type,
    ch,
    norm=True,
):
    """Merge data from Cloudsat with co-located data from GOES-16.

    Parameters
    ----------
    csat_data: ``extractors.cloudsat.CloudSat``
        Stratopy CloudSat fetched file.

    time_selected = str
        Time selected for downloading GOES16 object.
        It must be withing the range of the cloudsat granule start-end.
        Not inclute time zone within the str.

    prod_type:str
        Type of product to download from GOES16.

    ch: int
        Channel for downloading GOES16 file.

    norm: bool
        If True, normalizes all GOES channels [0,1].
        Default:True

    Returns
    -------
    Xarray.Dataset
        Dataset containing merged data.
    """
    dt_selected = parser.parse(time_selected)

    # Checks if selected time is within cloudsat pass range
    ts0 = (
        csat_data["time"].to_numpy()[0] - np.datetime64("1970-01-01T00:00:00Z")
    ) / np.timedelta64(1, "s")
    ts1 = (
        csat_data["time"].to_numpy()[-1]
        - np.datetime64("1970-01-01T00:00:00Z")
    ) / np.timedelta64(1, "s")
    first_time = datetime.utcfromtimestamp(ts0).astimezone(tz.UTC)
    last_time = datetime.utcfromtimestamp(ts1).astimezone(tz.UTC)

    if dt_selected < first_time or dt_selected > last_time:
        raise NothingHereError()
    else:
        goes_obj = GOES16(product_type=prod_type, channel=ch).fetch(
            time_selected
        )

    img = goes_obj.CMI.to_numpy()

    # Normalize data
    if norm:
        mini = np.amin(img[img != np.nan])  # min
        dif = np.amax(img[img != np.nan]) - mini  # max - min
        img = (img - mini) / dif

    # armar las tuplas
    scanx, scany = nearest_date.latlon2scan(
        csat_data.lat.to_numpy(), csat_data.lon.to_numpy()
    )
    cols, rows = nearest_date.scan2colfil(scanx, scany)

    # Merge
    da = xa.apply_ufunc(gen_vect, cols, rows, img)
    ds = xa.Dataset(
        data_vars=dict(da),
        coords=dict(
            lat=csat_data.lat,
            lon=csat_data.lon,
            time=csat_data.time,
        ),
        attrs=dict(description="Merged Dataset"),
    )

    return ds
