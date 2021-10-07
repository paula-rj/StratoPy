import datetime
import getpass
import io
import os
import pathlib
import tempfile
from collections.abc import Mapping
from ftplib import FTP, error_perm

import attr

from diskcache import Cache

from . import cloudsat


# ============================================================================
# CLASSES
# ============================================================================

# type: ignore
DEFAULT_CACHE_PATH = pathlib.Path(
    os.path.expanduser(os.path.join("~", "stratopy_cache"))
)


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


class FtpCloudsat(FTP):
    def __init__(self, server="ftp.cloudsat.cira.colostate.edu"):
        """Established FTP connection to Cloudsat server"""

        super().__init__()
        self.connect(host=server)
        user_name = input("login user name:")
        pwd = getpass.getpass(prompt="login password: ")
        # self.ftp = FTP(server)
        self.ftp = self.login(user_name, pwd)

    def download(self, file):
        """Downloads specific file"""
        print("Starting download")
        downloaded = self.retrbinary(f"RETR {file}", open(file, "wb").write)
        print("Finished download")
        return downloaded

    def quit(self):
        """Close connection with the server"""
        print("Closing connection with the server")
        self.quit()
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
            self.cwd(dirname)
            return self.dir()
        except error_perm as error:
            print(error)
            print("File not found. Try with other date or navigate to file.")

    def fetch(self, dirname):
        """Stores in-memory specific file from server as binary."""
        buffer = io.BytesIO()
        self.retrbinary(f"RETR {dirname}", buffer.write)
        return buffer


def fetch_cloudsat(dirname, path=DEFAULT_CACHE_PATH):
    """Fetch files of a certain date from cloudsat server and
    stores in a local cache.
    """
    cache = Cache(path)

    # Transform dirname into cache id
    id_ = os.path.split(dirname)[-1]
    # namevals = file_name.split("_")

    # date = namevals[0]
    # release = namevals[5] + '_' + namevals[6]
    # product = namevals[3]

    # str_date = datetime.date(*date).strftime("%Y/%j")
    # id_ = f"{product}_{release}_{date}"

    # Search in local cache
    cache.expire()
    # result = cache.get(id_)
    result = cache.get(id_, retry=True)

    if result is None:

        ftp = FTP()
        ftp.connect(host="ftp.cloudsat.cira.colostate.edu")
        user = input("login user name:")
        passwd = getpass.getpass(prompt="login password: ")
        ftp.login(user, passwd)

        buffer_file = io.BytesIO()
        ftp.retrbinary(f"RETR {dirname}", buffer_file.write)
        result = buffer_file.getvalue()

        cache.set(id_, result, tag="stratopy-cloudsat")

    with tempfile.TemporaryDirectory() as tmpdirname:
        fname = os.path.join(tmpdirname, id_)

        with open(fname, "wb") as fp:
            fp.write(result)

        df = cloudsat.CloudClass(fname)

    return df
