import io
import os
import pathlib
import tempfile
from ftplib import FTP

from diskcache import Cache
from diskcache.core import ENOVAL

import s3fs

from . import merger
from .cloudsat import read_hdf
from .goes import read_nc

# type: ignore
DEFAULT_CACHE_PATH = pathlib.Path(
    os.path.expanduser(os.path.join("~", "stratopy_cache"))
)


def fetch_cloudsat(
    dirname,
    user,
    passwd,
    host="ftp.cloudsat.cira.colostate.edu",
    tag="stratopy-cloudsat",
    path=DEFAULT_CACHE_PATH,
):
    """Fetch files of a certain date from cloudsat server and
    stores in a local cache.
    """
    cache = Cache(path)

    # Transform dirname into cache id
    id_ = os.path.split(dirname)[-1]

    # Search in local cache
    cache.expire()
    result = cache.get(id_, default=ENOVAL, retry=True)

    if result is ENOVAL:

        ftp = FTP()
        ftp.connect(host=host)
        ftp.login(user, passwd)

        buffer_file = io.BytesIO()
        ftp.retrbinary(f"RETR {dirname}", buffer_file.write)
        result = buffer_file.getvalue()

        cache.set(id_, result, tag=tag)

    with tempfile.TemporaryDirectory() as tmpdirname:
        fname = os.path.join(tmpdirname, id_)

        with open(fname, "wb") as fp:
            fp.write(result)

        df = read_hdf(fname)

    return df


# Esta función es fácilmente extendible a descargar por fecha aprox.
# Simplemente es guardar en una lista los archivos de la carpeta(con s3fs.ls)
# luego buscar el que más se acerca al horario deseado dentro de cierto margen.
# Se podría implementar en caso de poder hacer lo mismo con cloudstat
# (el problema ahí es el número de órbita).
def fetch_goes(
    dirname,
    tag="stratopy-goes",
    path=DEFAULT_CACHE_PATH,
):
    """Fetch files of a certain date from GOES server and
    stores in a local cache.
    """
    cache = Cache(path)

    # Transform dirname into cache id
    id_ = os.path.split(dirname)[-1]

    # Search in local cache
    cache.expire()
    result = cache.get(id_, default=ENOVAL, retry=True)

    if result is ENOVAL:
        # Starts connection with AWS S3 bucket
        s3 = s3fs.S3FileSystem(anon=True)

        # Open in-memory binary and write it
        buffer_file = io.BytesIO()
        with s3.open(dirname, "rb") as f:
            buffer_file.write(f.read())
        result = buffer_file.getvalue()

        cache.set(id_, result, tag=tag)

    with tempfile.TemporaryDirectory() as tmpdirname:
        fname = os.path.join(tmpdirname, id_)

        with open(fname, "wb") as fp:
            fp.write(result)

        goes_obj = read_nc((fname,))

    return goes_obj


def fetch(cloudsat_id, goes_id, cloudsat_kw=None, goes_kw=None):
    """[Summary]"""
    # Anon connection.
    goes_kw = {} if goes_kw is None else goes_kw
    goes_data = fetch_goes(goes_id, **goes_kw)

    # In this case cloudsat_kw can't be empty:
    # must have user and password to connect with server
    cloudsat_kw = {} if cloudsat_kw is None else cloudsat_kw
    cloudsat_data = fetch_cloudsat(cloudsat_id, **cloudsat_kw)

    return merger.StratoFrame(goes_data, cloudsat_data)
