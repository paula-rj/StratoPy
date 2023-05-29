#!/usr/bin/env python
# -*- coding: utf-8 -*-
# License: MIT (https://tldrlegal.com/license/mit-license)
# Copyright (c) 2022, Paula Romero Jure et al.
# All rights reserved.
r"""Contains functions to normalize images."""

import numpy as np

from . import tbase
from stratopy import metadatatools


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

    def transform(self, sat0):
        """Transforms image to normalized [0,1] image.
        Args
        ----
            sat0 (str): satellite name as str
        Returns
        -------
            norm_image: numpy array
                Normalized image.
        """
        imager = metadatatools.instrument_type(sat0)
        if imager != "Radiometer":
            raise ValueError("Not an image")

        # Gets data
        bands = metadatatools.product_and_key(sat0)
        image_ds = sat0[bands]
        image = image_ds.to_array().to_numpy()

        # Shape must be 3D (for generalization)
        if len(bands) < 3:
            # It's data array
            image = image.reshape(1, image.shape[0], image.shape[1])

        mini = np.nanmin(image, axis=(2, 1), keepdims=True)  # min
        dif = np.nanmax(image, axis=(2, 1), keepdims=True) - mini  # max - min
        nimg = image - mini
        norm_image = np.divide(nimg, dif)

        sat0[bands] = sat0[bands].expand_dims(
            nbands=np.arange(1, image.shape[0] + 1)
        )

        return sat0.update(bands=dict((image_ds.dims, norm_image)))
