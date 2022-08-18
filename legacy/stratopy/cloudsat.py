r"""Module containing all CloudSat satellite related classes and methods."""

import os
import pathlib

import attr

import geopandas as gpd

import numpy as np

import pandas as pd

from pyhdf.HDF import HC, HDF
from pyhdf.SD import SD
from pyhdf.VS import VS

# type: ignore
DEFAULT_CACHE_PATH = pathlib.Path(
    os.path.expanduser(os.path.join("~", "stratopy_cache"))
)


def read_hdf(path, layer="CloudLayerType"):
    """Read CloudSat data files, with extension ".hdf".

    Parameters
    ----------
    file_path: ``str``
        String containing local path to file.
    layer: ``str``, optional (default="CloudLayerType")
        Select any layer of the hdf file.

    Returns
    -------
    ``pandas.DataFrame``:
        Dataframe containing Latitude, Longitude and
        10 layers separated in columns.
    """
    try:
        hdf_file = HDF(path, HC.READ)
        vs = VS(hdf_file)
        vd_lat = attach_vdata(vs, "Latitude")
        lat = np.array(vd_lat[:]).flatten()
        vd_lon = attach_vdata(vs, "Longitude")
        lon = np.array(vd_lon[:]).flatten()

        seconds = np.array(attach_vdata(vs, "Profile_time"))[:, 0]
        TAI = vs.attach("TAI_start")[0][0]
        start = pd.to_datetime("1993-01-01") + pd.Timedelta(seconds=TAI)
        offsets = pd.to_timedelta(seconds, unit="s")
        hdf_time = pd.date_range(start=start, end=start, periods=offsets.size)
        hdf_time = hdf_time + offsets
    except Exception as error:
        raise error
    else:
        # Read sd data
        file_path = SD(path)
        cld_layertype = file_path.select(layer)[:]
        layers_df = {"read_time": hdf_time, "Longitude": lon, "Latitude": lat}
        for i, v in enumerate(np.transpose(cld_layertype)):
            layers_df[f"layer_{i}"] = v
        cld_df = CloudSatFrame(layers_df)
        vs.end()

    return cld_df


def attach_vdata(vs, varname):
    """Needed to obtain data from hd4 file.

    Operation that allows to extract the data from
    the hd4 format file that CloudSat is saved in.

    Parameters
    ----------
    vs : pyhdf.VS.VS
        Data from CloudSat image in hdf4 format.
    varname : string
        Name of the variable that wants to be loaded.

    Returns
    -------
    array-like
        Data of selected variable obtained from hdf4 Cloudsat file.
    """
    vdata = vs.attach(varname)
    data = vdata[:]
    vdata.detach()
    return data


@attr.s(frozen=True, repr=False)
class CloudSatFrame:
    """Make the CloudSatFrame.

    DataFrame used for manipulating Cloudsat and GOES data
    throughout this package.

    Attributes
    ----------
    data: attr.ib
        satellite image data.
    """

    _data = attr.ib(
        validator=attr.validators.instance_of(pd.DataFrame),
        converter=pd.DataFrame,
    )

    def __getitem__(self, slice):
        """x[y] <==> x.__getitem__(y)."""
        return self._data.__getitem__(slice)

    def __dir__(self):
        """dir(cdf) <==> cdf.__dir__()."""
        return super().__dir__() + dir(self._data)

    def __getattr__(self, a):
        """getattr(x, y) <==> x.__getattr__(y)."""
        return getattr(self._data, a)

    def __repr__(self):
        """repr(x) <=> x.__repr__()."""
        with pd.option_context("display.show_dimensions", False):
            df_body = repr(self._data).splitlines()
        df_dim = list(self._data.shape)
        sdf_dim = f"{df_dim[0]} rows x {df_dim[1]} columns"
        footer = f"\nCloudSatFrame - {sdf_dim}"
        return "\n".join(df_body + [footer])

    def _repr_html_(self):
        ad_id = id(self)

        with pd.option_context("display.show_dimensions", False):
            df_html = self._data._repr_html_()

        rows = f"{self._data.shape[0]} rows"
        columns = f"{self._data.shape[1]} columns"

        footer = f"CloudSatFrame - {rows} x {columns}"

        parts = [
            f'<div class="stratopy-data-container" id={ad_id}>',
            df_html,
            footer,
            "</div>",
        ]
        return "".join(parts)

    def cut(self, area=None):
        """Cut a specified area of an image.

        Cuts a specified area of an image given in as a
        list of four elements, which correspond to the
        latitud and longitud limits of the crop operation.

        Parameters
        ----------
        area : `list` of four elements, optional
            The list should be [lat_0, lat_1, lon_0, lon_1] where:
                - lat_0, latitude of minimal position
                - lat_1, latitude of maximal position
                - lon_0, longitude of minimal position
                - lon_1, longitude of maximal position

            by default cut will be south hemisphere.

        Returns
        -------
        cloudsat.CloudSatFrame
            Data frame cropped in the specified latitud and longitud interval.

        Raises
        ------
        ValueError
            If the area list does not contain 4 elements.
        """
        if not area:
            return CloudSatFrame(
                self._data.loc[
                    (self._data.Latitude < 0) & (self._data.Longitude < 0)
                ]
            )
        elif len(area) == 4:
            latitude_min = area[0]
            latitude_max = area[1]
            longitude_min = area[2]
            longitude_max = area[3]

            return CloudSatFrame(
                self._data.loc[
                    self._data["Latitude"].between(latitude_min, latitude_max)
                    & self._data["Longitude"].between(
                        longitude_min, longitude_max
                    )
                ]
            )
        else:
            raise ValueError("area must have length four")

    def convert_coordinates(
        self,
        projection="+proj=geos +h=35786023.0 +lon_0=-75.0 \
            +x_0=0 +y_0=0 +ellps=GRS80 +units=m +no_defs +sweep=x",
    ):
        """Convert the coordinates of the CloudSatFrame.

        Convert the coordinates of the CloudSatFrame in accordance
        to the defined projection.

        Parameters
        ----------
        projection : string, optional
            The reprojection that the user desires, \
        by default the geostationary projection for GOES-R \
        ( "+proj=geos +h=35786023.0 +lon_0=-75.0 +x_0=0 +y_0=0 \
        +ellps=GRS80 +units=m +no_defs +sweep=x" )

        Returns
        -------
        cloudsat.CloudSatFrame
            Returns reprojected CloudSatFrame.
        """
        geo_df = gpd.GeoDataFrame(
            self._data.values,
            columns=self._data.columns,
            index=self._data.index,
            geometry=gpd.points_from_xy(
                self._data["Longitude"], self._data["Latitude"]
            ),
        )
        # EPSG 4326 corresponds to coordinates in latitude and longitude
        geo_df.crs = "EPSG:4326"

        # Reprojecting into GOES16 geostationary projection
        geodf_to_proj = geo_df.to_crs(projection)
        return CloudSatFrame(geodf_to_proj)
