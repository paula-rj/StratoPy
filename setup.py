from setuptools import setup

REQUIREMENTS = [
    "numpy",
    "pandas",
    "matplotlib",
    "geopandas",
    "cartopy",
    "pyhdf",
    "netcdf",
    "diskcache",
]

setup(
    name="StratoPy",
    version="0.1.0",
    description="",
    lond_description="",
    author="Paula Romero",
    author_email="",
    url="https://github.com/paula-rj/StratoPy",
    py_modules=None,
    packages=["stratopy"],
    include_package_data=True,
    license="The MIT License",
    keywords=["stratopy", "clouds"],
    classifiers=[
        "Development Status :: 4 -Beta",
        "Intended Audience :: Education",
        "Intended Audience :: Science/Research",
        "Programming Language :: Python :: 3.9",
    ],
)
