import attr

from netCDF4 import Dataset

import numpy as np

import pandas as pd


from . import cloudsat as cs
from . import core


@attr.s(frozen=True, repr=False)
class StratoFrame:
    """Creates a StratoFrame, a kind of Pandas Dataframe
    in which co-located data from GOES16 and Cloudsat is fusioned are merged"""

    goes = attr.ib()
    cs = attr.ib()

    _df = attr.ib(
        init=False,
        validator=attr.validators.instance_of(pd.DataFrame),
        converter=pd.DataFrame,
    )

    @_df.default
    def _df_default(self):
        return pd.DataFrame({"GOES": self.goes.RGB, "CloudSat": self.cs._data})

    def __getitem__(self, slice):
        return self._df.__getitem__(slice)

    def __dir__(self):
        return super().__dir__() + dir(self._df)

    def __getattr__(self, a):
        return getattr(self._df, a)

    def __repr__(self):
        """repr(x) <=> x.__repr__()."""
        with pd.option_context("display.show_dimensions", False):
            df_body = repr(self._df).splitlines()
        df_dim = list(self._df.shape)
        sdf_dim = f"{df_dim[0]} rows x {df_dim[1]} columns"
        footer = f"\nStratoFrame - {sdf_dim}"
        return "\n".join(df_body + [footer])

    def __repr_html__(self):
        ad_id = id(self)

        with pd.option_context("display.show_dimensions", False):
            df_html = self._df.__repr_html__()
        rows = f"{self._df.shape[0]} rows"
        columns = f"{self._df.shape[1]} columns"

        footer = f"StratoFrame - {rows} x {columns}"

        parts = [
            f'<div class="stratopy-data-container" id={ad_id}>',
            df_html,
            footer,
            "</div>",
        ]
        return "".join(parts)

    def gen_vect(self, col_row, band_dict):
        """For a given (col,row) coordinate, generates a matrix of size 3x3x16
        where the central pixel is the one located in (col, fil) coordinate

        Parameters:
        ----------
        col_row: tuple

        band_dict: dict
        """
        band_vec = np.zeros((3, 3, 16))
        i = 0
        for band in band_dict.values():
            # normalizo la imagen
            band_vec[:, :, i] = band[
                col_row[1] - 1 : col_row[1] + 2,
                col_row[0] - 1 : col_row[0] + 2,
            ].copy()
            i = i + 1
        return np.array(band_vec)

    def _verify_datetime(self):
        time_goes = self.goes._img_date_default
        time_cldsat = self.cs.read_time
        if time_goes not in time_cldsat:
            raise (
                f"The GOES and CloudSAT database are in different times "
                f"GOES time: {time_goes} \nCloudSAT time: {time_cldsat}"
            )
        return True

    def merge(
        self,
        cloudsat_file,
        goes_file,
        all_layers=False,
        no_clouds=False,
        norm=True,
    ):

        """Merges data from Cloudsat with co-located data from GOES-16.

        Parameters:
        -----------

        cloudsat_file: str, path
        Total ClouSat file path

        goes_file: str, path
        Total GOES file path

        all_layers: bool
        If True, the final dataframe should include
        all layers of the CLDCLASS product.
        Default: False

        no_clouds: bool
        If Ture, the final dataframe should include
        coordinates where no clouds were detected by CloudSat.
        Default: False

        norm: bool
        If True, normalizes all GOES channels [0,1].
        Default:True

        Returns:
            stratoframe: cloudsat object
        """

        # GOES
        data = Dataset(goes_file)
        metadata = data.variables
        # h = 35786023.0  # goes height in m
        # lon_cen = -75.0
        # scale_factor = 5.6e-05
        # semieje_may = 6378137.0
        # semieje_men = 6356752.31414
        # p_size = 2004.0  # 1.1 km is cloudsat pixel size
        # offset = np.array([-0.151844,  0.151844], dtype='float32')

        band_dict = {}
        for i in range(1, 17):
            if i < 10:
                band = "CMI_C0" + str(i)
            else:
                band = "CMI_C" + str(i)
            img = metadata[band][:].data
            # Normalize data
            if norm:
                mini = np.amin(img[img != 65535.0])  # min
                dif = np.amax(img[img != 65535.0]) - mini  # max - min
                img = (img - mini) / dif
            band_dict.update({band: img})

        # Cloudsat
        cloudsat_obj = cs.read_hdf(cloudsat_file)
        cloudsat_obj = cloudsat_obj.cut([-45.0, 10.0, -78.0, -36.0])
        if all_layers is False:
            cloudsat_obj = cloudsat_obj.drop(
                [
                    "layer_1",
                    "layer_2",
                    "layer_3",
                    "layer_4",
                    "layer_5",
                    "layer_6",
                    "layer_7",
                    "layer_8",
                    "layer_9",
                ],
                axis=1,
            )
        if no_clouds is False:
            cloudsat_obj = cloudsat_obj[cloudsat_obj.capa_0 != 0]

        cloudsat_obj["col_row"] = cloudsat_obj.apply(
            lambda x: core.scan2colfil(
                core.latlon2scan(x.Latitude, x.Longitude),
            ),
            axis=1,
        )

        # Merge
        cloudsat_obj["goes_vec"] = cloudsat_obj.apply(
            lambda x: StratoFrame.gen_vect(x.col_row, band_dict), axis=1
        )

        return cloudsat_obj
