import datetime
import getpass
import os
import pathlib
from collections.abc import Mapping
from ftplib import FTP, error_perm

import attr

from diskcache import Cache


# ============================================================================
# CLASSES
# ============================================================================

# type: ignore


@attr.s(frozen=True, repr=False)
class MetaData(Mapping):
    """Implements an inmutable dict-like to store the metadata.
    Also provides attribute like access to the keys.
    Example
    -------
    >>> metadata = MetaData({"a": 1, "b": 2})
    >>> metadata.a
    1
    >>> metadata["a"]
    1
    """

    _data = attr.ib(converter=dict, factory=dict)

    def __repr__(self):
        """repr(x) <=> x.__repr__()."""
        return f"Metadata({repr(self._data)})"

    def __getitem__(self, k):
        """x[k] <=> x.__getitem__(k)."""
        return self._data[k]

    def __iter__(self):
        """iter(x) <=> x.__iter__()."""
        return iter(self._data)

    def __len__(self):
        """len(x) <=> x.__len__()."""
        return len(self._data)

    def __getattr__(self, a):
        """getattr(x, y) <==> x.__getattr__(y) <==> getattr(x, y)."""
        return self[a]


class FtpCloudsat:
    """
    Used to download CloudSata files from ftp-server

    To start will be needed:

    - file=None
    - server="ftp.cloudsat.cira.colostate.edu"):
    - "login user name:"
    - "login password: "

    """

    def __init__(self, file=None, server="ftp.cloudsat.cira.colostate.edu"):
        """Established FTP connection to Cloudsat server"""

        user_name = input("login user name:")
        pwd = getpass.getpass(prompt="login password: ")
        self.ftp = FTP(server)
        self.ftp.login(user_name, pwd)

        if file is not None:
            if ".hdf" in file:
                hdf = file.split("/")[-1]
                folder = file[: -len(hdf)]
                self.cd(folder)
                self.download(hdf)
            else:
                print("not an .hdf file. Please navigate to file")
        else:
            pass

    @property
    def ls(self):
        """List current directory files"""
        return self.ftp.dir()

    def cd(self, dir):
        """Allows to navigate in ftp host to file"""
        self.ftp.cwd(dir)
        return self.ftp.dir()

    def download(self, file):
        """Downloads specific file"""
        print("Starting download")
        downloaded = self.ftp.retrbinary(
            f"RETR {file}", open(file, "wb").write
        )
        print("Finished download")
        return downloaded

    def quit(self):
        """Close connection with the server"""
        print("Closing connection with the server")
        self.ftp.quit()
        print("Connection closed")
        return None

    def explore(self, date, product="2B-CLDCLASS", release="P1_R05"):
        """Access product directory and show files of a desire date.
        Parameters
        ----------
        date: ``int tuple``
            Tuple that contains date of observation in format (YYYY, MM, DD).
        product: ``str``, optional (defalult='2B-CLDCLASS')
            Cloudsat product.
        release: ``str``, optional (defalult='P1_R05')
            Cloudsat product version.

        Returns
        -------
        dirname: ``str``
            String containing the directory address of the input product
            and date.
        """
        str_date = datetime.date(*date).strftime("%Y/%j")
        dirname = f"{product}.{release}/{str_date}/"

        try:
            self.ftp.cwd(dirname)
            return self.ftp.dir()
        except error_perm as error:
            print(error)
            print("File not found. Try with other date or navigate to file.")


DEFAULT_CACHE_PATH = pathlib.Path(
    os.path.expanduser(os.path.join("~", "stratopy_cache"))
)


def fetch_cloudsat(
    dirname, product="2B-CLDCLASS", release="P1_R05", path=DEFAULT_CACHE_PATH
):
    """Fetch files of a certain date from cloudsat server and
    stores in a local cache.
    """
    cache = Cache(path)

    # Transform dirname into cache id
    file_name = os.path.split(dirname)[-1]
    date = file_name.split("_")[0]

    # str_date = datetime.date(*date).strftime("%Y/%j")
    id_ = f"{product}_{release}_{date}"

    # Search in local cache
    cache.expire()
    result = cache.get(id_)

    if result is None:
        # Search in cloudsat server and store in buffer
        # dirname = (
        # f"{product}.{release}/{str_date}/"
        # )

        ftp_cloudsat = FtpCloudsat()
        buffer_file = ftp_cloudsat.fetch(dirname)
        # -----------
        # procesar
        # ------------

        # Save file in local cache and delete buffer
        result = buffer_file.getvalue()
        cache.set(id_, result)

        buffer_file.close()

    return result
