#!/usr/bin/env python
# -*- coding: utf-8 -*-
# License: MIT (https://tldrlegal.com/license/mit-license)
# Copyright (c) 2022, Paula Romero Jure et al.
# All rights reserved.

# =============================================================================
# IMPORTS
# =============================================================================
import datetime

import numpy as np


def closest_datetime(files_array, to_search):
    """Retrieves the nearest available date to the one given as input in fetch.

    Parameters
    ----------
    arr: list or numpy array
        List or array of all the available dates.
    to_search: datetime
        Date given as input, as datetime object.

    Returns
    -------
        nearest_date: datetime object
            Nearest date to the one given as input.

    Notes
    -----
    Presicion: seconds
    """
    dates_list = [file[:11] for file in files_array]
    dt_list = np.array(
        [datetime.datetime.strptime(date, "%Y%j%H%M%S") for date in dates_list]
    )
    dt_to_search = datetime.datetime.strptime(to_search, "%Y%j%H%M%S")
    diff_abs = np.abs(dt_list - dt_to_search)
    diff_abs_seconds = [
        datetime.timedelta.total_seconds(da) for da in diff_abs
    ]

    return np.argmin(diff_abs_seconds)
