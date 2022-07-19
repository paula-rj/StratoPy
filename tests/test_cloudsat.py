import pandas as pd

import pytest

from stratopy import cloudsat


PATH = (
    "data/CloudSat/"
    "2019002175851_67551_CS_2B-CLDCLASS_GRANULE_P1_R05_E08_F03.hdf"
)

HDF_FILE = cloudsat.read_hdf(PATH)


def test_hdf_read():
    assert isinstance(HDF_FILE, cloudsat.CloudSatFrame)


def test_hdf_read_exception():
    with pytest.raises(Exception):
        cloudsat.read_hdf("non_existing_file.hdf")


def test_CloudDataFrame():
    assert not isinstance(cloudsat.CloudSatFrame, pd.DataFrame)


def test__getitem__():
    assert HDF_FILE[0:10].shape == (10, HDF_FILE.shape[1])
    assert HDF_FILE["Longitude"].shape == (HDF_FILE.shape[0],)


def test__dir__():
    assert len(dir(HDF_FILE)) > len(dir(HDF_FILE._data))


def test_repr():
    pdf = HDF_FILE
    with pd.option_context("display.show_dimensions", False):
        df_body = repr(pdf._data).splitlines()
    df_dim = list(pdf._data.shape)
    sdf_dim = f"{df_dim[0]} rows x {df_dim[1]} columns"
    footer = f"\nCloudSatFrame - {sdf_dim}"
    expected = "\n".join(df_body + [footer])
    assert repr(pdf) == expected


def test_repr_html():
    pdf = HDF_FILE
    ad_id = id(pdf)
    with pd.option_context("display.show_dimensions", False):
        df_html = pdf._data._repr_html_()
    rows = f"{pdf._data.shape[0]} rows"
    columns = f"{pdf._data.shape[1]} columns"
    footer = f"CloudSatFrame - {rows} x {columns}"
    parts = [
        f'<div class="stratopy-data-container" id={ad_id}>',
        df_html,
        footer,
        "</div>",
    ]
    expected = "".join(parts)

    assert pdf._repr_html_() == expected


def test_cut():
    trimmed_file = HDF_FILE.cut()
    assert trimmed_file.shape < HDF_FILE.shape


def test_cut_with_area():
    area_list = [-0.04492, 0.043348, 156.887802, 132.272720]
    trimmed_file = HDF_FILE.cut(area=area_list)
    assert trimmed_file.shape < HDF_FILE.shape


def test_cut_with_area_exception():
    area_list = [-0.04492, 0.043348]
    with pytest.raises(ValueError):
        HDF_FILE.cut(area=area_list)


def test_convert_coordinates():
    converted_file = HDF_FILE.convert_coordinates()
    assert len(HDF_FILE.columns) < len(converted_file.columns)
