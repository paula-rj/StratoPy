import io
import os
import xarray as xa
import numpy as np
import atexit
import shutil
import requests
import tempfile
import paramiko
from stat import *
import fnmatch
from pyhdf.HDF import HDF, HC
from pyhdf.VS import VS
from pyhdf.SD import SD, SDC
import pyhdf

""" DEFAULT_SSH_KEY = os.path.expanduser(os.path.join("~", ".ssh", "id_rsa"))
TEMP_DIR = tempfile.mkdtemp(prefix="stpy_cloudsat_")

atexit.register(shutil.rmtree, TEMP_DIR)  # al salir de PYTHON se ejecuta eso
atexit.register(print, "chau paula!")  # al salir de PYTHON se ejecuta eso


def retr(username="paula.romeroATmi.unc.edu.ar"):
    host = "www.cloudsat.cira.colostate.edu"
    port = 22

    transport = paramiko.Transport(host, port)
    keyfile = DEFAULT_SSH_KEY
    pkey = paramiko.RSAKey.from_private_key_file(keyfile, password="2022")

    transport.connect(username=username, pkey=pkey)

    pth = "Data/2B-CLDCLASS.P1_R05/2019/009/"

    client = paramiko.SSHClient()

    # Policy obj for automatically adding the hostname and new host key
    policy = paramiko.AutoAddPolicy()
    client.set_missing_host_key_policy(policy)

    # Starts connection with Cloudsat SFTP server
    client.connect(host, port=port, username=username, pkey=pkey)

    tmp_path = tempfile.mktemp(dir=TEMP_DIR)
    with client.open_sftp() as sftp:
        for filename in sftp.listdir(pth):
            if fnmatch.fnmatch(filename, "20190091550*"):
                full_path = "/".join([pth, filename])
                local_path = tmp_path
                f = sftp.get(
                    remotepath=full_path,
                    localpath=local_path,
                )

                return local_path """


#    with paramiko.SFTPClient.from_transport(transport) as sftp:
#        for entry in sftp.listdir_attr(path=pth):
#            if fnmatch.fnmatch(entry.filename, "20190091550*"):
#                full_path = "/".join([pth, entry.filename])
#                sftp.getfo(full_path, result)
#                result.seek(0)

#                return result

# with paramiko.SFTPClient.from_transport(self._transport) as sftp:
#    for entry in sftp.listdir_attr(path=store_dir):
#        if fnmatch.fnmatch(entry.filename, pattern):
#            full_path = "/".join([store_dir, entry.filename])
#            sftp.getfo(full_path, result)
#            result.seek(0)
#            return result

# Datasets
def opencs(result):
    sd_file = SD(result, SDC.READ)
    height = sd_file.select("Height").get()  # (36950, 125)
    cloud_scenario = sd_file.select("cloud_scenario").get()  # (36950, 125)
    cloudLayerBase = sd_file.select("CloudLayerBase").get()  # (36950, 10)
    cloudLayerTop = sd_file.select("CloudLayerTop").get()  # (36950, 10)
    cloudLayerType = sd_file.select("CloudLayerType").get()  # (36950, 10)

    # HDF
    hdf_file = HDF(result, HC.READ)
    vs = VS(hdf_file)

    # Important attributes, one number only
    vd_UTCstart = vs.attach("UTC_start")
    UTCstart = vd_UTCstart[:]
    vd_UTCstart.detach()

    vd_verticalBin = vs.attach("Vertical_binsize")
    vertical_Binsize = np.array(vd_verticalBin[:]).flatten()
    vd_verticalBin.detach()

    # geolocated data, 1D arrays
    vd_timeprofile = vs.attach("Profile_time")
    time = np.array(vd_timeprofile[:]).flatten()  # (36950,)
    vd_timeprofile.detach()

    vd_lat = vs.attach("Latitude")
    lat = np.array(vd_lat[:]).flatten()  # (36950,)
    vd_lat.detach()

    vd_lon = vs.attach("Longitude")
    lon = np.array(vd_lon[:]).flatten()  # (36950,)
    vd_lon.detach()

    vd_precip = vs.attach("Precip_flag")
    precip_flag = np.array(vd_precip[:]).flatten()  # (36950,)
    vd_precip.detach()

    vd_land = vs.attach("Navigation_land_sea_flag")
    land_sea_flag = np.array(vd_land[:]).flatten()  # (36950,)
    vd_land.detach()

    print(cloudLayerType.shape)
    # Array to Xarray

    np_arr10 = np.array([cloudLayerBase, cloudLayerTop, cloudLayerType])
    print(np_arr10.shape)

    coords125 = {
        "data": ["cloudsat_trace", "height"],
        "cloudsat_trace": np.arange(36950),
        "height": np.arange(125),
    }

    coords10 = {
        "data": ["base", "top", "layer"],
        "cloudsat_trace": np.arange(36950),
        "layer": np.arange(10),
    }

    xarr125 = xa.DataArray(
        [cloud_scenario, height],
        dims=["data", "cloudsat_trace", "height"],
        coords=coords125,
    )

    xarr10 = xa.DataArray(
        [cloudLayerBase, cloudLayerTop, cloudLayerType],
        dims=["data", "cloudsat_trace", "layer"],
        coords=coords10,
    )

    coords0 = {
        "geodata": ["time", "lat", "lon", "precip_flag", "land_sea_flag"],
        "cloudsat_trace": np.arange(36950),
    }
    xarr0 = xa.DataArray(
        [time, lat, lon, precip_flag, land_sea_flag],
        dims=["geodata", "cloudsat_trace"],
        coords=coords0,
    )

    ds = xa.Dataset(
        {
            "cloud_scenario": (["cloudsat_trace", "z"], cloud_scenario),
            "cloud_layer_type": (["cloudsat_trace", "layer"], cloudLayerType),
            "cloud_layer_base": (["cloudsat_trace", "layer"], cloudLayerBase),
            "cloud_layer_top": (["cloudsat_trace", "layer"], cloudLayerTop),
        },
        coords={
            "cloudsat_trace": np.arange(36950),
            "height": (["cloudsat_trace", "z"], height),
            "layer": np.arange(10),
            "lat": (["cloudsat_trace"], lat),
            "lon": (["cloudsat_trace"], lon),
            "time": (["cloudsat_trace"], time),
            "precip_flag": (["cloudsat_trace"], precip_flag),
            "land_sea_flag": (
                ["cloudsat_trace"],
                land_sea_flag,
            ),
        },
    )

    print(ds)
    return ds


opencs("2019002175851_67551_CS_2B-CLDCLASS_GRANULE_P1_R05_E08_F03.hdf")
