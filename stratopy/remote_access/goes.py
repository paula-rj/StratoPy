import xarray as xa

from . import base


def _default_product_parser(ptype, mode, channel, dtime):
    # OR_ABI-L2-CMIPF-M3C03_G16_s20190021800
    pdate = dtime.strftime("%Y%j%H%M")
    parsed = f"OR_{ptype}-M{mode}C{channel:02d}_G16_s{pdate}*"
    return parsed


def _whithout_chanel(ptype, mode, dtime):
    # OR_ABI-L2-MCMIPF-M6_G16_s20190021800
    pdate = dtime.strftime("%Y%j%H%M")
    parsed = f"OR_{ptype}-M{mode}_G16_s{pdate}*"
    return parsed


class GOES16(base.S3Mixin, base.ConnectorABC):

    _PRODUCT_TYPES_PARSERS = {
        "L1b-RadF": None,
        "ABI-L2-CMIPF": None,
        "ABI-L2-MCMIPF": _whithout_chanel,
        "ABI-L2-ACHTF": _whithout_chanel,
    }

    PRODUCT_TYPES = tuple(_PRODUCT_TYPES_PARSERS)

    _MODES = (1, 2, 3, 4, 5, 6)

    def __init__(self, product_type, mode=6):
        # NOTA: POR ahora solo trabajamos con el sensor ABI
        # y con imagenes full disk, por eso son todos F

        if product_type not in self.PRODUCT_TYPES:
            raise ValueError(
                "Invalid product type. "
                f"Expected one of: {self.PRODUCT_TYPES}. "
                f"Found {product_type!r}"
            )
        if mode not in self._MODES:
            raise ValueError()

        self.mode = mode
        self.product_type = product_type
        self._ptype_parser = (
            self._PRODUCT_TYPES_PARSERS[product_type]
            or _default_product_parser
        )

    def get_endpoint(self):
        return "/".join(["s3:/", "noaa-goes16", self.product_type])

    def _makequery(self, endpoint, dt):
        date_dir = dt.strftime("%Y/%j/%H")
        file_glob = self._ptype_parser(self.product_type, self.mode, 3, dt)
        query = "/".join([endpoint, date_dir, file_glob])
        return query

    def _parse_result(self, result):
        xarr = xa.open_dataset(result, engine="h5netcdf")
        return xarr
