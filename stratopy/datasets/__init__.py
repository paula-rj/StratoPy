import os
import pathlib
import functools

import pandas as pd


PATH = pathlib.Path(os.path.abspath(os.path.dirname(__file__)))


@functools.lru_cache(maxsize=None)
def load_goes_latlon_ctable():
    return pd.read_json(PATH / "goes_latlong_convertion_table.json")
