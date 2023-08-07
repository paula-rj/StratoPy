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

NEW_SD = metadatatools.SatelliteData.from_values(
    data=FAKE_XA,
    orbits_types=metadatatools.POLAR,
    platforms=metadatatools.CLOUDSAT,
    instruments_types=metadatatools.RADARS,
    products_keys="aaa",
    times_starts=0,
    times_ends=1,
)


def test_error_add_metadata():
    with pytest.raises(ValueError):
        metadatatools.SatelliteData.from_values(
            data=FAKE_XA,
            orbits_types="Extravagant",
            platforms=metadatatools.GOES,
            instruments_types=metadatatools.RADARS,
            products_keys="abc",
            times_starts=0,
            times_ends=1,
        )
    with pytest.raises(ValueError):
        metadatatools.SatelliteData.from_values(
            data=FAKE_XA,
            orbits_types=metadatatools.POLAR,
            platforms="somesat",
            instruments_types=metadatatools.RADARS,
            products_keys="abc",
            times_starts=0,
            times_ends=1,
        )
    with pytest.raises(ValueError):
        metadatatools.SatelliteData.from_values(
            data=FAKE_XA,
            orbits_types=metadatatools.GEOSTATIONARY,
            platforms=metadatatools.GOES,
            instruments_types="camera",
            products_keys="abc",
            times_starts=0,
            times_ends=1,
        )


@pytest.mark.parametrize("or_type", metadatatools.AVAIL_ORBITS)
def test_add_orbittype(or_type):
    new_xa = metadatatools.SatelliteData.from_values(
        data=FAKE_XA,
        orbits_types=or_type,
        platforms=metadatatools.CLOUDSAT,
        instruments_types=metadatatools.RADARS,
        products_keys="cloud_scenario",
        times_starts=0,
        times_ends=1,
    )
    assert isinstance(new_xa.orbits_types, tuple)
    assert new_xa.orbits_types == (or_type,)


@pytest.mark.parametrize("satellite", metadatatools.AVAIL_SATS)
def test_add_platform(satellite):
    new_xa = metadatatools.SatelliteData.from_values(
        data=FAKE_XA,
        orbits_types=metadatatools.POLAR,
        platforms=satellite,
        instruments_types=metadatatools.RADARS,
        products_keys="cloud_scenario",
        times_starts=0,
        times_ends=1,
    )
    assert isinstance(new_xa.platforms, tuple)
    assert new_xa.platforms == (satellite,)


@pytest.mark.parametrize("ins_type", metadatatools.AVAIL_INSTRUMENTS)
def test_add_instrument_type(ins_type):
    new_xa = metadatatools.SatelliteData.from_values(
        data=FAKE_XA,
        orbits_types=metadatatools.POLAR,
        platforms=metadatatools.CLOUDSAT,
        instruments_types=ins_type,
        products_keys="cloud_scenario",
        times_starts=0,
        times_ends=1,
    )
    assert isinstance(new_xa.instruments_types, tuple)
    assert new_xa.instruments_types == (ins_type,)


def test_add_product():
    assert NEW_SD.products_keys == ("aaa",)


def test_todict():
    assert isinstance(NEW_SD.to_dict(), dict)


def test_metadata_idx():
    return_dict = {
        "products_keys": "aaa",
        "instruments_types": "Radar",
        "platforms": "CloudSat",
        "orbits_types": "Polar",
        "times_starts": 0,
        "times_ends": 1,
        "notes": None,
    }
    assert NEW_SD.metadata_at(0) == return_dict

def test_repr():
    la_repr = f"<SatelliteData products_keys={str(NEW_SD.products_keys)}, instruments_types={str(NEW_SD.instruments_types)}, platforms={str(NEW_SD.platforms)}, orbits_types={str(NEW_SD.orbits_types)}, times_starts=(0,), times_ends=(1,)>" # noqa
    assert NEW_SD.__repr__() == la_repr
        
        