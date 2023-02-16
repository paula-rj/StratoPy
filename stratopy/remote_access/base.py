#!/usr/bin/env python
# -*- coding: utf-8 -*-
# License: MIT (https://tldrlegal.com/license/mit-license)
# Copyright (c) 2022, Paula Romero Jure et al.
# All rights reserved.

# =============================================================================
# IMPORTS
# =============================================================================

import abc
import atexit
import fnmatch
import io
import os
import shutil
import tempfile
from stat import *

import dateutil.parser

import paramiko

import pytz

import s3fs

from ..utils import from_cache, get_default_cache

# =============================================================================
# EXCEPTIONS
# =============================================================================


class NothingHereError(FileNotFoundError):
    """Error raised is the file is not found in the server.
    Only one file, or nothing, can be downloaded.

    """

    pass


# =============================================================================
# BASE CLASS
# =============================================================================


class ConnectorABC(abc.ABC):
    @abc.abstractmethod
    def get_endpoint(self):
        """Meant to return the url of the server where the files are stored.
        For example, AWS, FTP, HTTP.

        Raises
        ------
        NotImplementedError
            If this method is not implemented in a class
            that herits from ConnectorABC.
        """
        raise NotImplementedError()

    @abc.abstractmethod
    def _makequery(self, endpoint, date):
        """Meant to build the whole query needed
        to download the product.
        This method is unique for each satellite.
        Assumes that given the parameters it is possible to build the query.

        Parameters
        ----------
        endpoint: str
            Url where the products form a satellite are hosted.
        date: datetime obj
            requested date and time

        Raises
        ------
        NotImplementedError
            If this method is not implemented in a class
            that herits from ConnectorABC.
        """
        raise NotImplementedError()

    @abc.abstractmethod
    def _download(self, query):
        """Meant to download the file.

        Parameters
        ----------
        query: str
            The query needed to download the product.

        Raises
        ------
        NotImplementedError
            If this method is not implemented in a class
            that herits from ConnectorABC.
        """
        raise NotImplementedError()

    @abc.abstractmethod
    def _parse_result(self, result):
        """Meant to convert the downloaded file into xarray object.

        Parameters:
        -----------
        result: the file in some format

        Raises
        ------
        NotImplementedError
            If this method is not implemented in a class
            that herits from ConnectorABC.
        """
        raise NotImplementedError()

    @property
    def cache(self):
        return get_default_cache()

    @property
    def cache_tag(self):
        return type(self).__name__

    def parse_date(self, date, time_zone):
        """Builts the date for which a product will be downloaded.

        Parameters
        ----------
        date: str
            The date in format allowed by python-dateutils

        Returns
        -------
            datetime object
        """
        usr_date = dateutil.parser.parse(date)
        zone = pytz.timezone(time_zone)
        date_in_zone = zone.localize(usr_date)
        dt_utc = date_in_zone.astimezone(pytz.UTC)
        return dt_utc

    def fetch(self, date, tzone="UTC", force=False):
        """
        Downloads the requested product and retrieves it as xarray.

        Parameters
        ----------
        date: str

        Returns
        -------
        result_as_xr: xarray object
            Product as xarray object.
        """
        # recorta el nombre
        pdate = self.parse_date(date, tzone)

        # de donde lo baja
        endpoint = self.get_endpoint()

        # arma la url completa para descargar
        query = self._makequery(endpoint, pdate)

        # descarga, es el archivo en si
        fp = from_cache(
            cache=self.cache,
            tag=self.cache_tag,
            cache_expire=None,
            function=self._download,
            force=force,
            query=query,
        )

        # convierte a xarray
        result_as_xr = self._parse_result(fp)

        return result_as_xr


# =============================================================================
# S3 Mixin
# =============================================================================


class S3Mixin:
    def _download(self, query):
        """Downloads a file from AWS.

        Parameters
        ----------
        query: str or path
            The full query needed to download the file.
        """

        # Starts connection with AWS S3 bucket
        s3 = s3fs.S3FileSystem(anon=True)

        # Lists all available files
        avail = s3.glob(query)
        if not avail:
            raise NothingHereError(query)

        # TODO: Buscar la fecha mas cercana no la primera
        filepath = avail[0]

        # Open in-memory binary and write it
        with s3.open(filepath, "rb") as fp:
            result = fp.read()

        return io.BytesIO(result)


# =============================================================================
# SFTP Mixin
# =============================================================================

DEFAULT_SSH_KEY = os.path.expanduser(os.path.join("~", ".ssh", "id_rsa"))


class SFTPMixin:
    """Downloads a file from CloudSat SFTP server.

    Parameters
    ----------
    username: str
        username at CloudSat server
        https://www.cloudsat.cira.colostate.edu/
    keyfile: str
        File name for ssh public id.
        Default = None
    keypass: str
        Password for your ssh key. You may not have any.
        Default = None
    """

    def __init__(self, host, port, username, *, keyfile=None, keypass=None):
        if keyfile is None:
            keyfile = DEFAULT_SSH_KEY

        if "@" in username:
            username = username.replace("@", "AT", 1)

        # Client object
        self._client = paramiko.SSHClient()
        # self._transport = paramiko.Transport(host, port)

        # Policy obj for automatically adding the hostname and new host key
        policy = paramiko.AutoAddPolicy()
        self._client.set_missing_host_key_policy(policy)

        # Gets key file
        pkey = paramiko.RSAKey.from_private_key_file(keyfile, password=keypass)

        # Starts connection with Cloudsat SFTP server
        self._client.connect(host, port=port, username=username, pkey=pkey)
        # self._transport.connect(username=username, pkey=pkey)

    def __del__(self):
        self.close()

    def close(self):
        self._client.close()

    TEMP_DIR = tempfile.mkdtemp(prefix="stpy_cloudsat_")
    atexit.register(
        shutil.rmtree, TEMP_DIR
    )  # al salir de PYTHON se ejecuta eso
    atexit.register(print, "chau paula!")  # al salir de PYTHON se ejecuta eso

    def _download(self, query):
        TEMP_DIR = tempfile.mkdtemp(prefix="stpy_cloudsat_")
        atexit.register(
            shutil.rmtree, TEMP_DIR
        )  # al salir de PYTHON se ejecuta eso
        atexit.register(
            print, "chau paula!"
        )  # al salir de PYTHON se ejecuta eso
        tmp_path = tempfile.mktemp(dir=TEMP_DIR)
        store_dir, pattern = query.rsplit("/", 1)
        with self._client.open_sftp() as sftp:
            for filename in sftp.listdir(store_dir):
                if fnmatch.fnmatch(filename, pattern):
                    full_path = "/".join([store_dir, filename])
                    local_path = tmp_path
                    f = sftp.get(
                        remotepath=full_path,
                        localpath=local_path,
                    )

                    return local_path
