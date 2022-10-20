import io
import os
import pathlib

import pytest

import xarray as xa

DATA = pathlib.Path(os.path.abspath(os.path.dirname(__file__))) / "data"


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
