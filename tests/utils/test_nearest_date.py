#!/usr/bin/env python
# -*- coding: utf-8 -*-
# License: MIT (https://tldrlegal.com/license/mit-license)
# Copyright (c) 2022, Paula Romero Jure et al.
# All rights reserved.

# =============================================================================
# IMPORTS
# =============================================================================
import dateutil

from stratopy.utils import util_funcs


DATE = dateutil.parser.parse("2019 jan 09 16:00")

fake_files_list = [
    "2019009155049_67652_CS_2B-CLDCLASS_GRANULE_P1_R05_E08_F03.hdf",
    "2019009150042_67652_CS_2B-CLDCLASS_GRANULE_P1_R05_E08_F03.hdf",
    "2019009161802_67652_CS_2B-CLDCLASS_GRANULE_P1_R05_E08_F03.hdf",
]


def test_closest_datetime():
    pattern_to_search = DATE.strftime("%Y%j%H%M")
    tested = util_funcs.closest_datetime(fake_files_list, pattern_to_search)
    assert tested == 0
