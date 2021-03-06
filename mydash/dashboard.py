"""Dashboard Application.

This module is responsible for the configuration and creation of a Dash app
"""

# Third Party Libraries
import dash
import dash_core_components as dcc
import dash_html_components as html
import numpy as np
import plotly.express as px
from dash.dependencies import Input, Output
from dash_html_components import H1, H2, H3, Div, P

from .data import get_dataframes, groupby, list_assets

external_stylesheets = [
    {
        "href": "https://fonts.googleapis.com/css2?family=Lato:wght@400;700&display=swap",
        "rel": "stylesheet",
    },
]

assets = {}
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)


def dashboard(datapath: str) -> dash.Dash:
    """Create Plotly Dash App."""
    assets.update({asset_name: files for (asset_name, files) in list_assets(datapath)})
    app.layout = _set_layout(assets)
    return app


def _set_layout(assets):
    asset_names = sorted(assets.keys())
    header_elements = [
        Div(
            [
                H1("Data Asset Visualiser", className="header-title"),
                P("Load assets from JSON Lines files", className="header-description"),
            ],
            className="header",
        ),
        Div(
            dcc.Dropdown(
                id="asset-filter",
                options=[{"label": a, "value": a} for a in asset_names],
                value="",
                clearable=True,
                className="dropdown",
            ),
            className="menu",
        ),
    ]

    body = Div(_generate_body(), id="charts-body", className="wrapper")

    all_elements = header_elements + [body]

    return Div(all_elements)


def _generate_body(asset_name="", files=[]):
    elements = []

    elements.append(H2(" ".join(asset_name.split("-")).title()))

    df_records = groupby(get_dataframes(files), lambda x: ".".join(x["record_path"].split(".")[:-2]))

    for k, recs in df_records.items():
        # Header
        if k == "period":
            continue
        elements.append(H3(k))
        elements.append(Div(len(recs)))
        data = None
        if len(recs) == 1:
            # Data Vis: Chart or Table
            data = recs[0]["data"]
        elif len(recs) == 2:
            df_num_idx = 0 if _is_series_numeric(recs[0]["data"]["value"]) else 1
            df_str_idx = 1 - df_num_idx

            df_num = recs[df_num_idx]["data"]
            df_str = _reshape_dataframe_narrow_to_wide(recs[df_str_idx]["data"])
            join_keys = list(df_num.columns.intersection(df_str.columns))
            data = df_str.join(df_num.set_index(join_keys), on=join_keys, how="outer")

        if data is not None:
            if "value" in data.columns and _is_series_numeric(data["value"]) and "period" in data.columns:
                elements.append(_generate_chart(data, asset_name + k))
            else:
                elements.append(_generate_table(data))

    return elements


@app.callback(
    Output("charts-body", "children"),
    Input("asset-filter", "value"),
    prevent_initial_callback=True,
)
def _update_body(asset_filter_value):
    if asset_filter_value not in assets:
        return []
    else:
        return _generate_body(asset_filter_value, assets[asset_filter_value])


def _is_series_numeric(series):
    return series.dtype == np.float64 or series.dtype == np.int64


def _reshape_dataframe_narrow_to_wide(dataframe):
    row_keys = [c for c in dataframe.columns if c not in ["key", "value"]]
    col_keys = ["key"]
    df = dataframe.pivot(row_keys, col_keys).reset_index()

    # "pretty up" the column names stripping a layer of prior hierarchy
    df.columns = [str(c) if type(c) == int else c for c in df.columns]
    df.columns = [
        ".".join(c[1:]).strip() if type(c) == tuple and len(c) > 1 and c[0] == "value" else c
        for c in df.columns
    ]
    df.columns = ["".join(c).strip() if type(c) == tuple and len(c) > 1 else c for c in df.columns]
    return df


def _generate_table(dataframe, max_rows=10):
    df = _reshape_dataframe_narrow_to_wide(dataframe)
    td_style = {"textAlign": "center"}

    return html.Table(
        [
            html.Thead(html.Tr([html.Th(col) for col in df.columns])),
            html.Tbody(
                [
                    html.Tr([html.Td(df.iloc[i][col], style=td_style) for col in df.columns])
                    for i in range(min(len(df), max_rows))
                ]
            ),
        ],
        className="card",
        style={"width": "100%"},
    )


def _generate_chart(df, id=None):
    hover_keys = [c for c in df.columns if c not in ["key", "value", "period"]]
    fig = px.bar(df, x="period", y="value", color="key", hover_data=hover_keys)
    fig.update_layout(barmode="group")
    return dcc.Graph(id=id, figure=fig, className="card")
