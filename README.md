<p align="center">
<img src="https://github.com/paula-rj/StratoPy/blob/main/res/logo.jpg?raw=true" alt="logo" height="200"/>
</p>
<p align="center">
  <img src="https://img.shields.io/badge/python-3.9%2B-blue">
  <img src="https://img.shields.io/badge/License-MIT-blue.svg">
  <img alt="GitHub" src="https://img.shields.io/github/license/paula-rj/StratoPy?style=plastic">
  [<img src="https://img.shields.io/github/license/paula-rj/StratoPy?style=plastic">](https://github.com/paula-rj/StratoPy)
</p>
Python library designed to easily manipulate CloudSat and GOES-R and generate labeled images containing cloud types.

## Motivation:
Remote sensors aboard artificial satellites generate a lot of information every day. This information acquires spatial value when it can be transformed into something understandable to humans, such as the classification of satellite images. In this case, we focus on the classification of clouds in satellite images since knowing the type of cloud we can know its main characteristics and thus contribute to improve climate models and weather predictions. 
We use images from the ABI radiometer on board the GOES-16 geostationary satellite and develop two methods to classify the clouds observed in them:
1- We implement the Day Microphysics algorithm (\citar geocast ) which approximately shows each cloud type in a different color. 
2- We developed methods that allow to co-locate data from the CloudSat heliosynchronous satellite with GOES-16 images, being able to obtain a Pandas dATAFRAME with two columns, one is the pixels of the GOES images and the other gives a label to those pixels (provided by CloudSat) about the type of cloud that exists in those pixels. 

As for the second method (co-location of GOES and CloudSat), although there is literature on the subject we did not find any released code showing the procedure. Perhaps it could be done with other software that are usually paid. That is why we developed Stratopy, so that in a free and simple way it can be used and generate a data structure ready to be used for example as input in supervised machine learning algorithms. 

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

With pip:

> pip install stratopy

Via git
> pip install git+https://github.com/paula-rj/StratoPy.git

**Warning**: If you install [Stratopy] in a `Colab Notebook`, you must also upgrade `Numpy`

```!pip install numpy --upgrade```

and then restart sesion. After that, you can work as usuall. This is due to a conflict between `Numpy` and `Pyorbital` that afects only `Colab Notebooks`.

## Quick information and references:
CloudSat is an artificial satellite, with a sun-synchronous orbit which has a revisit period of 16 days. Its  most important instrument is the Cloud Profiling Radar (CPR), which returns verftical profiles of clouds in particular. The satellite was launched in 2006 and since 2011 its battery suffers a failure. Given that the radar needs energy to work, only daytime products are usefull since that year on. In `Stratopy`, we developed a pipeline that includes the 2B-CLDCLASS product, a product of level 2 of processing that contains the type of cloud that the radar found along the satellite's track around the Earth.
The following web pages are usefull references:

- [Cloudsat Official Page](https://cloudsat.atmos.colostate.edu/)
- [Cloudsat Overview](https://cloudsat.atmos.colostate.edu/CloudSat_overview.pdf)
- [Cloudsat Data Processing Center](http://www.cloudsat.cira.colostate.edu/)
- [2B-CLDCLASS product](https://www.cloudsat.cira.colostate.edu/data-products/2b-cldclass)


GOES-16 is an artificial satellite launched in 2016. It contains the Advances Baseline Radiometer (ABI) on board, a multiespectral sensor that can take images in 16 different bands or channels. It is a geostationary satellite, located in a central longitud of -75° which allows ABI to take images of nearly the whole American continet in a mode called "Full Disk". The pipelines developed in `Stratopy` includes the Cloud and Moisture (CMI) products of level 2 of processing its two presentations: single band and Multi-band (MCMIPF). We also included the algorithm needed to create a Day Microphysics RGB (based on [Souza's code](https://geonetcast.wordpress.com/2019/07/03/python-script-examples-to-generate-goes-16-rgbs/)), which shows (aproximately) different types of clouds in different colors. The GOES-16 team provides a [Day Microphysics Quickguide](https://weather.msfc.nasa.gov/sport/training/quickGuides/rgb/QuickGuide_DtMicroRGB_NASA_SPoRT.pdf) in order to have some reference for the interpretation of this RGB image. The following webpages contain usefull information about the satellite and its products:
- [GOES-R Official Webpage](https://www.goes-r.gov/)
- [GOES-R in NOAA Satelite information system](https://www.noaasis.noaa.gov/GOES/goes_overview.html)
- [GOES-R image viewer](https://www.star.nesdis.noaa.gov/GOES/index.php)
