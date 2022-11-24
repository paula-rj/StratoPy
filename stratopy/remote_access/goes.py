#!/usr/bin/env python
# -*- coding: utf-8 -*-
# License: MIT (https://tldrlegal.com/license/mit-license)
# Copyright (c) 2022, Paula Romero Jure et al.
# All rights reserved.

import xarray as xa

from . import base


def _with_channel_parser(ptype, mode, channel, dtime):
    """Returns the name of the product as a string,
    if the product has channels (ABI) to chose.

    Parameters:
    -----------
    ptype: str
        Product type hjj(available list in .....)
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
    parsed = f"OR_ABI-{ptype}-M{mode}C{channel:02d}_G16_s{pdate}*"
    return parsed


def _whithout_channel_parser(ptype, mode, channel, dtime):
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

    """

    # OR_ABI-L2-MCMIPF-M6_G16_s20190021800
    pdate = dtime.strftime("%Y%j%H%M")
    parsed = f"OR_ABI-{ptype}-M{mode}_G16_s{pdate}*"
    return parsed


class GOES16(base.S3Mixin, base.ConnectorABC):
    """
    Attributes
    ----------
    product_type: str
        Type of product to be downloaded
    channel: int
        ABI channel (not always available)
    mode: int
        Aquisition mode of the sensor
    """

    _PRODUCT_TYPES_PARSERS = {
        "L1b-RadF": _with_channel_parser,
        "L2-CMIPF": _with_channel_parser,
        "L2-MCMIPF": _whithout_channel_parser,
        "L2-ACHTF": _whithout_channel_parser,
    }

    PRODUCT_TYPES = tuple(_PRODUCT_TYPES_PARSERS)

    _MODES = (1, 2, 3, 4, 5, 6)

    def __init__(self, product_type, channel=3, mode=6):
        # NOTA: POR ahora solo trabajamos con el sensor ABI
        # y con imagenes full disk, por eso son todos F

        if product_type not in self.PRODUCT_TYPES:
            raise ValueError(
                "Invalid product type. "
                f"Expected one of: {self.PRODUCT_TYPES}. "
                f"Found {product_type!r}"
            )
        if mode not in self._MODES:
            raise ValueError(
                "Invalid mode for ABI. "
                f"Expected one of: {self._MODES}. "
                f"Found {mode!r}"
            )

        self.mode = mode
        self.product_type = product_type
        self.channel = channel
        self._ptype_parser = self._PRODUCT_TYPES_PARSERS[product_type]

    def __repr__(self):
        return f"GOES16 object. {self.product_type} "

    def get_endpoint(self):
        """ "Gets the URL direction where all the GOES16
        files are stored. Returns the URL as str.

        """
        return "/".join(["s3:/", "noaa-goes16", self.product_type])

    def _makequery(self, endpoint, dt):
        date_dir = dt.strftime("%Y/%j/%H")
        file_glob = self._ptype_parser(
            ptype=self.product_type,
            mode=self.mode,
            channel=self.channel,
            dtime=dt,
        )
        query = "/".join([endpoint, date_dir, file_glob])
        return query

    def _parse_result(self, result):
        xarr = xa.open_dataset(result, engine="h5netcdf")
        return xarr
