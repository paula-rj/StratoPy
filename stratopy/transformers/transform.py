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
import xarray
from ..utils import nearest_date
from ..extractors.base import NothingHereError
from ..extractors.goes import GOES16


def gen_vect(col_row, band_dict):
    """Generate 3D vector.

    For a given (col,row) coordinate, generates a matrix of size 3x3xN
    where the central pixel is the one located in (col, fil) coordinate.
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
    key_list = list(band_dict.keys())
    brows, bcols = band_dict.get(key_list[0]).shape

    if col_row[0] > bcols or col_row[1] > brows:
        raise ValueError("Input column or row larger than image size")
    band_vec = np.zeros((3, 3, len(band_dict)))

    # cut
    for count, band in enumerate(band_dict.values()):
        band_vec[:, :, count] = band[
            col_row[1] - 1 : col_row[1] + 2,
            col_row[0] - 1 : col_row[0] + 2,
        ].copy()

    return np.array(band_vec)


def merge(
    cloudsat_obj,
    date_time,
    prod_type,
    all_layers=False,
    no_clouds=False,
    norm=True,
):
    """Merge data from Cloudsat with co-located data from GOES-16.

    Parameters
    ----------
    cloudsat_obj: ``extractors.cloudsat.CloudSat``
        Stratopy CloudSat object.

    date_time = str
        date and time selected for downloading GOES16 object.

    all_layers: bool
        If True, the final dataframe should include
        all layers of the CLDCLASS product.
        Default: False

    no_clouds: bool
        If Ture, the final dataframe should include
        coordinates where no clouds were detected by CloudSat.
        Default: False

    norm: bool
        If True, normalizes all GOES channels [0,1].
        Default:True

    Returns
    -------
    Xarray.Dataset
        Dataset containing merged data.
    """
    dt_selected = parser.parse(date_time)
    granule_range = cloudsat_obj["time"][0], cloudsat_obj["time"][-1]
    if dt_selected < granule_range[0] or dt_selected > granule_range[1]:
        raise NothingHereError
    else:
        goes_date = nearest_date.closest_datetime()
        goes_obj = GOES16(product_type=prod_type, channel=16).fetch(goes_date)

    # recorte
    # merge
    # return
    band_dict = {}
    for key, band in goes_obj._data.items():
        img = np.array(band["CMI"][:].data)
        # Normalize data
        if norm:
            mini = np.amin(img[img != 65535.0])  # min
            dif = np.amax(img[img != 65535.0]) - mini  # max - min
            img = (img - mini) / dif
        band_dict.update({key: img})

    # Cloudsat
    if all_layers is False:
        cloudsat_obj = cloudsat_obj.drop(
            [
                "layer_1",
                "layer_2",
                "layer_3",
                "layer_4",
                "layer_5",
                "layer_6",
                "layer_7",
                "layer_8",
                "layer_9",
            ],
            axis=1,
        )
    if no_clouds is False:
        cloudsat_obj = cloudsat_obj[cloudsat_obj.layer_0 != 0]

    cloudsat_obj["col_row"] = cloudsat_obj.apply(
        lambda x: scan2colfil(
            latlon2scan(x.Latitude, x.Longitude),
        ),
        axis=1,
    )

    # Merge
    cloudsat_obj["goes_vec"] = cloudsat_obj.apply(
        lambda x: gen_vect(x.col_row, band_dict), axis=1
    )

    return cloudsat_obj
