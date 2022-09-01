import abc
from abc import ABC
from dateutil import parser
import xarray 
import s3fs 
import io 


class ConnectorABC(ABC):
    @classmethod
    @abc.abstractmethod
    def get_endpoint(self):
        """Sirve para sacar en donde esta alojado el archivo.
        Ej: Amazon, pag de ftp, http.
        Varios satelites pueden usar el mismo tipo de host pero no la misma url."""
        raise NotImplementedError()

    @abc.abstractmethod
    def _makequery(self, endpoint, date):
        """Arma el string del producto.
        Exclusivo de cada satelite porque cada uno tiene sus tipos de productos y nomenclatura.
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

    def parse(self, date):
        return parser(date)
        
    def fetch(self, date):
        pdate = self.parse(date)  # recorta el nombre
        endpoint = self.get_endpoint()  # de donde lo baja
        query = self._makequery(
            endpoint, pdate
        )  # arma la url completa para descargar
        result = self._download(query)  # descarga, es el archivo en si
        presult = self._parse_result(result)  # convierte a xarray
        return presult


class NetCDFmixin():
    def _parse_result(self, result):
        """Convierte netcdf en xarray comun
        Parameters:
        result: es el archivo netcdf descargado
        
        Returns
        xarr: archivo leido y pasado a xarray"""

        xarr = xarray.open_dataset(result, engine={"netcdf4"})
        return xarr


class S3mixin():

    def _download(self, query):
        print(query)
        return None
        # Starts connection with AWS S3 bucket
        #s3 = s3fs.S3FileSystem(anon=True)

        # Open in-memory binary and write it
        #buffer_file = io.BytesIO()
        #with s3.open(query, "rb") as f:
        #    buffer_file.write(f.read())
        #result = buffer_file.getvalue()
        #
        #return result


class Goes16(NetCDFmixin, S3mixin, ConnectorABC):

    @classmethod
    def get_endpoint(
        self
    ):
        return None

    def _makequery(self, endpoint, date):
        print(endpoint,date)
        return None
