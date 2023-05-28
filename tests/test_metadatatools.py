#!/usr/bin/env python
# -*- coding: utf-8 -*-
# License: MIT (https://tldrlegal.com/license/mit-license)
# Copyright (c) 2022, Paula Romero Jure et al.
# All rights reserved.
import pytest
import numpy as np
import xarray as xa
from stratopy import metadatatools


FAKE_XA = xa.Dataset(
    data_vars={"the_vars": ["a", "b", "c", "d"]},
    coords={"the_cords": np.arange(4)},
)


def test_error_add_metadata():
    with pytest.raises(ValueError):
        metadatatools.Metadata(
            orbit_type="Extravagant",
            platform=metadatatools.GOES,
            instrument_type=metadatatools.RADARS,
            product_key="abc",
        )
    with pytest.raises(ValueError):
        metadatatools.Metadata(
            orbit_type=metadatatools.POLAR,
            platform="somesat",
            instrument_type=metadatatools.RADIOMETERS,
            product_key="abc",
        )
    with pytest.raises(ValueError):
        metadatatools.Metadata(
            orbit_type=metadatatools.GEOSTATIONARY,
            platform=metadatatools.CLOUDSAT,
            instrument_type="CAMERA",
            product_key="abc",
        )


def test_add_metadata():
    new_xa = metadatatools.add_metadata(
        FAKE_XA,
        orbit_type=metadatatools.POLAR,
        platform=metadatatools.CLOUDSAT,
        instrument_type=metadatatools.RADARS,
        product_key="cloud_scenario",
    )
    assert new_xa._STRATOPY_.orbit_type == "polar"
    assert new_xa._STRATOPY_.platform == "CloudSat"
    assert new_xa._STRATOPY_.instrument_type == "Radar"
    assert new_xa._STRATOPY_.product_key == "cloud_scenario"
