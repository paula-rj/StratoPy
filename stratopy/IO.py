r"""Module containing magement function."""

import io
import os
import pathlib
import tempfile
from ftplib import FTP

from diskcache import Cache
from diskcache.core import ENOVAL

import s3fs

from . import core
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
    """Get cloudsat files.

    Fetch files of a certain date from cloudsat ftp server and
    stores in a local cache.

    Parameters
    ----------
    dirname : `str`
        Path to cloudsat image.
    user : `str`
        Username for cloudsat ftp connection.
    passwd : `str`
        Password for cloudsat ftp connection.
    host : `str`, optional
        Name of the url where the file is hosted.
    tag : `str`, optional
        Tag to be added to the cached file.
    path : `str`, optional
        Path where to save the cached file.

    Returns
    -------
    df : `stratopy.cloudsat.CloudSatFrame`
        Dataframe containing the image data.
    """
    cache = Cache(path)

    # Transform dirname into cache id (exact date)
    id_ = os.path.split(dirname)[-1].split("_")[0]

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
    """Get GOES files.

    Fetch files of a certain date from GOES server and
    stores in a local cache.

    Parameters
    ----------
    dirname : `str`
        Name of the cached file.
    tag : `str`
        Tag to append to name of cached file.
    path : `str`
        Location where to save the cached file.

    Returns
    -------
    goes_obj : `netCDF4.Dataset`
        GOES image data.
    """
    cache = Cache(path)

    # Transform dirname into cache id
    id_ = os.path.split(dirname)[-1].split("_")[3][1:]

    # Save filename
    filename = os.path.split(dirname)[-1]

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
        fname = os.path.join(tmpdirname, filename)

        with open(fname, "wb") as fp:
            fp.write(result)

        goes_obj = read_nc((fname,))

    return goes_obj


def fetch(cloudsat_id, goes_id, cloudsat_kw=None, goes_kw=None):
    """Run both fetches for CloudSat and GOES data and merges them.

    Parameters
    ----------
    cloudsat_id : str
        Path to cloudsat image.
    goes_id : str
        Path to GOES image.
    cloudsat_kw : str, optional
        Label to append to Cloudsat cached file, by default None
    goes_kw : str, optional
        Label to append to Cloudsat cached file, by default None

    Returns
    -------
    merger.StratoFrame
        Resulting merged DataFrame from both inputs.
    """
    # Anon connection.
    goes_kw = {} if goes_kw is None else goes_kw
    goes_data = fetch_goes(goes_id, **goes_kw)

    # In this case cloudsat_kw can't be empty:
    # must have user and password to connect with server
    cloudsat_kw = {} if cloudsat_kw is None else cloudsat_kw
    cloudsat_data = fetch_cloudsat(cloudsat_id, **cloudsat_kw)

    return core.merge(cloudsat_data, goes_data)
