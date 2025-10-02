"""
Decision Sensitivity tab content for MAR DSS dashboard.
"""

import dash_bootstrap_components as dbc
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from dash import dcc, html


def create_decision_sensitivity_content():
    """Create content for Decision Sensitivity sidebar tab."""
    # Generate sample data
    dates = pd.date_range(start="2023-01-01", end="2023-12-31", freq="D")
    recharge_data = np.random.exponential(2, len(dates)) * (
        1 + 0.5 * np.sin(np.arange(len(dates)) * 2 * np.pi / 365)
    )

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=dates,
            y=recharge_data,
            mode="lines+markers",
            name="Recharge Rate",
            line=dict(color="#ff7f0e", width=2),
            marker=dict(size=4),
        )
    )

    fig.update_layout(
        title="Recharge Rate Analysis",
        xaxis_title="Date",
        yaxis_title="Recharge Rate (m³/day)",
        hovermode="x unified",
        template="plotly_white",
    )

    return html.Div(
        [
            html.H3("Decision Sensitivity Analysis"),
            html.P(
                "Sensitivity analysis for decision parameters and their impact on outcomes."
            ),
            dcc.Graph(figure=fig),
            html.Hr(),
            html.H5("Sensitivity Parameters:"),
            dbc.Row(
                [
                    dbc.Col(
                        [
                            html.Label("Water Demand Variation:"),
                            dbc.Input(
                                type="number", value=10, min=0, max=50, step=1
                            ),
                        ],
                        width=4,
                    ),
                    dbc.Col(
                        [
                            html.Label("Climate Change Factor:"),
                            dbc.Input(
                                type="number",
                                value=1.2,
                                min=0.5,
                                max=2.0,
                                step=0.1,
                            ),
                        ],
                        width=4,
                    ),
                    dbc.Col(
                        [
                            html.Label("Economic Sensitivity:"),
                            dbc.Input(
                                type="number", value=15, min=5, max=30, step=1
                            ),
                        ],
                        width=4,
                    ),
                ],
                className="mb-3",
            ),
            html.H5("Sensitivity Results:"),
            html.P(
                "The sensitivity analysis shows how changes in key parameters affect the overall project viability and recommendations."
            ),
        ]
    )
