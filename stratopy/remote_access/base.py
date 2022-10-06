import abc
from abc import ABC

from dateutil import parser

import xarray as xr


class ConnectorABC(ABC):
    @abc.abstractmethod
    def get_endpoint(self):
        """Sirve para sacar en donde esta alojado el archivo.

        Ej: Amazon, pag de ftp, http.
        Varios satelites pueden usar el
        mismo tipo de host pero no la misma url.

        """
        raise NotImplementedError()

    @abc.abstractmethod
    def _makequery(self, endpoint, date):
        """Arma el string del producto.
        Exclusivo de cada satelite porque cada
        uno tiene sus tipos de productos y nomenclatura.
        Parameters
        endpoint: le pasa la url de donde esta alojado
        date: le pasa la fecha y el tipo
        entonces con esos dos construye url final de donde va a descargar"""
        raise NotImplementedError()

    @abc.abstractmethod
    def _download(self, query):
        """Descarga el archivo
        Parameters:
        query: le pasas la url completa para poder descargar"""
        raise NotImplementedError()

    @abc.abstractmethod
    def _parse_result(self, result):
        """Recibe el result que es el archivo descargado )en netcdf pej)  y
        lo convierte a un formato comun p ej xarray
        Parameters:
        result: el archivo en su formato original"""
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


class NetCDFmixin:
    def _parse_result(self, fp):
        """Convierte netcdf en xarray comun
        Parameters:
        result: es el archivo netcdf descargado

        Returns
        xarr: archivo leido y pasado a xarray"""

        xarr = xr.open_dataset(fp)
        return xarr


import io
import s3fs

class NothingHereError(FileNotFoundError):
    pass


class S3mixin:
    def _download(self, query):

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


# =============================================================================
# goes.py
# =============================================================================


def _default_product_parser(ptype, mode, chanel, dtime):
    # OR_ABI-L2-CMIPF-M3C03_G16_s20190021800
    pdate = dtime.strftime("%Y%j%H%M")
    parsed = f"OR_{ptype}-M{mode}C{chanel:02d}_G16_s{pdate}*"
    return parsed


def _whithout_chanel(ptype, mode, chanel, dtime):
    # OR_ABI-L2-CMIPF-M3C_G16_s20190021800
    pdate = dtime.strftime("%Y%j%H%M")
    parsed = f"OR_{ptype}-M{mode}_G16_s{pdate}*"
    return parsed


class GOES16(NetCDFmixin, S3mixin, ConnectorABC):

    _PRODUCT_TYPES_PARSERS = {
        "L1b-RadF": None,
        "ABI-L2-CMIPF": None,
        "ABI-L2-MCMIPF": _whithout_chanel,
        "ABI-L2-ACHTF": _whithout_chanel,
    }

    PRODUCT_TYPES = tuple(_PRODUCT_TYPES_PARSERS)

    _MODES = (1, 2, 3)

    def __init__(self, product_type, mode=3):
        # NOTA: POR ahora solo trabajamos con el sensor ABI
        # y con imagenes full disk, por eso son todos F

        if product_type not in self.PRODUCT_TYPES:
            raise ValueError(
                "Invalid product type. "
                f"Expected one of: {self.PRODUCT_TYPES}. "
                f"Found {product_type!r}"
            )
        if mode not in self._MODES:
            raise ValueError()

        self.mode = mode
        self.product_type = product_type
        self._ptype_parser = (
            self._PRODUCT_TYPES_PARSERS[product_type]
            or _default_product_parser
        )

    def get_endpoint(self):
        return "/".join(["noaa-goes16", self.product_type])

    def _makequery(self, endpoint, dt):

        date_dir = dt.strftime("%Y/%j/%H")
        file_glob = self._ptype_parser(self.product_type, self.mode, 3, dt)
        query = "/".join([endpoint, date_dir, file_glob])

        # noaa-goes16/ABI-L2-CMIPF/2019/002/18/OR_ABI-L2-CMIPF-M3C03_G16_s20190021800
        return query
