.. _coord_change_module:

:mod:`stratopy.transformers.coord_change`
-----------------------------------------

.. automodule:: stratopy.transformers.coord_change


Examples
~~~~~~~~~
.. code-block:: python
    :linenos:
    
    from stratopy.transformers import coord_change
    # From GOES projection to lat lon
    x0 = -0.151872
    y0 = 0.151872
    sx, sy, sz  = coord_change.scan2sat(x0,y0)
    lat, lon = coord_change.sat2latlon(sx,sy,sz)
    
    # From (lat,lon) to GOES projection
    x,y  = coord_change.latlon2scan(0., -75.)
    lat, lon = coord_change.scan2sat(x,y)
