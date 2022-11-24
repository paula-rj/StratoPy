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
        """
        raise NotImplementedError()

    @abc.abstractmethod
    def _makequery(self, endpoint, date):
        """Meant to build the whole query needed
        to download the product.
        This method is unique for each satellite.
        Assumes that, given this two parameters,
        it is possible to build the whole string

        Parameters
        ----------
        endpoint: str
            Le pasa la url de donde esta alojado
        date: datetime obj
            le pasa la fecha y el tipo
        """
        raise NotImplementedError()

    @abc.abstractmethod
    def _download(self, query):
        """Meant to download the file.

        Parameters
        ----------
        query: str
            The query needed to download the product.
        """
        raise NotImplementedError()

    @abc.abstractmethod
    def _parse_result(self, result):
        """Converts the downloaded file into xarray object.

        Parameters:
        -----------
        result: the file in some format
        """
        raise NotImplementedError()

    @property
    def cache(self):
        return get_default_cache()

    @property
    def cache_tag(self):
        return type(self).__name__

    def parse_date(self, date):
        "arma la fecha como corresponde"
        return dateutil.parser.parse(date)

    def fetch(self, date, force=False):
        # recorta el nombre
        pdate = self.parse_date(date)

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
        presult = self._parse_result(fp)

        return presult


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
# S3 Mixin
# =============================================================================


class SFTPMixin:
    def _download(self, query):
        ...
