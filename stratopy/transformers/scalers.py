#!/usr/bin/env python
# -*- coding: utf-8 -*-
# License: MIT (https://tldrlegal.com/license/mit-license)
# Copyright (c) 2022, Paula Romero Jure et al.
# All rights reserved.
r"""Contains functions to normalize images."""

import numpy as np

from . import tbase


# class L1_norm - ver si esta en satpy
class Min_Max_Normalize(tbase.UnaryTransformerABC):
    """Normalizes image as min max.

    Args
    ----
        image: numpy array
            Image as numpy array

    Methods
    -------
    transformer
        Transforms.
    """

    def __init__(self, image):
        self.image = image

    def transformer(self, sat0):
        """Transforms image to normalized [0,1] image.

        Args
        ----
            sat0 (str): satellite name as str

        Returns
        -------
            norm_image: numpy array
                Normalized image.
        """
        # x = self.image[~np.isnan(self.image)]  # tarda 6.3 sec
        mini = np.nanmin(self.image, axis=(2, 1), keepdims=True)  # min
        dif = (
            np.nanmax(self.image, axis=(2, 1), keepdims=True) - mini
        )  # max - min
        nimg = self.image - mini
        norm_image = np.divide(nimg, dif)
        return norm_image
