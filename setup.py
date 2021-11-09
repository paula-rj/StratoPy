from setuptools import setup

with open("README.md", "r") as fp:
    LONG_DESCRIPTION = fp.read()


REQUIREMENTS = [
    "numpy",
    "pandas",
    "attrs",
    "matplotlib",
    "geopandas",
    "pyhdf",
    "pyorbital",
    "pyspectral",
    "netCDF4",
    "diskcache",
]

setup(
    name="StratoPy",
    version="0.1.0",
    description=(
        "Python library designed to easily manipulate CloudSat "
        "and GOES-R data and generate labeled images containing cloud types."
    ),
    long_description=LONG_DESCRIPTION,
    long_description_content_type="text/markdown",
    install_requires=REQUIREMENTS,
    author="Paula Romero, Georgynio Rosales, Jose Robledo, Julian Villa",
    author_email="paula.romero@mi.unc.edu.ar",
    url="https://github.com/paula-rj/StratoPy",
    py_modules=None,
    packages=["stratopy"],
    include_package_data=True,
    license="The MIT License",
    keywords=["stratopy", "clouds"],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Education",
        "Intended Audience :: Science/Research",
        "Programming Language :: Python :: 3.9",
    ],
)
