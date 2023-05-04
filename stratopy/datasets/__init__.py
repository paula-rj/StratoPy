#!/usr/bin/env python
# -*- coding: utf-8 -*-
# License: MIT (https://tldrlegal.com/license/mit-license)
# Copyright (c) 2022, Paula Romero Jure et al.
# All rights reserved.
r"""Init file for datasets."""

import functools
import os
import pathlib


import pandas as pd


PATH = pathlib.Path(os.path.abspath(os.path.dirname(__file__)))  # noqa


@functools.lru_cache(maxsize=None)
def load_goes_latlon_ctable():
    """Loads the conversion table for every pixel of GOES16.

    Returns the json as a Pandas Dataframe.
    """
    return pd.read_json(PATH / "goes_latlong_convertion_table.json")
