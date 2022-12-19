#!/usr/bin/env python
# -*- coding: utf-8 -*-
# License: MIT (https://tldrlegal.com/license/mit-license)
# Copyright (c) 2022, Paula Romero Jure et al.
# All rights reserved.

import xarray as xa

from . import base


class CloudSat(base.SFTPMixin, base.ConnectorABC):

    _PRODUCT_TYPES = (
        "2B-CLDCLASS.P1_R05",
        "2B-CLDCLASS.P_R04",
        "2B-CLDCLASS-LIDAR.P_R04",
    )

    def __init__(self, product_type, username, *, keyfile=None, keypass=None):
        super().__init__(username=username, keyfile=keyfile, keypass=keypass)
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
        """Gets the URL direction where all the GOES16
        files are stored. Returns the URL as str.
        """
        return "/".join(["Data", self.product_type])

    def _makequery(self, endpoint, date_time):
        """solo me importa la fecha hasta la hora, o los min a lo sumo
        hay que ver el algo de busqueda a hora mas cercana
        los min no sabemos, las pasadas son cada 2 horas aprox
        """
        date_dir = date_time.strftime("%Y/%j")
        # 2019009155049_67652_CS_2B-CLDCLASS_GRANULE_P1_R05_E08_F03.hdf
        pdate = date_time.strftime("%Y%j%H%M")
        parsed = f"{pdate}*"
        query = "/".join([endpoint, date_dir, parsed])
        return query

    def _parse_result(self, result):
        """Converts the downloaded hdf file into xarray object.

        Parameters:
        -----------
        result: the file in Bytes.
        """
        xarr = xa.open_dataset(result, engine="h5netcdf")
        return xarr
