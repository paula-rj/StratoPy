#!/usr/bin/env python
# -*- coding: utf-8 -*-
# License: MIT (https://tldrlegal.com/license/mit-license)
# Copyright (c) 2022, Paula Romero Jure et al.
# All rights reserved.
r"""Contains functions to normalize images."""

import numpy as np

from . import tbase
from .. import metadatatools


# class L1_norm - ver si esta en satpy
class MinMaxNormalize(tbase.UnaryTransformerABC):
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

        imager = sat0._STRATOPY_.instrument_type
        if imager != "Radiometer":
            raise ValueError("Not an image")

        # Gets image as numpy array
        image = sat0[sat0._STRATOPY_.product_key].to_numpy()

        # Shape must be 3D (for generalization)
        if len(image.shape) < 3:
            image = image.reshape(1, image.shape[0], image.shape[1])
        mini = np.nanmin(image, axis=(2, 1), keepdims=True)  # min
        dif = np.nanmax(image, axis=(2, 1), keepdims=True) - mini  # max - min
        nimg = image - mini
        norm_image = np.divide(nimg, dif)
        return norm_image
