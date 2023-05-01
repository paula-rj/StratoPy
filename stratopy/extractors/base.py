#!/usr/bin/env python
# -*- coding: utf-8 -*-
# License: MIT (https://tldrlegal.com/license/mit-license)
# Copyright (c) 2022, Paula Romero Jure et al.
# All rights reserved.

r"""This module defines the abstract methods that must be implemented
every for each new extractor, within the Connector class.
Besides, it implements a perse_date function and a fetch funtion,
that integrates the whole downloading pipeline.
The extraction classes for every host, ie AWS, SFTP, and any other,
are also implemenmted in the base module."""
# =============================================================================
# IMPORTS
# =============================================================================

import abc
import atexit
import fnmatch
import io
import os
import tempfile


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
    """Base class for implementing any extractor.

    Methods
    -------
    get_endpoint:
        Gets host url.
    _makequery:
        Retrieves the whole url for downloading a product.
    _download:
        Downloads a product.
    _parse_result:
        Returns the original product as an Xarray Dataset.
    parse_date:
        Recieves the date for the download as a str.
    fetch:
        Coordinates all the pipeline for downloading a product.
    """

    @abc.abstractmethod
    def get_endpoint(self):
        """Returns the url of the server where the files are stored.
        For example, AWS, SFTP, HTTP.

        Raises
        ------
        NotImplementedError
            If this method is not implemented in a class
            that herits from ConnectorABC.
        """
        raise NotImplementedError()

    @abc.abstractmethod
    def _makequery(self, endpoint, date):
        """Builds the whole query needed to download the product.
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
        """Download one file.

        Parameters
        ----------
        query: str
            The query needed to download a product.

        Raises
        ------
        NotImplementedError
            If this method is not implemented in a class
            that herits from ConnectorABC.
        """
        raise NotImplementedError()

    @abc.abstractmethod
    def _parse_result(self, result):
        """Converts the downloaded file into Xarray object.

        Parameters:
        -----------
        result: the file in the format,
            for example, bytes, HDF, etc.

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
        """Builts the date in UTC format, from a str,
            for which a product will be downloaded.

        Parameters
        ----------
        date: str
            The date in format allowed by python-dateutils.
        time_zone: str
            The time zone for the input date and time.

        Returns
        -------
            dt_utc: datetime object
                Date and time in UTC as datetime object.
        """
        usr_date = dateutil.parser.parse(date)
        zone = pytz.timezone(time_zone)
        date_in_zone = zone.localize(usr_date)
        dt_utc = date_in_zone.astimezone(pytz.UTC)
        return dt_utc

    def fetch(self, date, tzone="UTC", force=False):
        """
        Downloads the requested product and retrieves it as xarray Dataset.

        Parameters
        ----------
        date: str
            Date and time for downloading the product.
        tzone: str
            default: "UTC"
            Time zone for the given date and time.
        force: bool
            default: False
            Forces to download the file even if it is in the cache.

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
    """Implements an extractor from AWS.

    Methods
    -------
    _download:
        Downloads a products given a query.
    """

    def _download(self, query):
        """Downloads a file from AWS and returns it as Bytes.

        Parameters
        ----------
        query: str or path
            The full query needed to download the file.

        Returns
        -------
        result: Bytes
            File in bytes.
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
    """Implements an extractor from a SFTP server.

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

    Methods
    -------
    close:
        Closes connection.
    _download:
        Downloads a product given a query.

    """

    def __init__(self, host, port, username, *, keyfile=None, keypass=None):
        if keyfile is None:
            keyfile = DEFAULT_SSH_KEY

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

    def _download(self, query):
        """Downloads a file from a SFTP server.

        Parameters
        ----------
        query: str
            url for downloading the product.

        Returns
        -------
        tmp_path: str or Path
            Temporary path where HDF4 file is stored.

        """
        store_dir, pattern = query.rsplit("/", 1)

        # Creates sftp session (on SSH server) object
        with self._client.open_sftp() as sftp:
            # Raises FileNotFoundError if file not found

            for filename in sftp.listdir(store_dir):
                if fnmatch.fnmatch(filename, pattern):
                    full_path = "/".join([store_dir, filename])

                    # temporary container
                    cls_name = type(self).__name__
                    _, tmp_path = tempfile.mkstemp(prefix=f"stpy_{cls_name}_")
                    atexit.register(os.remove, tmp_path)

                    # Downloads file from full and copies into tmp
                    sftp.get(remotepath=full_path, localpath=tmp_path)

                    # Returns temps cause parse_result gets a path as input
                    return tmp_path
