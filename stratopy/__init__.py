#!/usr/bin/env python
# -*- coding: utf-8 -*-

# =============================================================================
# META
# =============================================================================
r"""A Python package designed to easily manipulate CloudSat and GOES-R
and generate labeled images containing cloud types.

It consists in five modules:

- stratopy.cloudsat module
- stratopy.core module
- stratopy.goes module
- stratopy.io module

 """
__name__ = "stratopy"
__version__ = "0.0.1"


# =============================================================================
# IMPORTS
# =============================================================================

from .cloudsat import *  # noqa
from .core import *  # noqa
from .goes import *  # noqa
from .IO import *  # noqa
