#!/usr/bin/env python
# -*- coding: utf-8 -*-
# License: MIT (https://tldrlegal.com/license/mit-license)
# Copyright (c) 2022, Paula Romero Jure et al.
# All rights reserved.
r"""Contains methods to perform transformation operations on loaded images."""

import numpy as np


# =============================================================================
# Transformation functions (coords)
# =============================================================================
def scan2sat(x, y, Re=6378137.0, Rp=6356752.31414, h=35786023.0):
    """Convert scan to satellite coordinates.

    Transform x,y geostationary scan coordinates into
    cartesian coordinates with origin on the satellite. Based
    PUG3, version 5.2.8.1.

    Parameters
    ----------
    x : float, float arr numpy.ma.core.MaskedArray
        Horizontal coordinate, in radians.
    y : float, float arr numpy.ma.core.MaskedArray
        Vertical coordinate, in radians. Parallel to earth's axis.
        longitud
    Re: float
        Equatorial radius, in m.
    Rp: float
        Polar radius, in m.
    h: float
        Satellite's height, in m.

    Returns
    -------
    sx : float, float arr
        Coordinate pointing to the center of the Earth.
    sy : float, float arr
        Horizontal coordinate.
    sz : float, float arr
        Vertical coordinate.
    """
    if (
        str(type(x))[8:-2] != "numpy.ma.core.MaskedArray"
        or str(type(y))[8:-2] != "numpy.ma.core.MaskedArray"
    ):
        x = np.ma.MaskedArray(x)
        y = np.ma.MaskedArray(y)
    mask = x.mask

    H = Re + h  # satellite orbital radius
    a = np.sin(x) ** 2 + np.cos(x) ** 2 * (np.cos(y) ** 2 + (np.sin(y) * Re / Rp) ** 2)
    b = -2 * H * np.cos(x) * np.cos(y)
    c = H**2 - Re**2

    aux = b**2 - 4 * a * c

    rs = np.zeros(aux.shape)

    sx = np.ma.MaskedArray(np.zeros(aux.shape), mask)
    sy = np.ma.MaskedArray(np.zeros(aux.shape), mask)
    sz = np.ma.MaskedArray(np.zeros(aux.shape), mask)

    rs[aux >= 0] = -(b[aux >= 0] + np.sqrt(aux[aux >= 0])) / (2 * a[aux >= 0])

    sx[aux >= 0] = rs[aux >= 0] * np.cos(x[aux >= 0]) * np.cos(y[aux >= 0])
    sy[aux >= 0] = -rs[aux >= 0] * np.sin(x[aux >= 0])
    sz[aux >= 0] = rs[aux >= 0] * np.cos(x[aux >= 0]) * np.sin(y[aux >= 0])

    return sx, sy, sz


def sat2latlon(sx, sy, sz, lon0=-75.0, Re=6378137.0, Rp=6356752.31414, h=35786023.0):
    """Convert satellite to geographic coordinates.

    Transforms cartesian coordinates with origin
    in the satellite sx,sy,sz into
    latitude/longitude coordinates.
    Based on PUG3 5.1.2.8.1

    Parameters
    ----------
    sx : float, float arr
        Coordinate pointing to the Earth's center.
    sy : float, float arr
        Horizontal coordinate.
    sz : float, float arr
        Vertical coordinate.
    lon0 : float
        Satellite's longitude, origin of plane coordinate system.
    Re: float
        Equatorial radius, in m.
    Rp: float
        Polar radius, in m.
    h: float
        Satellite's height, in m.

    Returns
    -------
    lat : float, float arr
        Latitude coordinates.
    lon : float, float arr
        Longitude coordinates.

    """
    H = Re + h
    gr2rad = np.pi / 180

    lat = np.arctan((Re / Rp) ** 2 * sz / np.sqrt((H - sx) ** 2 + sy**2)) / gr2rad
    lon = lon0 - np.arctan(sy / (H - sx)) / gr2rad
    return lat, lon


def latlon2scan(lat, lon, lon0=-75.0, Re=6378137.0, Rp=6356752.31414, h=35786023.0):
    """Convert geographical to scan coordinates.

    Transform latitud/longitud coordinates
    into x/y geoestationary projection.
    Based on PUG3 5.1.2.8.2

    Parameters
    ----------
    lat: float, float arr
        Latitude.
    lon: float, float arr
        Longitude.
    lon0 : float
        Satellite's longitude, origin of plane coordinate system.
    Re: float
        Equatorial radius, in m.
    Rp: float
        Polar radius, in m.
    h: float
        Satellite's height, in m.

    Returns
    -------
    x : float, float arr
       Horizontal coordinate, in radianes.
    y : float, float arr
       Vertical coordinate, in radianes. Paralell to Earth's axis.
    """
    H = Re + h
    e = (1 - (Rp / Re) ** 2) ** 0.5  # excentricity
    gr2rad = np.pi / 180

    latc = np.arctan((Rp / Re) ** 2 * np.tan(lat * gr2rad))

    rc = Rp / (1 - (e * np.cos(latc)) ** 2) ** 0.5

    sx = H - rc * np.cos(latc) * np.cos((lon - lon0) * gr2rad)
    sy = -rc * np.cos(latc) * np.sin((lon - lon0) * gr2rad)
    sz = rc * np.sin(latc)

    s_norm = np.sqrt(sx**2 + sy**2 + sz**2)

    x = np.arcsin(-sy / s_norm)
    y = np.arctan(sz / sx)

    return x, y


def colfil2scan(col, row, x0=-0.151844, y0=0.151844, scale=5.6e-05):
    """Reproject into radians.

    Transforms columns/rows of the image into
    x/y en geostationary projection.
    Based on PUG3 5.1.2.8.2

    Parameters
    ----------
    col : int, int arr
        Selected column.
    row : int, int arr
        Selected row.
    x0 : float
        Position of the first coordinate x[0] in radians.
    y0 : float
        Horizontal coordinate of the first spot, in radians.
        Paralell to Earth's axis
    scale : float
        Pixel size in radians.

    Returns
    -------
    x : float, float arr
        Horizontal coordinate, in radianes.
    y : float, float arr
        Vertical coordinate, in radianes. Paralell to Earth's axis.
    """
    x = col * scale + x0
    y = -row * scale + y0
    return x, y


def scan2colfil(x, y, x0=-0.151844, y0=0.151844, scale=5.6e-05, tipo=1):
    """Get the coordinate possition.

    Converts x/y coordinates (scan projection) into (row,column) coordinates,
    a geostationary projection. Based on PUG3, version 5.2.8.2

    Parameters
    ----------
    x_y : float tuple, float arr
       Tuple containig, in radians,
       (horizontal coordinate x, vertical coordinate y).
    x0 : float
        Position of the first x cooridnate x[0] in radians.
    y0 : float
        Horizontal coordinate of the first spot, in radians.
        Paralell to Earth's axis.
    scale : float
        Pixel size, in radians.
    tipo : TYPE, optional
        Output type, 0 for float, 1 for int.
        Default: 1

    Returns
    -------
    col :
        column number coordinate.
    row :
        Row number coordinate.
    """
    col = (x - x0) / scale  # x
    row = -(y - y0) / scale  # y
    if tipo == 0:
        return col, row
    elif tipo == 1:
        return (np.rint(col)).astype(int), (np.rint(row)).astype(int)
    else:
        raise TypeError("Type must be 0 (float) or 1 (int)")
