#!/usr/bin/env python
# -*- coding: utf-8 -*-
# License: MIT (https://tldrlegal.com/license/mit-license)
# Copyright (c) 2022, Paula Romero Jure et al.
# All rights reserved.

import io
import os
import pathlib
from collections.abc import MutableMapping
from unittest import mock

import pytest

from pyhdf.HDF import HC, HDF
from pyhdf.SD import SD, SDC
from pyhdf.VS import VS

import xarray as xa

# =============================================================================
# GLOBALS
# =============================================================================

DATA = pathlib.Path(os.path.abspath(os.path.dirname(__file__))) / "data"

# =============================================================================
# CACHE PATCH
# =============================================================================


class _FakeCache(MutableMapping):
    """Implements a minimalist no-cache for disk-cache."""

    def __init__(self, **kwargs):
        self._params = kwargs

    def get(self, key, default=None, *args, **kwargs):
        """Return the ``default``."""
        return default

    def set(self, key, value, *args, **kwargs):
        """Return True."""
        return True

    def expire(self, now=None, retry=False):
        """Return 0."""
        return 0

    def __getattr__(self, a):
        return self._params[a]

    def __len__(self):
        """Return 0."""
        return 0

    def __enter__(self):
        """Enter the runtime context related to this object.

        The with statement will bind this method's return value to the
        target(s) specified in the as clause of the statement, if any.

        """
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        """Exit the runtime context related to this object.

        The parameters describe the exception that caused the context to be
        exited. If the context was exited without an exception, all three
        arguments will be None.

        """
        pass

    def __delitem__(self, k):
        """Raise KeyError."""
        raise KeyError(k)

    def __getitem__(self, k):
        """Raise KeyError."""
        raise KeyError(k)

    def __iter__(self):
        """Return an empty iterator."""
        return iter({})

    def __setitem__(self, k, v):
        """Do nothing."""
        pass


@pytest.fixture(scope="session", autouse=True)
def patch_cache():
    with mock.patch("diskcache.Cache", _FakeCache):
        yield


# =============================================================================
# DATA FIXTURES
# =============================================================================


@pytest.fixture(scope="session")
def data_path():
    def _make_path(sat, fname):
        return DATA / sat / fname

    return _make_path


@pytest.fixture(scope="session")
def data_bytes(data_path):
    def _read_bytes_io(sat, fname):
        fpath = data_path(sat, fname)
        with open(fpath, "rb") as fp:
            buff = io.BytesIO(fp.read())
        return buff

    return _read_bytes_io


@pytest.fixture(scope="session")
def dataset(data_bytes):
    def _make(sat, fname, engine):
        buff = data_bytes(sat, fname)
        xarr = xa.open_dataset(buff, engine=engine)
        return xarr

    return _make


@pytest.fixture(scope="session")
def data_hdf(data_path):
    def read_hdf(sat, fname):
        fpath = data_path(sat, fname)
        sd_file = SD(fpath, SDC.READ)
        hdf_file = HDF(fpath, HC.READ)

        return sd_file, hdf_file

    return read_hdf


def mock_conn():
    return None
