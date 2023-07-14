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

import dataclasses as dcss
import xarray as xa

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


AVAIL_ORBITS = ["Polar", "Goestationary"]
AVAIL_SATS = ["GOES", "CloudSat", "Terra"]
AVAIL_INSTRUMENTS = ["Radar", "Radiometer"]


@dcss.dataclass(frozen=True) 
class SatelliteData:
    """Defines new satellite data.""" 
    
    data: xa.Dataset
    time_start: str
    time_end: str
    product_key: str
    instrument_type: str
    platform: str
    orbit_type: str
    
    def __post_init__(self):
        if self.orbit_type not in AVAIL_ORBITS:
            raise ValueError(f"Orbit type not valid or available. Must be one of {AVAIL_ORBITS}")
        if self.platform not in AVAIL_SATS:
            raise ValueError(f"Platform name not valid or not available. Must be one of {AVAIL_SATS}")
        if self.instrument_type not in AVAIL_INSTRUMENTS:
            raise ValueError(f"Instrument not valid or not available. Must be one of {AVAIL_INSTRUMENTS}")
        
    def to_dict(self):
        return dcss.asdict(self) 
