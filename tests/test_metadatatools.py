#!/usr/bin/env python
# -*- coding: utf-8 -*-
# License: MIT (https://tldrlegal.com/license/mit-license)
# Copyright (c) 2022, Paula Romero Jure et al.
# All rights reserved.
import numpy as np

import pytest

from stratopy import metadatatools

import xarray as xa


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

    assert new_xa.attrs["_STRATOPY_"].orbit_type == "polar"
    assert new_xa.attrs["_STRATOPY_"].platform == "CloudSat"
    assert new_xa.attrs["_STRATOPY_"].instrument_type == "Radar"
    assert new_xa.attrs["_STRATOPY_"].product_key == "cloud_scenario"


@pytest.mark.parametrize("or_type", metadatatools.ORBIT_TYPES)
def test_add_orbittype(or_type):
    new_xa = metadatatools.add_metadata(
        FAKE_XA,
        orbit_type=or_type,
        platform=metadatatools.CLOUDSAT,
        instrument_type=metadatatools.RADARS,
        product_key="cloud_scenario",
    )
    assert metadatatools.orbit_type(new_xa) == or_type


@pytest.mark.parametrize("satellite", metadatatools.PLATFORMS)
def test_add_platform(satellite):
    new_xa = metadatatools.add_metadata(
        FAKE_XA,
        orbit_type=metadatatools.POLAR,
        platform=satellite,
        instrument_type=metadatatools.RADARS,
        product_key="cloud_scenario",
    )
    assert metadatatools.platform(new_xa) == satellite


@pytest.mark.parametrize("ins_type", metadatatools.INSTRUMENTS_TYPES)
def test_add_instrument_type(ins_type):
    new_xa = metadatatools.add_metadata(
        FAKE_XA,
        orbit_type=metadatatools.POLAR,
        platform=metadatatools.CLOUDSAT,
        instrument_type=ins_type,
        product_key="cloud_scenario",
    )
    assert metadatatools.instrument_type(new_xa) == ins_type


def test_add_product():
    new_xa = metadatatools.add_metadata(
        FAKE_XA,
        orbit_type=metadatatools.GEOSTATIONARY,
        platform=metadatatools.GOES,
        instrument_type=metadatatools.RADIOMETERS,
        product_key="aaa",
    )
    assert metadatatools.product_and_key(new_xa) == "aaa"
