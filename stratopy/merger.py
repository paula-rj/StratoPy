import attr

import numpy as np

import pandas as pd

import cloudsat
import core
import goes


@attr.s(frozen=True, repr=False)
class StratoFrame:
    """[summary]"""

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

    # Paso 1: Chequear que las fechas de goes y de cloudsat sean parecidas
    # (no van a ser exactamente iguales, podriamos poner que tengan a lo sumo 30 min de diferencia)

    def merge(cloudsat_obj, goes_obj):
        metadata = dict(goes_obj._data.values())
        h = metadata[0][
            "goes_imager_projection"
        ].perspective_point_height  # goes height in m
        lon_cen = metadata[0][
            "goes_imager_projection"
        ].longitude_of_projection_origin
        scale_factor = metadata[0]["x"].scale_factor
        semieje_may = metadata[0]["goes_imager_projection"].semi_major_axis
        semieje_men = metadata[0]["goes_imager_projection"].semi_minor_axis
        p_size = 2004.0  # 1.1 km is cloudsat pixel size
        offset = np.array(
            [metadata[0]["x"].add_offset, metadata[0]["y"].add_offset]
        )

        x, y = core.latlon2scan(
            x.Latitude,
            x.Longitude,
            lon0=lon_cen,
            Re=semieje_may,
            Rp=semieje_men,
            h=h,
        )
        
        cloudsat_obj["row"] = cloudsat_obj.apply(
            lambda x: core.latlon2scan(
                x.Latitude,
                x.Longitude,
                lon0=lon_cen,
                Re=semieje_may,
                Rp=semieje_men,
                h=h,
            ),
            axis=1,
        )

        cloudsat_obj["col"] = cloudsat_obj.apply(
            lambda x: core.latlon2scan(
                x.Latitude,
                x.Longitude,
                lon0=lon_cen,
                Re=semieje_may,
                Rp=semieje_men,
                h=h,
            ),
            axis=1,
        )

        col = int((offset[1] + x) / scale_factor)
        fil = -int((offset[0] + y) / scale_factor)

        return cloudsat_obj

    # Paso 2: obtener la coord fil,col para cloudsat a partir de lat,lon (input)
    def get_fil(lat, lon, goes_obj):
        metadata = dict(goes_obj._data.values())
        h = metadata[0][
            "goes_imager_projection"
        ].perspective_point_height  # goes height in m
        lon_cen = metadata[0][
            "goes_imager_projection"
        ].longitude_of_projection_origin
        scale_factor = metadata[0]["x"].scale_factor
        semieje_may = metadata[0]["goes_imager_projection"].semi_major_axis
        semieje_men = metadata[0]["goes_imager_projection"].semi_minor_axis
        offset = np.array(
            [metadata[0]["x"].add_offset, metadata[0]["y"].add_offset]
        )
        p_size = 2004.0  # 1.1 km is cloudsat pixel size

        x, y = core.latlon2scan(
            x.Latitude,
            x.Longitude,
            lon0=lon_cen,
            Re=semieje_may,
            Rp=semieje_men,
            h=h,
        )
        fil = -int(
            (offset[0] + y) / scale_factor
        )  # obs! se simplifican las alturas
        return fil

    def get_col(lat, lon, goes_obj, cloudsat_df):
        metadata = dict(goes_obj._data.values())
        h = metadata[0][
            "goes_imager_projection"
        ].perspective_point_height  # goes height in m
        lon_cen = metadata[0][
            "goes_imager_projection"
        ].longitude_of_projection_origin
        scale_factor = metadata[0]["x"].scale_factor
        semieje_may = metadata[0]["goes_imager_projection"].semi_major_axis
        semieje_men = metadata[0]["goes_imager_projection"].semi_minor_axis
        p_size = 2004.0  # 1.1 km is cloudsat pixel size
        x, y = core.latlon2scan(
            lat, lon, lon0=lon_cen, Re=semieje_may, Rp=semieje_men, h=h
        )
        offset = np.array(
            [metadata[0]["x"].add_offset, metadata[0]["y"].add_offset]
        )
        col = int((offset[1] + x) / scale_factor)
        return col

    # Paso 2: añadir columnas al clousat dataframe con las coord fil,col para cada lat,lon
    def addfilcol(cloudsat_obj, goes_obj):
        """This function adds two columns to a cloudsat object,
        converting the (lat,lon) coordinate system (Cloudsat) to a
        (row,col) coordinate system where row and col are the
        correspondent row and column pixel of a GOES16 image.

        Parameters:
        -----------
            cloudsat_obj ([type]): A Cloudsat object
            goes_obj ([type]): A Goes object

        Returns:
        --------

        """
        cloudsat_obj["fil"] = cloudsat_obj.apply(
            lambda x: get_fil(x.Latitude, x.Longitude, goes_obj), axis=1
        )
        cloudsat_obj["col"] = cloudsat_obj.apply(
            lambda x: get_col(x.Latitude, x.Longitude, goes_obj), axis=1
        )

        return cloudsat_obj

    def superpix(cs_fila, cs_col, lat_lon_extent, GOES_path_list):
        """
        Parameters
        ----------
        cs_fila: int
        cs_col: int
        Columna en la que se encuentra el pixel de Cloudsat
        GOES_path_list: list[str]
        direcciónes en la que se encuentran los archivos de GOES

        Returns:
        -------
        superpix: np arrayEl punto de cloudsat + superpixel, pero todo de GOES ya en RRGB
        """
        superpix1 = metadato1["CMI"][:].data[cs_fila:cs_fila, cs_col:cs_col]
        superpix2 = metadato2["CMI"][:].data[cs_fila:cs_fila, cs_col:cs_col]
        superpix3 = metadato3["CMI"][:].data[cs_fila:cs_fila, cs_col:cs_col]

        superpix2b = solar_7(superpix2, superpix3, lat_lon_extent)

        RGBsuperpix = dayRGB(superpix1, superpix2b, superpix3)
        return RGBsuperpix
    
    def _verify_datetime(self):
        time_goes = self.goes._img_date_default
        time_cldsat = self.cs.read_time
        if time_goes not in time_cldsat:
            raise (
                f"The GOES and CloudSAT database are in different times "
                f"GOES time: {time_goes} \nCloudSAT time: {time_cldsat}"
            )
        return True
