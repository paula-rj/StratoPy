#!/usr/bin/env python
# -*- coding: utf-8 -*-
# License: MIT (https://tldrlegal.com/license/mit-license)
# Copyright (c) 2022, Paula Romero Jure et al.
# All rights reserved.
r"""Module that defines the methods for extracting a GOES16 product.

Currently works only for products defined in PRODUCT TYPES attribute.
"""

# =============================================================================
# IMPORTS
# =============================================================================

import dateutil.parser

import pytz

import xarray as xa

from . import ebase
from ..metadatatools import GEOSTATIONARY, GOES, RADIOMETERS

# =============================================================================
# CONSTANTS
# =============================================================================

MODE_CHANGE_DATE = dateutil.parser.parse("2019 feb 19 15:00 UTC").astimezone(pytz.UTC)

# =============================================================================
# QUERY PARSERS
# =============================================================================


def _with_channel_parser(ptype, dtime, channel, mode):
    """Returns the name of the product as a str.

    Works for products with channels (ABI).

    Parameters
    ----------
    ptype: str
        Product type (available list in .....)
    mode: int
        Aquisition mode of ABI sensor
    channel: int
        Channel of ABI
    dtime: datetiem object
        Date and time in UTC

    Returns
    -------
    parsed: str
        Full name of the file

    """
    # OR_ABI-L2-CMIPF-M3C03_G16_s20190021800
    pdate = dtime.strftime("%Y%j%H%M")
    parsed = f"OR_{ptype}-M{mode}C{channel:02d}_G16_s{pdate}*"
    return parsed


def _whithout_channel_parser(ptype, dtime, channel, mode):
    """Returns the name of the product as a str.

    Works for products without channels (ABI).

    Parameters
    ----------
    ptype: str
        Product type (available list in .....)
    mode: int
        Aquisition mode of ABI sensor.
    channel: int
        Channel of ABI. Not needed here.
    dtime: datetiem object
        Date and time in UTC.

    Returns
    -------
    parsed: str
        Full name of the file.
    """
    # OR_ABI-L2-MCMIPF-M6_G16_s20190021800
    pdate = dtime.strftime("%Y%j%H%M%S")
    parsed = f"OR_{ptype}-M{mode}_G16_s{pdate}*"
    return parsed


# =============================================================================
# CONNECTOR
# =============================================================================


class GOES16(ebase.S3Mixin, ebase.ConnectorABC):
    """
    Creates a connection with GOES16 AWS server.

    The connection is meant to download the product later.

    Parameters
    ----------
    product_type: str
        Type of product to be downloaded.
    channel: int
        ABI channel
    mode: int
        Aquisition mode of the sensor.

    Attributes
    ----------
    _PRODUCT_TYPES_PARSERS: Gets the type of product.
    PRODUCT_TYPES: Type of products available.

    Methods
    -------
    get_endpoint
        Gets host url, a directory from s3 AWS.
    """

    _PRODUCT_TYPES_PARSERS = {
        "ABI-L1b-RadF": _with_channel_parser,  # Radiances
        "ABI-L2-CMIPF": _with_channel_parser,  # Cloud & Moisture
        "ABI-L2-ACHA2KMF": _whithout_channel_parser,  # Clouds Height
        "ABI-L2-ACHAF": _whithout_channel_parser,  # Clouds Height
        "ABI-L2-ACHTF": _whithout_channel_parser,
        "ABI-L2-ACMF": _whithout_channel_parser,  # Clear sky mask
        "ABI-L2-ADPF": _whithout_channel_parser,  # Aerosol Detection
        "ABI-L2-AODF": _whithout_channel_parser,  # Aerosol
        "ABI-L2-BRFF": _whithout_channel_parser,  # Bidir. Reflactance Factor
        "ABI-L2-CODF": _whithout_channel_parser,  # Cloud Optical Depth
        "ABI-L2-CPSF": _whithout_channel_parser,  # Cloud Particle Size
        "ABI-L2-CTPF": _whithout_channel_parser,  # CLoud Top Pressure
        "ABI-L2-MCMIPF": _whithout_channel_parser,  # Cloud & Moist. Multiband
    }

    PRODUCT_TYPES = tuple(_PRODUCT_TYPES_PARSERS)

    def __init__(self, product_type, channel):
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
            int(channel) if self._ptype_parser is _with_channel_parser else None
        )

    def __repr__(self):
        """Representation for a GOOES16 object as chosen product type, band."""
        return f"<GOES16 product_type={self.product_type!r}, ch={self.channel}>"

    def _repr_html_(self):
        """Representation for a G OES16 object as chosen product type, band."""
        return f"<GOES16 product_type={self.product_type!r}  , ch={self.channel}>"

    def get_endpoint(self):
        """Gets the URL direction where all the GOES16 files are stored.

        Returns the URL as str.
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

        Returns
        -------
        query: str or Path
            Full path where the file is stored in the server.

        """
        date_dir = dt.strftime("%Y/%j/%H")

        if dt < MODE_CHANGE_DATE:
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

    def get_orbit_type(self):
        """Gets the type of orbit.

        Returns
        -------
            str: GOES satellites are geostationary.
        """
        return GEOSTATIONARY

    def get_product_type_key(self):
        """Gets the type of product.

        Returns
        -------
            str: GOES satellites are geostationary.
        """
        #: GOES ch list
        CH_LIST = [
            "CMI_C01",
            "CMI_C02",
            "CMI_C03",
            "CMI_C04",
            "CMI_C05",
            "CMI_C06",
            "CMI_C07",
            "CMI_C08",
            "CMI_C09",
            "CMI_C10",
            "CMI_C11",
            "CMI_C12",
            "CMI_C13",
            "CMI_C14",
            "CMI_C15",
            "CMI_C16",
        ]
        #: data for goes products
        DATA_GOES = {
            "ABI-L1b-RadF": "Rad",  # Radiances
            "ABI-L2-CMIPF": "CMI",  # Cloud & Moisture
            "ABI-L2-ACHA2KMF": "",  # Clouds Height
            "ABI-L2-ACHAF": "",  # Clouds Height
            "ABI-L2-ACHTF": "",
            "ABI-L2-ACMF": "",  # Clear sky mask
            "ABI-L2-ADPF": "",  # Aerosol Detection
            "ABI-L2-AODF": "",  # Aerosol
            "ABI-L2-BRFF": "",  # Bidir. Reflactance Factor
            "ABI-L2-CODF": "",  # Cloud Optical Depth
            "ABI-L2-CPSF": "",  # Cloud Particle Size
            "ABI-L2-CTPF": "",  # CLoud Top Pressure
            "ABI-L2-MCMIPF": CH_LIST,  # Cloud & Moist. Multiband
        }
        return DATA_GOES.get(self.product_type)

    def get_instrument_type(self):
        """Gets the type of product.

        Returns
        -------
            str: GOES satellites are geostationary.
        """
        return "Radiometer"

    def get_platform(self):
        """Gets the type of product.

        Returns
        -------
            str: GOES satellites are geostationary.
        """
        return GOES

    def _parse_result(self, result):
        """Converts the downloaded netcdf file-like into xarray object.

        Parameters
        ----------
        result: the file in Bytes.

        Returns
        -------
        goes_ds: Xarray Dataset
            Dataset containing the information from the original NetCDF file.
        """
        goes_ds = xa.open_dataset(result, engine="h5netcdf")
        return goes_ds
