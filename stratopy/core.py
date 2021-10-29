import attr

import pandas as pd


@attr.s(frozen=True, repr=False)
class StratoFrame:
    """[summary]"""

    cld_df = attr.ib(
        validator=attr.validators.instance_of(pd.DataFrame),
        converter=pd.DataFrame,
    )

    def __getitem__(self, slice):
        return self.cld_df.__getitem__(slice)

    def __dir__(self):
        return super().__dir__() + dir(self.cld_df)

    def __getattr__(self, a):
        return getattr(self.cld_df, a)

    def __repr__(self) -> (str):
        """repr(x) <=> x.__repr__()."""
        with pd.option_context("display.show_dimensions", False):
            df_body = repr(self.cld_df).splitlines()
        df_dim = list(self.cld_df.shape)
        sdf_dim = f"{df_dim[0]} rows x {df_dim[1]} columns"
        footer = f"\nStratoFrame - {sdf_dim}"
        cloudsat_cldcls_repr = "\n".join(df_body + [footer])
        return cloudsat_cldcls_repr

    def __repr_html__(self) -> str:
        ad_id = id(self)

        with pd.option_context("display.show_dimensions", False):
            df_html = self.cld_df.__repr_html__()
        rows = f"{self.cld_df.shape[0]} rows"
        columns = f"{self.cld_df.shape[1]} columns"

        footer = f"StratoFrame - {rows} x {columns}"

        parts = [
            f'<div class="stratopy-data-container" id={ad_id}>',
            df_html,
            footer,
            "</div>",
        ]
        html = "".join(parts)
        return html
