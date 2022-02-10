StratoPy
========
.. image:: https://img.shields.io/badge/python-3.9%2B-blue
   :alt: python badge

.. image:: https://img.shields.io/badge/License-MIT-blue.svg
   :alt: License badge

Python package designed to easily manipulate CloudSat and GOES-R and generate labeled images containing cloud types. 

About
-----

This package is intended for aiding machine learning data scientist in classifying cloud imagery data into different cloud types.
The main objective of Stratopy is to merge different sattelite image information into a simple data frame called `StratoFrame` which
can be used as input for neural network training with `Torch`.   

Requirements:
-------------

You need python 3.9+ to install Stratopy. For more information about installation, please refer to :ref:`installation-label`.

.. toctree::
   :maxdepth: 5
   :caption: Contents:

   self
   installation
   stratopy
   tutorial.ipynb