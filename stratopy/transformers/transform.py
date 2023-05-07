#!/usr/bin/env python
# -*- coding: utf-8 -*-
# License: MIT (https://tldrlegal.com/license/mit-license)
# Copyright (c) 2022, Paula Romero Jure et al.
# All rights reserved.

r"""Contains methods to perform transformation operations on loaded images."""

# =============================================================================
# IMPORTS
# =============================================================================
from dateutil import parser, tz

import numpy as np

from pandas import Timestamp

import pytz

import xarray as xa

from . import coord_change
from ..extractors.base import NothingHereError
from ..extractors.goes import GOES16


# =============================================================================
# Collocations
# =============================================================================
def gen_vect(col, row, image):
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
    brows, bcols = image.shape

    if col > bcols or row > brows:
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
    dt_selected = parser.parse(time_selected).astimezone(tz.UTC)

    # Checks if selected time is within cloudsat pass range
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

    if dt_selected < first_time or dt_selected > last_time:
        raise NothingHereError(
            f"{dt_selected} out of range for this CloudSat track."
        )
    else:
        goesdata = GOES16(product_type=prod_type, channel=ch).fetch(
            time_selected
        )

    img = goesdata.CMI.to_numpy()
    # Normalize data
    if norm:
        x = img[~np.isnan(img)]  # tarda 6.3 sec
        mini = np.amin(x)  # min
        dif = np.amax(x) - mini  # max - min
        img = (img - mini) / dif

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
        imlist.append(gen_vect(cols[i], rows[i], img))

    _TRACE = np.arange(36950, dtype=np.int32)
    goes_ds = xa.Dataset(
        data_vars={"gdata": (["size", "cloudsat_trace"], imlist)},
        coords={"size": (3, 3), "cloudsat_trace": _TRACE.copy},
    )
    merged_ds = xa.merge([csat_data, goes_ds])

    return merged_ds
