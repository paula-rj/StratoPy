import abc
import io
from abc import ABC

from dateutil import parser

import s3fs


class ConnectorABC(ABC):
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

    def parse_date(self, date):
        "arma la fecha como corresponde"
        return parser.parse(date)

    def fetch(self, date):
        pdate = self.parse_date(date)  # recorta el nombre
        endpoint = self.get_endpoint()  # de donde lo baja
        query = self._makequery(
            endpoint, pdate
        )  # arma la url completa para descargar
        fp = self._download(query)  # descarga, es el archivo en si
        presult = self._parse_result(fp)  # convierte a xarray
        return presult


class NothingHereError(FileNotFoundError):
    """Error raised is the file is not found in the server.
    Only one file, or nothing, can be downloaded.
    POR QUEEE
    """

    pass


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

        # list all available files
        avail = s3.glob(query)
        if not avail:
            raise NothingHereError(query)

        filepath = avail[0]

        # Open in-memory binary and write it
        with s3.open(filepath, "rb") as fp:
            result = fp.read()

        return io.BytesIO(result)
