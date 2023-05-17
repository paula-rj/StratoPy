#!/usr/bin/env python
# -*- coding: utf-8 -*-
# License: MIT (https://tldrlegal.com/license/mit-license)
# Copyright (c) 2022, Paula Romero Jure et al.
# All rights reserved.
import numpy as np
from stratopy.transformers import scalers

FAKE_IMG = np.random.randint(0, 255, size=(16, 3, 3))


def test_min_max_normalize():
    result = scalers.Min_Max_Normalize(FAKE_IMG).transformer(sat0="goes16")
    np.testing.assert_array_less(result, 1.1)