Installation
============

Installing with pip
-------------------

We recommend installing stratopy in a new environment. To install StratoPy run on a terminal

.. code-block:: sh

    pip install stratopy

Please make sure that the requirements are fullfilled. Stratopy requires `numpy`, `pandas`, `attrs`,
`matplotlib`, `geopandas`, `pyhdf`, `pyorbital`, `pyspectral`, `netCDF4`, `diskcache` and `s3fs`.

Installing with git
-------------------

It is also possible to install the version under development by cloning the github repository,

.. code-block:: sh

    git clone https://github.com/paula-rj/StratoPy.git

and afterwards installing it by running

.. code-block:: sh

    cd StratoPy
    pip install -e .