"""
Runoff Calculator tab components for MAR DSS dashboard.
"""

import dash_bootstrap_components as dbc
import plotly.graph_objects as go
from dash import dcc, html
import dash_leaflet as dl


def create_runoff_map(lat=38.5816, lon=-121.4944, zoom=10):
    """Create an interactive runoff analysis map using Leaflet."""
    return dl.Map(
        center=[lat, lon],
        zoom=zoom,
        children=[
            dl.TileLayer(url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"),
            dl.LayerGroup(id="marker-layer"),
            dl.LayerGroup(id="stations-layer"),
            dl.LayerGroup(id="watershed-layer"),
        ],
        style={'width': '100%', 'height': '500px', 'borderRadius': '8px', 'boxShadow': '0 4px 6px rgba(0, 0, 0, 0.1)'},
        id="runoff-map"
    )


def create_runoff_calculator_tab():
    """Create the content for the Runoff Calculator tab."""
    return [
        html.H3("Runoff Calculator", className="mb-4"),
        html.P("Calculate and analyze runoff patterns for your MAR project location.", className="mb-4"),

        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("Runoff Analysis Map", className="fw-bold bg-primary text-white"),
                    dbc.CardBody([
                        create_runoff_map()
                    ])
                ])
            ], width=8),

            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("Analysis Controls", className="fw-bold bg-primary text-white"),
                    dbc.CardBody([
                        dbc.Button(
                            "Obtain nearby streams",
                            id="obtain-streams-btn",
                            color="success",
                            className="me-2 mb-3"
                        ),
                        dbc.Button(
                            "Get Watershed Info",
                            id="get-watershed-btn",
                            color="info",
                            className="mb-3"
                        ),
                        html.Hr(),
                        html.Label("Watershed Area (acres):", className="fw-bold"),
                        dbc.Input(
                            id="watershed-area-input",
                            type="number",
                            value=1000,
                            min=1,
                            max=100000,
                            step=10,
                            style={"margin-bottom": "15px"}
                        ),

                        html.Label("Land Use Type:", className="fw-bold"),
                        dcc.Dropdown(
                            id="land-use-dropdown",
                            options=[
                                {"label": "Urban", "value": "urban"},
                                {"label": "Agricultural", "value": "agricultural"},
                                {"label": "Forest", "value": "forest"},
                                {"label": "Mixed", "value": "mixed"}
                            ],
                            value="mixed",
                            style={"margin-bottom": "15px"}
                        ),

                        html.Label("Rainfall (inches/year):", className="fw-bold"),
                        dbc.Input(
                            id="rainfall-input",
                            type="number",
                            value=25,
                            min=1,
                            max=200,
                            step=1,
                            style={"margin-bottom": "15px"}
                        ),

                        html.Label("Selected Latitude:", className="fw-bold"),
                        dbc.Input(
                            id="selected-latitude",
                            type="number",
                            value=None,
                            placeholder="Click map to set latitude",
                            step=0.000001,
                            style={"margin-bottom": "10px"}
                        ),

                        html.Label("Selected Longitude:", className="fw-bold"),
                        dbc.Input(
                            id="selected-longitude",
                            type="number",
                            value=None,
                            placeholder="Click map to set longitude",
                            step=0.000001,
                            style={"margin-bottom": "15px"}
                        ),

                        dbc.Button(
                            "Calculate Runoff",
                            id="calculate-runoff-btn",
                            color="primary",
                            className="me-2"
                        ),

                        html.Hr(),

                        html.Div(id="runoff-results", className="mt-3"),

                        html.Small(
                            "Click on the map to add monitoring points or draw watershed boundaries.",
                            className="text-muted"
                        )
                    ])
                ])
            ], width=4)
        ], className="mb-4"),

        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("Runoff Calculation Results", className="fw-bold bg-primary text-white"),
                    dbc.CardBody([
                        html.Div(id="runoff-calculation-output")
                    ])
                ])
            ])
        ])
    ]