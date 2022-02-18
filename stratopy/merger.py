r"""Contains the principal Data Frame class which allows for merging
satellite images."""

import attr

import numpy as np

import pandas as pd


from . import core


@attr.s(frozen=True, repr=False)
class StratoFrame:
    """Creates a StratoFrame.

    A StratoFrame is a kind of Pandas Dataframe
    in which co-located data from GOES16 and Cloudsat is fusioned are merged.

    Returns
    -------
    StratoFrame
        DataFrame with GOES and Cloudsat data fusioned and merged.
    """

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

    def _verify_datetime(self):
        time_goes = self.goes._img_date_default
        time_cldsat = self.cs.read_time
        if time_goes not in time_cldsat:
            raise (
                f"The GOES and CloudSAT database are in different times "
                f"GOES time: {time_goes} \nCloudSAT time: {time_cldsat}"
            )
        return True


def gen_vect(col_row, goes_obj):
    """For a given (col,row) coordinate, generates a matrix of size 3x3xN
    where the central pixel is the one located in (col, fil) coordinate.
    N should be 1 if the goes object contains one band CMI,
    N should be 3 if the goes object contains three band CMI,
    N should be 16 if goes object is a multi-band CMI.

    Parameters
    ----------
    col_row : tuple
        Column and row coordinates given as (col, row).
    band_dict : dict
        Dictionary where bands are defined.
    Returns
    -------
    array-like
        Band vector.
    """
    band_dict = goes_obj._data
    key_list = list(band_dict.keys())
    brows, bcols = band_dict.get(key_list[0])["CMI"][:].data.shape

    if col_row[0] > bcols or col_row[1] > brows:
        raise ValueError("Input column or row larger than image size")
    band_vec = np.zeros((3, 3, len(band_dict)))

    # cut
    for count, band in enumerate(band_dict.values()):
        band_vec[:, :, count] = band[
            col_row[1] - 1 : col_row[1] + 2,
            col_row[0] - 1 : col_row[0] + 2,
        ].copy()

    return np.array(band_vec)


def merge(
    cloudsat_obj,
    goes_obj,
    all_layers=False,
    no_clouds=False,
    norm=True,
):

    """Merges data from Cloudsat with co-located data from GOES-16.

    Parameters
    ----------
    cloudsat_file: str, path
        Total ClouSat file path.

    goes_file: str, path
        Total GOES file path.

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

    Returns
    -------
    Cloudsat Object
        DataFrame containing merged data.
    """

    # GOES
    # h = 35786023.0  # goes height in m
    # lon_cen = -75.0
    # scale_factor = 5.6e-05
    # semieje_may = 6378137.0
    # semieje_men = 6356752.31414
    # p_size = 2004.0  # 1.1 km is cloudsat pixel size
    # offset = np.array([-0.151844,  0.151844], dtype='float32')

    band_dict = {}
    for key in goes_obj.keys():
        img = goes_obj.get(key)
        # Normalize data
        if norm:
            mini = np.amin(img[img != 65535.0])  # min
            dif = np.amax(img[img != 65535.0]) - mini  # max - min
            img = (img - mini) / dif
        band_dict.update({key: img})

    # Cloudsat
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
        cloudsat_obj = cloudsat_obj[cloudsat_obj.layer_0 != 0]

    cloudsat_obj["col_row"] = cloudsat_obj.apply(
        lambda x: core.scan2colfil(
            core.latlon2scan(x.Latitude, x.Longitude),
        ),
        axis=1,
    )

    # Merge

    cloudsat_obj["goes_vec"] = cloudsat_obj.apply(
        lambda x: gen_vect(x.col_row, band_dict), axis=1
    )

    return cloudsat_obj
