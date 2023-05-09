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
from ..extractors.base import NothingHereError
from ..extractors.goes import GOES16


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
    # key_list = list(band_dict.keys())
    brows, bcols = image.shape

    if col > bcols or row > brows:
        raise ValueError("Input column or row larger than image size")
    # band_vec = np.zeros((3, 3, N))

    rsize = int(trim_shape[0] / 2)
    csize = int(trim_shape[1] / 2)
    # cut
    band_vec = image[
        row - rsize : row + rsize + 1,
        col - csize : col + csize + 1,
    ].copy()

    return band_vec


def merge(
    csat_data,
    time_selected,
    goes_prod_type,
    band,
    trim_size=(3, 3),
    norm=True,
):
    """Merge data from Cloudsat with co-located data from GOES-16.

    Parameters
    ----------
    csat_data: ``extractors.cloudsat.CloudSat``
        Stratopy CloudSat fetched file.

    time_selected : str
        Time selected for downloading GOES16 object.
        It must be withing the range of the cloudsat granule start-end.
        Not inclute time zone within the str.

    goes_prod_type: str
        Type of product to download from GOES16.
        See the available list in goes_obj._PROD_PARSER.

    band: int
        Band or channel you want to download from ABI (1-16).

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
    time_zone = "UTC"
    usr_date = parser.parse(time_selected)
    zone = pytz.timezone(time_zone)
    date_in_zone = zone.localize(usr_date)
    dt_selected = date_in_zone.astimezone(pytz.UTC)

    # Checks if selected time is within cloudsat pass range
    first_time = (
        Timestamp(csat_data.time.to_numpy()[0])
        .to_pydatetime()
        .replace(tzinfo=pytz.UTC)  # noqa
    )
    last_time = (
        Timestamp(csat_data.time.to_numpy()[-1])
        .to_pydatetime()
        .replace(tzinfo=pytz.UTC)  # noqa
    )

    if dt_selected < first_time or dt_selected > last_time:
        raise NothingHereError(
            f"{dt_selected} out of range for this CloudSat track [{first_time}: {last_time}]."  # noqa
        )
    else:
        goesdata = GOES16(product_type=goes_prod_type, channel=band).fetch(
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
