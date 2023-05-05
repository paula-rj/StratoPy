#!/usr/bin/env python
# -*- coding: utf-8 -*-
# License: MIT (https://tldrlegal.com/license/mit-license)
# Copyright (c) 2022, Paula Romero Jure et al.
# All rights reserved.

r"""Module that defines methods for extracting a product from the Cloudsat DPC.

The CloudSat class is an extractor that is meant to create a cloudsat object
and then fetch the object given a certain date and time.
"""

# =============================================================================
# IMPORTS
# =============================================================================
import atexit
import datetime as dt
import os
import tempfile

from dateutil import parser
import numpy as np

from pyhdf.HDF import HC, HDF
from pyhdf.SD import SD, SDC
from pyhdf.VS import VS

import xarray as xa

from . import base
from ..utils import nearest_date

_TRACE = np.arange(36950, dtype=np.int32)
_LAYERS = np.arange(10, dtype=np.int8)


def read_hdf4(path):
    """Reads a HDF file CloudSat product and returns it as an Xarray Dataset.

    Currently is only useful for 2B-CLDCLASS files.

    Parameters
    ----------
    path: str or Path
        Path where the file is stored

    Returns
    -------
    ds: Xarray Dataset
        Dataset containing the most relevant coordinates
        and attributes of a 2B-CLDCLASS file.
    """
    sd_file = SD(path, SDC.READ)
    height = sd_file.select("Height").get()
    cloud_scenario = sd_file.select("cloud_scenario").get()
    cloudLayerBase = sd_file.select("CloudLayerBase").get()
    cloudLayerTop = sd_file.select("CloudLayerTop").get()
    cloudLayerType = sd_file.select("CloudLayerType").get().astype("int8")

    # HDF
    hdf_file = HDF(path, HC.READ)
    vs = VS(hdf_file)

    # Seconds since start of granule
    vd_seconds = vs.attach("Profile_time")
    profile_seconds = np.array(vd_seconds[:])[:, 0]
    vd_seconds.detach()

    # TAI timestamp for the first profile in the data file
    vd_TAI = vs.attach("TAI_start")
    TAI = vd_TAI[0][0]
    vd_TAI.detach()

    # Getting profile time for evey footprint
    start = parser.parse("1993-01-01") + dt.timedelta(seconds=TAI)
    # A profile is taken every 0.16 s
    offsets = [dt.timedelta(seconds=sec) for sec in profile_seconds]
    profile_time = np.array([start + offset for offset in offsets])

    # Important attributes, one number only
    vd_UTCstart = vs.attach("UTC_start")
    UTCstart = vd_UTCstart[:]
    vd_UTCstart.detach()

    vd_verticalBin = vs.attach("Vertical_binsize")
    vertical_Binsize = np.array(vd_verticalBin[:]).flatten()
    vd_verticalBin.detach()

    # Geolocated data, 1D arrays

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
            "time": (["cloudsat_trace"], profile_time),
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
    Establishes a connection with the CloudSat DPC.

    Parameters
    ----------
    product_type: str
        Type of product to be downloaded. Currently 3 available.
    username: str
        username at CloudSat server.
    keyfile:
        Key for ssh connection.
        Default = None
    keypass: str
        Password for you ssh key. You may not have any.
        Default = None

    Attributes
    ----------
    _PRODUCT_TYPES: tuple
        types of products available for downloading.
    _SCEN_OR_LAYER: tuple
        Work with cld_scenario or Layer.
    _CLOUDSAT_HOST: str
        SFTP server at CloudSat DPC.
    _CLOUDSAT_PORT: int
        Host port.

    Methods
    -------
    get_endpoint
        Gets host url, a directory from CloudSat DPC.

    Notes
    -----
        CloudSat DPC: The user must have and account created at CloudSat DPC
        (https://www.cloudsat.cira.colostate.edu/) to be able
        to use this class and retrieve a product from the CloudSat server.
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
        if "@" in username:
            username = username.replace("@", "AT", 1)

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
        """Representation for a CloudSat object as chosen product type."""
        return f"<CloudSat product_type={self.product_type!r}>"

    def _repr_html_(self):
        """Representation for a CloudSat object as chosen product type."""
        return f"<CloudSat product_type={self.product_type!r}>"

    def get_endpoint(self):
        """Gets the directory url for CloudSat files.

        Returns the URL as str.
        """
        return "/".join(["Data", self.product_type])

    def _makequery(self, endpoint, date_time):
        """Builds the whole query needed to download the product from DPC.

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
        parsed_date = date_time.strftime("%Y%j%H%M%S")
        query = "/".join([endpoint, date_dir, parsed_date])
        return query

    def _parse_result(self, result):
        """Converts the downloaded HDF file into Xarray Dataset.

        Parameters
        ----------
        result: Path where the file is stored.

        Returns
        -------
        xarr: Xarray-like
            Contains the most relevant data of a 2B-CLADCLASS file,
            in xarray format.

        Notes
        -----
        Warning! Height is upside down, height[0] is highest.
        """
        return read_hdf4(result)

    def _download(self, query):
        # splits full query to obtain date pattern YYYYdddHHMM*
        store_dir, pattern = query.rsplit("/", 1)
        # Creates sftp session (on SSH server) object
        with self._client.open_sftp() as sftp:
            # Raises FileNotFoundError if file not found
            candidates = sftp.listdir(store_dir)
            # List of files for selected date
            filename_idx = nearest_date.closest_datetime(candidates, pattern)
            filename = candidates[filename_idx]

            full_path = "/".join([store_dir, filename])

            # Temporary container
            cls_name = type(self).__name__
            _, tmp_path = tempfile.mkstemp(suffix=".hdf", prefix=f"stpy_{cls_name}_")
            atexit.register(os.remove, tmp_path)

            # Downloads file from full and copies into tmp
            sftp.get(remotepath=full_path, localpath=tmp_path)

            # Returns temps cause parse_result gets a path as input
            return tmp_path
