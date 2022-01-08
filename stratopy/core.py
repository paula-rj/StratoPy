import math

import numpy as np


def geo2grid(lat, lon, nc):

    # Apply scale and offset
    xscale, xoffset = nc["x"].scale_factor, nc["x"].add_offset
    yscale, yoffset = nc["y"].scale_factor, nc["y"].add_offset

    x, y = latlon2xy(lat, lon)
    col = (x - xoffset) / xscale
    lin = (y - yoffset) / yscale

    return int(lin), int(col)


def latlon2xy(lat, lon):
    # goes_imagery_projection:semi_major_axis
    req = 6378137  # meters
    #  goes_imagery_projection:inverse_flattening
    # invf = 298.257222096
    # goes_imagery_projection:semi_minor_axis
    rpol = 6356752.31414  # meters
    e = 0.0818191910435
    # goes_imagery_projection:perspective_point_height
    # + goes_imagery_projection:semi_major_axis

    H = 42164160  # meters
    # goes_imagery_projection: longitude_of_projection_origin
    lambda0 = -1.308996939

    # Convert to radians
    latRad = lat * (math.pi / 180)
    lonRad = lon * (math.pi / 180)

    # (1) geocentric latitude
    Phi_c = math.atan(((rpol ** 2) / (req ** 2)) * math.tan(latRad))
    # (2) geocentric distance to the point on the ellipsoid
    rc = rpol / (
        math.sqrt(1 - ((e ** 2) * (math.cos(Phi_c) * math.cos(Phi_c))))
    )
    # (3) sx
    sx = H - (rc * math.cos(Phi_c) * math.cos(lonRad - lambda0))
    # (4) sy
    sy = -rc * math.cos(Phi_c) * math.sin(lonRad - lambda0)
    # (5)
    sz = rc * math.sin(Phi_c)

    # x,y
    x = math.asin((-sy) / math.sqrt((sx * sx) + (sy * sy) + (sz * sz)))
    y = math.atan(sz / sx)

    return x, y


def scan2sat(x, y, lon0=-75.0, Re=6378000.0, Rp=6356000.0, h=3600000.0):
    """
    Transforma coordenadas de scaneo geostacionarias x,y
    en coordenadas cartesianas con origen en el satelite sx,sy,sz
    En base a 5.2.8.1 de PUG3
    Parameters
    ----------
    x : float, float arr numpy.ma.core.MaskedArray
       coordenada horizontal, en radianes
    y : float, float arr numpy.ma.core.MaskedArray
       coordenada vertical, en radianes. Paralelo al eje terrestre
        longitud
    lon0 : float
        longitud del satélite y origen del sistema de coordenadas planas
    Re: float
        radio ecuatorial, en m
    Rp: float
        radio polar, en m
    h: float
        altura del satélite respecto de la superficie, en m
    Returns
    -------
    sx : float, float arr
        coordenada hacia el centro de la tierra
    sy : float, float arr
        coordenada horizontal
    sz : float, float arr
        coordenada vertical
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
    sx, sy, sz, lon0=-75.0, Re=6378000.0, Rp=6356000.0, h=3600000.0
):
    """
    Transforma coordenadas cartesianas con origen
    en el satelite sx,sy,sz
    en coordenadas de latitud/longitud
    En base a 5.2.8.1 de PUG3
    Parameters
    ----------
    sx : float, float arr
        coordenada hacia el centro de la tierra
    sy : float, float arr
        coordenada horizontal
    sz : float, float arr
        coordenada vertical
    lon0 : float
        longitud del satélite y origen del sistema de coordenadas planas
    Re: float
        radio ecuatorial, en m
    Rp: float
        radio polar, en m
    h: float
        altura del satélite respecto de la superficie, en m
    Returns
    -------
    lat : float, float arr
        latitud
    lon : float, float arr
        longitud
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
    lat, lon, lon0=-75.0, Re=6378000.0, Rp=6356000.0, h=36000000.0
):
    """
    Transforma coordenadas de latitud/longitud
    a x/y en proyeccion geoestacionaria
    En base a 5.2.8.2 de PUG3
    Parameters
    ----------
    lat: float, float arr
        latitud
    lon: float, float arr
        longitud
    lon0: float, float arr
        longitud del satélite y origen del sistema de coordenadas planas
    Re: float,
        radio ecuatorial, en m
    Rp: float
        radio polar, en m
    h: float
        altura del satélite respecto de la superficie, en m
    Returns
    -------
    x : float, float arr
       coordenada horizontal, en radianes
    y : float, float arr
       coordenada vertical, en radianes. Paralelo al eje terrestre
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

    return y, x


def colfil2scan(col, fil, x0, y0, scale):
    """
    Transforma filas/columnas de la imagen a x/y en proyeccion geoestacionaria
    En base a 5.2.8.2 de PUG3
    Parameters
    ----------
    col : int, int arr
        columna
    fil : int, int arr
        fila
    x0 : float
        posición del x[0] en radianes
    y0 : float
        coordenada horizontal del primer punto, en radianes.
        Paralelo al eje terrestre
    scale : float
        tamaño del pixel en radianes
    Returns
    -------
    x : float, float arr
       coordenada horizontal, en radianes.
    y : float, float arr
       coordenada vertical, en radianes. Paralelo al eje terrestre
    """
    x = col * scale + x0
    y = -fil * scale + y0
    return x, y


def scan2colfil(x, y, x0, y0, scale, tipo=1):
    """
    Converts x/y coordinates into row, column coordinartes, 
    a geostationary projection. Based on PUG3, version 5.2.8.2
     
    Parameters
    ----------
    x : float, float arr
       coordenada vertical, en radianes
    x : float
       coordenada vertical del primer punto en radianes
    x0 : float
        posición del x[0] en radianes
    y0 : float
        coordenada horizontal del primer punto, en radianes.
        Paralelo al eje terrestre
    scale : float
        tamaño del pixel en radianes
    tipo : TYPE, optional
        tipo de salida. The default is 0 para float, 1 para int.
        
    Returns
    -------
    col : columna
    fil : fila
    """
    col = (x - x0) / scale
    fil = -(y - y0) / scale
    if tipo == 0:
        return col, fil
    elif tipo == 1:
        return round(col), round(fil)
    else:
        raise TypeError("Type must be 0 (float) or 1 (int)")
