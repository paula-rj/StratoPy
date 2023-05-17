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
