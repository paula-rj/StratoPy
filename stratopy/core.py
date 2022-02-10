r"""Contains methods to perform transformation operations on loaded images."""

import numpy as np


def scan2sat(x, y, lon0=-75.0, Re=6378137.0, Rp=6356752.31414, h=35786023.0):
    """
    Transforms x,y geostationary scan coordinates into
    cartesian coordinates with origin on the satellite.
    Based PUG3, version 5.2.8.1.

    Parameters
    ----------
    x : float, float arr numpy.ma.core.MaskedArray
       horizontal coordinate, in radians
    y : float, float arr numpy.ma.core.MaskedArray
       vertical coordinate, in radians. Paralelo al eje terrestre
        longitud
    lon0 : float
        satellite's longitude, origin of plane coordinate system
    Re: float
        equatorial radius, in m
    Rp: float
        polar radius, in m
    h: float
        satellite's height, in m

    Returns
    -------
    sx : float, float arr
        coordinate pointing to the center of the Earth
    sy : float, float arr
        horizontal coordinate
    sz : float, float arr
        vertical coordinate
    """

    if (
        str(type(x))[8:-2] != "numpy.ma.core.MaskedArray"
        or str(type(y))[8:-2] != "numpy.ma.core.MaskedArray"
    ):
        x = np.ma.MaskedArray(x)
        y = np.ma.MaskedArray(y)
        # print ("cambia el tipo")
    mask = x.mask

    H = Re + h  # radio orbital del satelite
    a = np.sin(x) ** 2 + np.cos(x) ** 2 * (
        np.cos(y) ** 2 + (np.sin(y) * Re / Rp) ** 2
    )
    b = -2 * H * np.cos(x) * np.cos(y)
    c = H ** 2 - Re ** 2

    aux = b ** 2 - 4 * a * c

    rs = np.zeros(aux.shape)

    sx = np.ma.MaskedArray(np.zeros(aux.shape), mask)
    sy = np.ma.MaskedArray(np.zeros(aux.shape), mask)
    sz = np.ma.MaskedArray(np.zeros(aux.shape), mask)

    rs[aux >= 0] = -(b[aux >= 0] + np.sqrt(aux[aux >= 0])) / (2 * a[aux >= 0])

    sx[aux >= 0] = rs[aux >= 0] * np.cos(x[aux >= 0]) * np.cos(y[aux >= 0])
    sy[aux >= 0] = -rs[aux >= 0] * np.sin(x[aux >= 0])
    sz[aux >= 0] = rs[aux >= 0] * np.cos(x[aux >= 0]) * np.sin(y[aux >= 0])

    return sx, sy, sz


def sat2latlon(
    sx, sy, sz, lon0=-75.0, Re=6378137.0, Rp=6356752.31414, h=35786023.0
):
    """
    Transforms cartesian coordinates with origin
    in the satellite sx,sy,sz into
    latitude/longitude coordinates.
    Based on PUG3 5.1.2.8.1

    Parameters
    ----------
    sx : float, float arr
        coordinate pointing to the Earth's center
    sy : float, float arr
        horizontal coordinate
    sz : float, float arr
        vertical coordinate
    lon0 : float
        satellite's longitude, origin of plane coordinate system
    Re: float
        equatorial radius, in m
    Rp: float
        polar radius, in m
    h: float
        satellite's height, in m

    Returns
    -------
    lat : float, float arr
        latitude
    lon : float, float arr
        longitude
    """
    H = Re + h  # radio orbital del satelite
    gr2rad = np.pi / 180

    lat = (
        np.arctan((Re / Rp) ** 2 * sz / np.sqrt((H - sx) ** 2 + sy ** 2))
        / gr2rad
    )
    lon = lon0 - np.arctan(sy / (H - sx)) / gr2rad
    return lat, lon


def latlon2scan(
    lat, lon, lon0=-75.0, Re=6378137.0, Rp=6356752.31414, h=35786023.0
):
    """
    Transforms latitud/longitud coordinates
    into x/y geoestationary projection.
    Based on PUG3 5.1.2.8.2

    Parameters
    ----------
    lat: float, float arr
        latitude
    lon: float, float arr
        longitude
    lon0 : float
        satellite's longitude, origin of plane coordinate system
    Re: float
        equatorial radius, in m
    Rp: float
        polar radius, in m
    h: float
        satellite's height, in m

    Returns
    -------
    x : float, float arr
       horizontal coordinate, in radianes.
    y : float, float arr
       vertical coordinate, in radianes. Paralell to Earth's axis.
    """

    H = Re + h  # radio orbital del satelite
    e = (1 - (Rp / Re) ** 2) ** 0.5  # 0.0818191910435 # excentricidad
    gr2rad = np.pi / 180

    latc = np.arctan((Rp / Re) ** 2 * np.tan(lat * gr2rad))

    rc = Rp / (1 - (e * np.cos(latc)) ** 2) ** 0.5

    sx = H - rc * np.cos(latc) * np.cos((lon - lon0) * gr2rad)
    sy = -rc * np.cos(latc) * np.sin((lon - lon0) * gr2rad)
    sz = rc * np.sin(latc)

    s_norm = np.sqrt(sx ** 2 + sy ** 2 + sz ** 2)

    x = np.arcsin(-sy / s_norm)
    y = np.arctan(sz / sx)

    return x, y  # ojo aca estaban al reves y,x


def colfil2scan(col, row, x0=-0.151844, y0=0.151844, scale=5.6e-05):
    """
    Transforms columns/rows of the image into
    x/y en geostationary projection.
    Based on PUG3 5.1.2.8.2

    Parameters
    ----------
    col : int, int arr
        column
    row : int, int arr
        row
    x0 : float
        position of x[0] in radians
    y0 : float
        horizontal coordinate of the first spot, in radians.
        Paralell to Earth's axis
    scale : float
        pixel size in radians
    Returns
    -------
    x : float, float arr
       horizontal coordinate, in radianes.
    y : float, float arr
       vertical coordinate, in radianes. Paralell to Earth's axis.
    """
    x = col * scale + x0
    y = -row * scale + y0
    return x, y


def scan2colfil(x_y, x0=-0.151844, y0=0.151844, scale=5.6e-05, tipo=1):
    """
    Converts x/y coordinates (scan projection) into (row,column) coordinartes,
    a geostationary projection. Based on PUG3, version 5.2.8.2

    Parameters
    ----------
    x_y : float tuple, float arr
       tuple containig, in radians,
       (horizontal coordinate x, vertical coordinate y)
    x0 : float
        position of x[0] in radianes
    y0 : float
        horizontal coordinate of the first spot, in radians.
        Paralell to Earth's axis
    scale : float
        pixel size, in radians
    tipo : TYPE, optional
        output type, 0 for float, 1 for int.
        Default: 1

    Returns
    -------
    col : number of column
    row : number of row
    """
    col = (x_y[0] - x0) / scale  # x
    row = -(x_y[1] - y0) / scale  # y
    if tipo == 0:
        return col, row
    elif tipo == 1:
        return round(col), round(row)
    else:
        raise TypeError("Type must be 0 (float) or 1 (int)")
