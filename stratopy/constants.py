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

DATA_CLOUDSAT = {
    "2B-CLDCLASS.P1_R05": ["cloud_scen", "cloud_layer_type"],
    "2B-CLDCLASS.P_R04": "cloud_scen",
    "2B-CLDCLASS-LIDAR.P_R04": "cloud_scen",
}

# Radiometers
RADIOMETERS = ("G16", "G17", "G18", "MODIS")

# Radars
