"""Dashboard Application.

This module is responsible for the configuration and creation of a Dash app
"""

# Third Party Libraries
import dash
import dash_core_components as dcc
import dash_html_components as html
import numpy as np
import plotly.express as px
from dash_html_components import H1, H2, H3, Div, P

from .data import get_dataframes, list_assets

external_stylesheets = [
    {
        "href": "https://fonts.googleapis.com/css2?" "family=Lato:wght@400;700&display=swap",
        "rel": "stylesheet",
    },
]


def dashboard(datapath):
    """Create Plotly Dash App."""
    app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
    assets = list_assets(datapath)
    app.layout = _set_layout(assets)
    return app


def _set_layout(assets):
    header_elements = [
        Div(
            [
                H1("Data Asset Visualiser", className="header-title"),
                P("Load assets from JSON Lines files", className="header-description"),
            ],
            className="header",
        )
    ]
    elements = []
    for asset_name, files in assets:
        if not asset_name.startswith("invoice-simulation"):
            continue
        elements.append(H2(" ".join(asset_name.split("-")).title()))
        dfs = get_dataframes(files)
        for df in dfs:
            data = df["data"]
            elements.append(H3(df["record_path"]))
            if "value" in data.columns and (
                data["value"].dtype == np.float64 or data["value"].dtype == np.int64
            ):

                if "period" in data.columns:
                    elements.append(_generate_chart(data, asset_name + df["record_path"]))
                else:
                    elements.append(_generate_table(data))

            else:
                elements.append(_generate_table(data))
    all_elements = header_elements + [Div(elements, className="wrapper")]
    return Div(all_elements)


def _generate_table(dataframe, max_rows=10):
    row_keys = [c for c in dataframe.columns if c not in ["key", "value"]]
    col_keys = ["key"]
    df = dataframe.pivot(row_keys, col_keys).reset_index()
    df.columns = [
        ".".join(c[1:]).strip() if type(c) == tuple and len(c) > 1 and c[0] == "value" else c
        for c in df.columns
    ]
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
