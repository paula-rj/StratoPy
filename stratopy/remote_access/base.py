#!/usr/bin/env python
# -*- coding: utf-8 -*-
# License: MIT (https://tldrlegal.com/license/mit-license)
# Copyright (c) 2022, Paula Romero Jure et al.
# All rights reserved.

# =============================================================================
# IMPORTS
# =============================================================================

import abc
import io

import dateutil.parser

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

    def parse_date(self, date, time_zone="UTC"):
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
        dt_utc = date_in_zone.astimezone(pytz.utc)
        return dt_utc

    def fetch(self, date, tzone, force=False):
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
        """ "Downloads a file from AWS.

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


class SFTPMixin:
    def _download(self, query):
        ...
