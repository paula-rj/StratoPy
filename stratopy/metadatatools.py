#!/usr/bin/env python
# -*- coding: utf-8 -*-
# License: MIT (https://tldrlegal.com/license/mit-license)
# Copyright (c) 2022, Paula Romero Jure et al.
# All rights reserved.

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
MAX_METADATA_ELEMS_SHOW = 10

#: Types of orbits available ==================================================
GEOSTATIONARY = "Geostationary"
POLAR = "Polar"

AVAIL_ORBITS = (GEOSTATIONARY, POLAR)

# Satellites available ========================================================
GOES = "GOES"
CLOUDSAT = "CloudSat"

AVAIL_SATS = (GOES, CLOUDSAT)

# Sensor type =================================================================

RADIOMETERS = "Radiometer"
RADARS = "Radar"

AVAIL_INSTRUMENTS = (RADIOMETERS, RADARS)

# =============================================================================
# CLASS
# =============================================================================


@dcss.dataclass(frozen=True, repr=False)
class SatelliteData:
    """Defines new satellite data."""

    data: xa.Dataset
    products_keys: tuple[str]
    instruments_types: tuple[str]
    platforms: tuple[str]
    orbits_types: tuple[str]
    times_starts: tuple[str]
    times_ends: tuple[str]
    notes: tuple[str]

    def _validate_metadata_tuple(
        self, metadata, values, choices, expected_len
    ):
        if not isinstance(values, tuple):
            raise TypeError(f"{metadata} must be an instance of tuple")
        if expected_len is not None and len(values) != expected_len:
            raise ValueError(f"{metadata} must be of lentgh {expected_len}")

        if choices:
            for value in values:
                if value is not None and value not in choices:
                    raise ValueError(
                        f"{metadata} must be one of {choices}. Found {value!r}"
                    )

    def __post_init__(self):
        self._validate_metadata_tuple(
            "orbits_types", self.orbits_types, AVAIL_ORBITS, None
        )

        expected_len = len(self.orbits_types)
        self._validate_metadata_tuple(
            "platforms", self.platforms, AVAIL_SATS, expected_len
        )
        self._validate_metadata_tuple(
            "instruments_types",
            self.instruments_types,
            AVAIL_INSTRUMENTS,
            expected_len,
        )
        self._validate_metadata_tuple(
            "times_starts", self.times_starts, (), expected_len
        )
        self._validate_metadata_tuple(
            "times_ends", self.times_ends, (), expected_len
        )
        self._validate_metadata_tuple("notes", self.notes, (), expected_len)

    @classmethod
    def from_values(
        cls,
        data,
        *,
        products_keys,
        instruments_types,
        platforms,
        orbits_types,
        times_starts,
        times_ends,
        notes=None,
    ):
        def _str_as_tuple(value):
            return value if isinstance(value, tuple) else (value,)

        products_keys = _str_as_tuple(products_keys)
        instruments_types = _str_as_tuple(instruments_types)
        platforms = _str_as_tuple(platforms)
        orbits_types = _str_as_tuple(orbits_types)
        times_starts = _str_as_tuple(times_starts)
        times_ends = _str_as_tuple(times_ends)
        notes = _str_as_tuple(notes)
        return cls(
            data=data,
            products_keys=products_keys,
            instruments_types=instruments_types,
            platforms=platforms,
            orbits_types=orbits_types,
            times_starts=times_starts,
            times_ends=times_ends,
            notes=notes,
        )

    def __repr__(self):
        clsname = type(self).__name__
        products_keys = self.products_keys[:MAX_METADATA_ELEMS_SHOW]
        instruments_types = self.instruments_types[:MAX_METADATA_ELEMS_SHOW]
        platforms = self.platforms[:MAX_METADATA_ELEMS_SHOW]
        orbits_types = self.orbits_types[:MAX_METADATA_ELEMS_SHOW]
        times_starts = self.times_starts[:MAX_METADATA_ELEMS_SHOW]
        times_ends = self.times_ends[:MAX_METADATA_ELEMS_SHOW]
        repr_str = (
            f"<{clsname} "
            f"{products_keys=}, {instruments_types=}, {platforms=}, "
            f"{orbits_types=}, {times_starts=}, {times_ends=}>"
        )
        return repr_str

    def to_dict(self):
        return dcss.asdict(self)

    def metadata_at(self, idx):
        return {k: v[idx] for k, v in self.to_dict().items() if k != "data"}
