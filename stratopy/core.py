import abc
from collections.abc import Mapping

import attr
from attr import validators

import pandas as pd

# ============================================================================
# CLASSES
# ============================================================================

# type: ignore

@attr.s(frozen=True, repr=False)
class MetaData(Mapping):
    """Implements an inmutable dict-like to store the metadata.
    Also provides attribute like access to the keys.
    Example
    -------
    >>> metadata = MetaData({"a": 1, "b": 2})
    >>> metadata.a
    1
    >>> metadata["a"]
    1
    """

    _data = attr.ib(converter=dict, factory=dict)

    def __repr__(self):
        """repr(x) <=> x.__repr__()."""
        return f"Metadata({repr(self._data)})"

    def __getitem__(self, k):
        """x[k] <=> x.__getitem__(k)."""
        return self._data[k]

    def __iter__(self):
        """iter(x) <=> x.__iter__()."""
        return iter(self._data)

    def __len__(self):
        """len(x) <=> x.__len__()."""
        return len(self._data)

    def __getattr__(self, a):
        """getattr(x, y) <==> x.__getattr__(y) <==> getattr(x, y)."""
        return self[a]

@attr.s(frozen=True, repr=False)
class StratoPyDataFrame:
    
    model = attr.ib(validator=attr.validators.instance_of(str))
    model_df = attr.ib(validator=attr.validators.instance_of(pd.DataFrame))
    
    metadata = attr.ib(factory=MetaData, converter=MetaData)
    
    def __getitem__(self, slice):
        sliced = self.model_df.__getitem__(slice)
        return StratoPyDataFrame(
            model=self.model,
            model_df=sliced,
            metadata=dict(self.metadata),
        )
    def __dir__(self):
        return super().__dir__() + dir(self.model_df)
    
    def __getattr__(self, a):
        return getattr(self.model_df, a)
    
    def __repr__(self) -> str:
        with pd.option_context("display.show_dimensions", False):
            df_body = repr(self.model_df).splitlines()
        df_dim = list(self.model_df.shape)
        sdf_dim = f"{df_dim[0]} rows x {df_dim[1]} columns"
        
        fotter = f"\nStratoPyDataFrame - {sdf_dim}"
        stratopy_data_repr = "\n".join(df_body + [fotter])
        return stratopy_data_repr
    
    def _repr_html_(self):
        ad_id = id(self)
        
        with pd.option_context("display.show_dimensions", False):
            df_html = self.model_df._repr_html_()
        
        rows = f"{self.model_df.shape[0]} rows"
        columns = f"{self.model_df.shape[1]} columns"
        
        footer = f"StratoPyDataFrame - {rows} x {columns}"
        
        parts = [
            f"<div class='stratopy-data-container' id={ad_id}>",
            df_html,
            footer,
            "</div>"
        ]
        html = "".join(parts)
        return html