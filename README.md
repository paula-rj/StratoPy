<p align="center">
<img src="https://github.com/paula-rj/StratoPy/blob/main/res/logo.jpg?raw=true" alt="logo" height="200"/>
</p>
<p align="center">
  <img src="https://img.shields.io/badge/python-3.9%2B-blue">
  <img src="https://img.shields.io/badge/License-MIT-blue.svg">
</p>
Python library designed to easily manipulate CloudSat and GOES-R and generate labeled images containing cloud types.

## Motivation:
Remote sensors aboard artificial satellites generate a lot of information every day. This information acquires spatial value when it can be transformed into something understandable to humans, such as the classification of satellite images. In this case, we focus on the classification of clouds in satellite images since knowing the type of cloud we can know its main characteristics and thus contribute to improve climate models and weather predictions. 
We use images from the ABI radiometer on board the GOES-16 geostationary satellite and develop two methods to classify the clouds observed in them:
1- We implement the Day Microphysics algorithm (\citar geocast ) which approximately shows each cloud type in a different color. 
2- We developed methods that allow to co-locate data from the CloudSat heliosynchronous satellite with GOES-16 images, being able to obtain a Pandas dATAFRAME with two columns, one is the pixels of the GOES images and the other gives a label to those pixels (provided by CloudSat) about the type of cloud that exists in those pixels. 

As for the second method (co-location of GOES data OVER CLOUDSAT), although there is literature on the subject we did not find any released code showing the procedure. Perhaps it could be done with other software that are usually paid. That is why we decided to develop Stratopy, so that in a free and simple way it can be used and generate a data structure ready to be used for example as input in supervised machine learning algorithms. 

## Requirements:

You need Python 3.9+ to run Stratopy. The following libraries will be installed: 
- [pyhdf](https://pypi.org/project/pyhdf/)
- [numpy](https://numpy.org/)
- [scipy](https://www.scipy.org/)
- [geopandas](https://geopandas.org/)
- [netcdf4](https://unidata.github.io/netcdf4-python/)
- [pyorbital](https://github.com/pytroll/pyorbital)
- [pyspectral](https://github.com/pytroll/pyspectral)

## Installation:

> pip install stratopy

## References:
The main functions that integrate [StratoPy] were construct helped in the next bibliography:
- [Cloudsat Overview](https://cloudsat.atmos.colostate.edu/CloudSat_overview.pdf)
- [Cloudsat Page](https://cloudsat.atmos.colostate.edu/)
- [Cloudsat Data Processing Center](http://www.cloudsat.cira.colostate.edu/)
- [CloudSat product 2B-CLDCLASS](https://www.cloudsat.cira.colostate.edu/data-products/2b-cldclass)

- [GOES-R Webpage](https://www.goes-r.gov/)
- [GOES-R in NOAA Satelite information system](https://www.noaasis.noaa.gov/GOES/goes_overview.html)
- [GOES-R image viewer](https://www.star.nesdis.noaa.gov/GOES/index.php)
- [Day Microphysics Quickguide: provides an aproximate interpretation about the product](https://weather.msfc.nasa.gov/sport/training/quickGuides/rgb/QuickGuide_DtMicroRGB_NASA_SPoRT.pdf)
