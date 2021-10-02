from collections.abc import Mapping

import attr

from . import cloudsat

import datetime

import geopandas as gpd

import os

# ============================================================================
# CLASSES
# ============================================================================

# type: ignore


@attr.s(frozen=True, repr=False)
class MetaData(Mapping):
    """Implements an inmutable dict-like to store the metadata.
    Also provides attribute like access to the keys.
    Example
    -------
    >>> metadata = MetaData({"a": 1, "b": 2})
    >>> metadata.a
    1
    >>> metadata["a"]
    1
    """

    _data = attr.ib(converter=dict, factory=dict)

    def __repr__(self):
        """repr(x) <=> x.__repr__()."""
        return f"Metadata({repr(self._data)})"

    def __getitem__(self, k):
        """x[k] <=> x.__getitem__(k)."""
        return self._data[k]

    def __iter__(self):
        """iter(x) <=> x.__iter__()."""
        return iter(self._data)

    def __len__(self):
        """len(x) <=> x.__len__()."""
        return len(self._data)

    def __getattr__(self, a):
        """getattr(x, y) <==> x.__getattr__(y) <==> getattr(x, y)."""
        return self[a]
