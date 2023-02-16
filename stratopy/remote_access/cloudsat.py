#!/usr/bin/env python
# -*- coding: utf-8 -*-
# License: MIT (https://tldrlegal.com/license/mit-license)
# Copyright (c) 2022, Paula Romero Jure et al.
# All rights reserved.

import numpy as np
import xarray as xa
from pyhdf.HDF import HDF, HC
from pyhdf.VS import VS
from pyhdf.SD import SD

from . import base


class CloudSat(base.SFTPMixin, base.ConnectorABC):
    """
    Object created by retrieving products from CloudSat satellite.

    Attributes
    ----------
    product_type: str
        Type of product to be downloaded. Currently 3 available.
    username: str
        username at CloudSat server
        https://www.cloudsat.cira.colostate.edu/
    keyfile:
        Key for
        Default = None
    keypass: str
        Password for you ssh key. You may not have any.
        Default = None
    """

    _PRODUCT_TYPES = (
        "2B-CLDCLASS.P1_R05",
        "2B-CLDCLASS.P_R04",
        "2B-CLDCLASS-LIDAR.P_R04",
    )

    _CLOUDSAT_HOST, _CLOUDSAT_PORT = "www.cloudsat.cira.colostate.edu", 22

    def __init__(self, product_type, username, *, keyfile=None, keypass=None):
        super().__init__(
            host=self._CLOUDSAT_HOST,
            port=self._CLOUDSAT_PORT,
            username=username,
            keyfile=keyfile,
            keypass=keypass,
        )
        self.product_type = product_type

        if product_type not in self._PRODUCT_TYPES:
            raise ValueError(
                "Invalid product type. "
                f"Expected one of: {self._PRODUCT_TYPES}. "
                f"Found {product_type!r}"
            )

    def __repr__(self):
        return f"<CloudSat product_type={self.product_type!r}>"

    def get_endpoint(self):
        """Gets the directory direction where all the CloudSat
        files are stored in the SFTP. Returns the URL as str.
        """
        return "/".join(["Data", self.product_type])

    def _makequery(self, endpoint, date_time):
        """Builds the whole query needed to download the product
        from Cloudsat server.

        Parameters
        ----------
        endpoint: str
            directory where CloudSAT products are stored.
        date_time: datetime obj
            the requested date and time.
            It should contain year, month, day and hour.
        """
        date_dir = date_time.strftime("%Y/%j")
        # 2019009155049_67652_CS_2B-CLDCLASS_GRANULE_P1_R05_E08_F03.hdf
        pdate = date_time.strftime("%Y%j%H%M") + "*"
        query = "/".join([endpoint, date_dir, pdate])
        return query

    def _parse_result(self, result):
        """Converts the downloaded hdf file into xarray object.

        Parameters:
        -----------
        result: Binary file-like object.
        """
        hdf_file = HDF(result, HC.READ)
        vs = VS(hdf_file)

        vd_lat = vs.attach("Latitude")
        lat_data = vd_lat[:]
        vd_lat.detach()

        vd_lon = vs.attach("Longitude")
        lon_data = vd_lon[:]
        vd_lon.detach()

        np_arr = np.array([lon_data, lat_data])
        shape = np_arr.shape[:1]
        np_arr = np.reshape(np_arr, shape)
        xarr = xa.DataArray(np_arr, dims=("lon", "lat"))

        return xarr
