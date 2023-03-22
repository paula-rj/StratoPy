#!/usr/bin/env python
# -*- coding: utf-8 -*-
# License: MIT (https://tldrlegal.com/license/mit-license)
# Copyright (c) 2022, Paula Romero Jure et al.
# All rights reserved.

# =============================================================================
# IMPORTS
# =============================================================================
import numpy as np

from pyhdf.HDF import HC, HDF
from pyhdf.SD import SD, SDC
from pyhdf.VS import VS

import xarray as xa

from . import base

_TRACE = np.arange(36950, dtype=np.int32)
_LAYERS = np.arange(10, dtype=np.int8)


def read_hdf4(path):
    """Reads a HDF-EOS file from CloudSat
    and returns it as an Xarray Dataset

    Parameters
    ----------
    path: str or Path
        Path where the file is stored

    Returns
    -------
    ds: Xarray Dataset
        Dataset containing the most relevant coordinates
        and attributes of a 2B-CLDCLASS file."""
    sd_file = SD(path, SDC.READ)
    height = sd_file.select("Height").get()
    cloud_scenario = sd_file.select("cloud_scenario").get()
    cloudLayerBase = sd_file.select("CloudLayerBase").get()
    cloudLayerTop = sd_file.select("CloudLayerTop").get()
    cloudLayerType = sd_file.select("CloudLayerType").get().astype("int8")

    # HDF
    hdf_file = HDF(path, HC.READ)
    vs = VS(hdf_file)

    # Important attributes, one number only
    vd_UTCstart = vs.attach("UTC_start")
    UTCstart = vd_UTCstart[:]
    vd_UTCstart.detach()

    vd_verticalBin = vs.attach("Vertical_binsize")
    vertical_Binsize = np.array(vd_verticalBin[:]).flatten()
    vd_verticalBin.detach()

    # geolocated data, 1D arrays
    vd_timeprofile = vs.attach("Profile_time")
    time = np.array(vd_timeprofile[:]).flatten()
    vd_timeprofile.detach()

    vd_lat = vs.attach("Latitude")
    lat = np.array(vd_lat[:]).flatten()
    vd_lat.detach()

    vd_lon = vs.attach("Longitude")
    lon = np.array(vd_lon[:]).flatten()
    vd_lon.detach()

    vd_precip = vs.attach("Precip_flag")
    precip_flag = np.array(vd_precip[:]).flatten().astype("int8")
    vd_precip.detach()

    vd_land = vs.attach("Navigation_land_sea_flag")
    land_sea_flag = np.array(vd_land[:]).flatten().astype("float32")
    vd_land.detach()

    # Xarrays named after the layers of height they contain

    ds = xa.Dataset(
        {
            "cloud_scenario": (["cloudsat_trace", "z"], cloud_scenario),
            "cloud_layer_type": (
                ["cloudsat_trace", "layer"],
                cloudLayerType,
            ),
            "cloud_layer_base": (
                ["cloudsat_trace", "layer"],
                cloudLayerBase,
            ),
            "cloud_layer_top": (
                ["cloudsat_trace", "layer"],
                cloudLayerTop,
            ),
        },
        coords={
            "trace": _TRACE.copy,
            "height": (["cloudsat_trace", "z"], height, {"units": "m"}),
            "layers": _LAYERS.copy,
            "lat": (["cloudsat_trace"], lat),
            "lon": (["cloudsat_trace"], lon),
            "time": (["cloudsat_trace"], time),
            "precip_flag": (["cloudsat_trace"], precip_flag),
            "land_sea_flag": (
                ["cloudsat_trace"],
                land_sea_flag,
            ),
        },
        attrs={"UTCstart": UTCstart, "bin_size": vertical_Binsize},
    )

    return ds


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
    _SCEN_OR_LAYER = (
        "scenario",
        "layer",
    )

    _CLOUDSAT_HOST, _CLOUDSAT_PORT = "www.cloudsat.cira.colostate.edu", 22

    def __init__(
        self,
        product_type,
        username,
        *,
        keyfile=None,
        keypass=None,
    ):
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
        parsed_date = date_time.strftime("%Y%j%H%M") + "*"
        query = "/".join([endpoint, date_dir, parsed_date])
        return query

    def _parse_result(self, result):
        """Converts the downloaded hdf file into xarray object.
        Warning! Height is upside down
        height[0] is highest

        Parameters:
        -----------
        result: Path where the file is stored.

        Returns:
        --------
        xarr: Xarray-like
            Contains the most relevant data of a 2B-CLADCLASS file,
            in xarray format.
        """
        return read_hdf4(result)
