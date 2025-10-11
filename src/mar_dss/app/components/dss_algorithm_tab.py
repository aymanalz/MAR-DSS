"""
DSS Algorithm tab content for MAR DSS dashboard.
"""

import dash_bootstrap_components as dbc
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from dash import dcc, html


def create_dss_algorithm_content():
    """Create content for DSS Algorithm sidebar tab."""
    # Generate sample data
    dates = pd.date_range(start="2023-01-01", end="2023-12-31", freq="D")
    water_levels = np.random.normal(100, 10, len(dates)) + 5 * np.sin(
        np.arange(len(dates)) * 2 * np.pi / 365
    )

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=dates,
            y=water_levels,
            mode="lines+markers",
            name="Water Level",
            line=dict(color="#1f77b4", width=2),
            marker=dict(size=4),
        )
    )

    fig.update_layout(
        title="Water Level Monitoring",
        xaxis_title="Date",
        yaxis_title="Water Level (m)",
        hovermode="x unified",
        template="plotly_white",
    )

    return html.Div(
        [
            html.H3("DSS Algorithm Analysis"),
            html.P(
                "Advanced decision support algorithms for MAR project evaluation."
            ),
            dcc.Graph(figure=fig),
            html.Hr(),
            html.H5("Algorithm Parameters:"),
            dbc.Row(
                [
                    dbc.Col(
                        [
                            html.Label("Algorithm Type:"),
                            dbc.Select(
                                options=[
                                    {
                                        "label": "Multi-Criteria Decision Analysis",
                                        "value": "mcda",
                                    },
                                    {"label": "Fuzzy Logic", "value": "fuzzy"},
                                    {
                                        "label": "Neural Network",
                                        "value": "neural",
                                    },
                                    {
                                        "label": "Genetic Algorithm",
                                        "value": "genetic",
                                    },
                                ],
                                value="mcda",
                            ),
                        ],
                        width=6,
                    ),
                    dbc.Col(
                        [
                            html.Label("Confidence Level:"),
                            dbc.Input(type="number", value=85, min=0, max=100),
                        ],
                        width=6,
                    ),
                ],
                className="mb-3",
            ),
            html.H5("Results:"),
            html.P(
                "The DSS algorithm has analyzed your MAR project parameters and generated comprehensive recommendations based on multi-criteria decision analysis."
            ),
        ]
    )


