#!/usr/bin/env python
# -*- coding: utf-8 -*-
# License: MIT (https://tldrlegal.com/license/mit-license)
# Copyright (c) 2022, Paula Romero Jure et al.
# All rights reserved.

import dateutil.parser

import pytz

import xarray as xa

from . import base

# =============================================================================
# QUERY PARSERS
# =============================================================================


def _with_channel_parser(ptype, dtime, channel, mode):
    """Returns the name of the product as a string,
    if the product has channels (ABI) to chose.

    Parameters:
    -----------
    ptype: str
        Product type (available list in .....)
    mode: int
        Aquisition mode of ABI sensor
    channel: int
        Channel of ABI
    dtime: datetiem object
        Date and time in UTC

    Returns:
    --------
    parsed: str
        Full name of the file

    """
    # OR_ABI-L2-CMIPF-M3C03_G16_s20190021800
    pdate = dtime.strftime("%Y%j%H%M")
    parsed = f"OR_{ptype}-M{mode}C{channel:02d}_G16_s{pdate}*"
    return parsed


def _whithout_channel_parser(ptype, dtime, channel, mode):
    """Returns the name of the product as a string,
    if the product does not have channels (ABI) to choose.

    Parameters:
    -----------
    ptype: str
        Product type (available list in .....)
    mode: int
        Aquisition mode of ABI sensor
    channel: int
        Channel of ABI
    dtime: datetiem object
        Date and time in UTC

    Returns:
    --------
    parsed: str
        Full name of the file

    Raises
    ------
    Value error
        If the user changes the default channel
        value to something different than None.

    """

    # OR_ABI-L2-MCMIPF-M6_G16_s20190021800
    pdate = dtime.strftime("%Y%j%H%M")
    parsed = f"OR_{ptype}-M{mode}_G16_s{pdate}*"
    return parsed


# =============================================================================
# CONNECTOR
# =============================================================================


class GOES16(base.S3Mixin, base.ConnectorABC):
    """
    Object that is created by retrieving products from GOES-16 satellite.

    Attributes
    ----------
    product_type: str
        Type of product to be downloaded
    channel: int
        ABI channel
    mode: int
        Aquisition mode of the sensor
    """

    _PRODUCT_TYPES_PARSERS = {
        "ABI-L1b-RadF": _with_channel_parser,
        "ABI-L2-CMIPF": _with_channel_parser,
        "ABI-L2-MCMIPF": _whithout_channel_parser,
        "ABI-L2-ACHTF": _whithout_channel_parser,
    }

    PRODUCT_TYPES = tuple(_PRODUCT_TYPES_PARSERS)

    def __init__(self, product_type, channel=3):
        # POR ahora solo trabajamos con el sensor ABI
        # y con imagenes full disk, por eso son todos F

        if product_type not in self.PRODUCT_TYPES:
            raise ValueError(
                "Invalid product type. "
                f"Expected one of: {self.PRODUCT_TYPES}. "
                f"Found {product_type!r}"
            )

        self.product_type = product_type
        self._ptype_parser = self._PRODUCT_TYPES_PARSERS[product_type]
        self.channel = (
            int(channel)
            if self._ptype_parser is _with_channel_parser
            else None
        )

    def __repr__(self):
        return f"<GOES16 product_type={self.product_type!r}>"

    def get_endpoint(self):
        """Gets the URL direction where all the GOES16
        files are stored. Returns the URL as str.
        """
        return "/".join(["s3:/", "noaa-goes16", self.product_type])

    def _makequery(self, endpoint, dt):
        """Builds the whole query needed to download the product from s3.

        Parameters
        ----------
        endpoint: str
            url where GOES-16 products are hosted.
        date: datetime obj
            the requested date and time.
            It should contain year, month, day, hour and minutes.

        """
        date_dir = dt.strftime("%Y/%j/%H")

        mode_change_date = dateutil.parser.parse(
            "2019 feb 19 15:00 UTC"
        ).astimezone(pytz.UTC)
        if dt < mode_change_date:
            mode = 3  # 15 min
        else:
            mode = 6  # 10 min

        file_glob = self._ptype_parser(
            ptype=self.product_type,
            dtime=dt,
            channel=self.channel,
            mode=mode,
        )
        query = "/".join([endpoint, date_dir, file_glob])
        return query

    def _parse_result(self, result):
        """Converts the downloaded netcdf file-like into xarray object.

        Parameters:
        -----------
        result: the file in Bytes.
        """
        xarr = xa.open_dataset(result, engine="h5netcdf")
        return xarr
