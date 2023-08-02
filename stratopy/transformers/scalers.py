#!/usr/bin/env python
# -*- coding: utf-8 -*-
# License: MIT (https://tldrlegal.com/license/mit-license)
# Copyright (c) 2022, Paula Romero Jure et al.
# All rights reserved.
r"""Contains functions to normalize images."""

import numpy as np

import xarray as xa

from . import tbase


class MinMaxNormalize(tbase.UnaryTransformerABC):
    """Normalizes image within an Xarray as min=0,  max=1.

    Methods
    -------
    transformer:
        Transforms Xarray image to normalized image returning same Xarray.
    """

    def transform(self, sat0):
        """Transforms image within an xarray to normalized [0,1] image.

        Parameters
        ----------
            sat0: ``Xarray.Dataset``
                Dataset containig an image and mandatory Metadata.

        Returns
        -------
            norm_image: ``Xarray.Dataset``
                The same Dataset containig the Normalized image.

                It also adds a new dimension "bands".
        """
        imager = sat0.instrument_type
        if imager != "Radiometer":
            raise ValueError("Not an image in Xarray")

        bands = sat0.product_key
        image_ds = sat0.data[bands]  # Gets product data

        if type(image_ds) == xa.core.dataarray.DataArray:
            image = image_ds.variable.to_numpy()
        elif type(image_ds) == xa.core.dataset.Dataset:
            image = image_ds.to_array().to_numpy()

        dimslist = [x for x in image_ds.dims]
        # Shape must be 3D (for generalization)
        if len(image.shape) < 3:
            image = image.reshape(1, image.shape[0], image.shape[1])
        if len(dimslist) < len(image.shape):
            sat0.data[bands] = sat0.data[bands].expand_dims(
                nbands=np.arange(1, image.shape[0] + 1)
            )
            dimslist = ["nbands"] + dimslist

        mini = np.nanmin(image, axis=(2, 1), keepdims=True)  # min
        dif = np.nanmax(image, axis=(2, 1), keepdims=True) - mini  # max - min
        nimg = image - mini
        norm_image = np.divide(nimg, dif)

        da = xa.DataArray(norm_image, dims=dimslist)

        if type(bands) == list:
            for i in range(len(bands)):
                sat0.data.update({bands[i]: da[i, :, :]})
        else:
            sat0.data.update({bands: da})

        return sat0
