#!/usr/bin/env python
# -*- coding: utf-8 -*-
# License: MIT (https://tldrlegal.com/license/mit-license)
# Copyright (c) 2022, Paula Romero Jure et al.
# All rights reserved.

# =============================================================================
# META
# =============================================================================

"""Constants used inside stratopy."""


# =============================================================================
# IMPORTS
# =============================================================================

import dataclasses as dcs

# =============================================================================
# CONSTANTS
# =============================================================================

#:
STRATOPY_METADATA_KEY = "_STRATOPY_"


# ORBITS ======================================================================

#: For Geostationary satellites
GEOSTATIONARY = "geostationary"

#: For Polar orbiting satellites
POLAR = "polar"

#: Types of satellite orbits available
ORBIT_TYPES = (GEOSTATIONARY, POLAR)

# Satellites available ========================================================
GOES = "G16"
CLOUDSAT = "CloudSat"

PLATFORMS = (GOES, CLOUDSAT)

# instruments =================================================================

RADIOMETERS = "Radiometer"

RADARS = "Radar"

INSTRUMENTS_TYPES = (RADIOMETERS, RADARS)

# =============================================================================
# CLASS
# =============================================================================


@dcs.dataclass(frozen=True)
class Metadata:
    """Class that ensures the description of a satellite's orbit.

    Raises
    ------
        ValueError: If satellite extractor has not descripted its orbit.
    """

    orbit_type: str
    platform: str
    instrument_type: str
    product_key: str

    def _validate_in(self, field, value, options):
        if value not in options:
            raise ValueError(
                f"{field!r} must be one of {options}. Found: {value!r}"  # noqa
            )

    def __post_init__(self):
        """Initialie field value orbit type.

        Raises
        ------
            ValueError: If satellite extractor has not descripted its orbit.
        """
        self._validate_in("orbit_type", self.orbit_type, ORBIT_TYPES)
        self._validate_in("platform", self.platform, PLATFORMS)
        self._validate_in(
            "instrument_type", self.instrument_type, INSTRUMENTS_TYPES
        )


# =============================================================================
# FUNCTIONS
# =============================================================================


def add_metadata(da, **kwargs):
    """Adds mandatory metadata as attrs.

    Parameters
    ----------
    da: ``xarray.DataArray``
        DataArray to which the metadata will be added.

    Returns
    -------
    da:  ``xarray.DataArray``
        The same DataArray but with the metadata added as attrs.
    """
    metadata = Metadata(**kwargs)
    da.attrs.update({STRATOPY_METADATA_KEY: metadata})
    return da


def orbit_type(da):
    """Adds data about the orbit type of the platform.

    It could be POLAR or GEOSTATIONARY.

    Parameters
    ----------
    da: ``xarray.DataArray``
        DataArray to which the metadata will be added.

    Returns
    -------
    da:  ``xarray.DataArray``
        The same DataArray but with the orbit type added as attrs \
            under the key 'orbit_type'.
    """
    return da.attrs[STRATOPY_METADATA_KEY].orbit_type


def platform(da):
    """Adds data about the name of the satellite.

    Parameters
    ----------
    da: ``xarray.DataArray``
        DataArray to which the metadata will be added.

    Returns
    -------
    da:  ``xarray.DataArray``
        The same DataArray but with the metadata added as attrs.
    """
    return da.attrs[STRATOPY_METADATA_KEY].platform


def instrument_type(da):
    """Adds data about the instrument type that generated the products.

    It could be RADIOMETER or RADAR.

    Parameters
    ----------
    da: ``xarray.DataArray``
        DataArray to which the metadata will be added.

    Returns
    -------
    da:  ``xarray.DataArray``
        The same DataArray but with the metadata added as attrs \
            under the key 'instrument_type'.
    """
    return da.attrs[STRATOPY_METADATA_KEY].instrument_type


def product_and_key(da):
    """Adds data abouname of the field of the product that can be merged.

    When fetched, products are retrieved as xarrays.Datasets.
    Each data_var has a key name. Most products have many data vars.
    When merging two products, we usually only need one field to work with.

    Parameters
    ----------
    da: ``xarray.DataArray``
        DataArray to which the metadata will be added.

    Returns
    -------
    da:  ``xarray.DataArray``
        The same DataArray but with the metadata added as attrs.
    """
    return da.attrs[STRATOPY_METADATA_KEY].product_key
