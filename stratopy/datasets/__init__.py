#!/usr/bin/env python
# -*- coding: utf-8 -*-
# License: MIT (https://tldrlegal.com/license/mit-license)
# Copyright (c) 2022, Paula Romero Jure et al.
# All rights reserved.

import functools
import os
import pathlib


import pandas as pd


PATH = pathlib.Path(os.path.abspath(os.path.dirname(__file__)))


@functools.lru_cache(maxsize=None)
def load_goes_latlon_ctable():
    return pd.read_json(PATH / "goes_latlong_convertion_table.json")
