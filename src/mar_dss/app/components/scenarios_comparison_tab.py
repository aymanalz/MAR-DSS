"""
Scenarios Comparison tab content for MAR DSS dashboard.
"""

import dash_bootstrap_components as dbc
import plotly.graph_objects as go
from dash import dcc, html


def create_scenarios_comparison_content():
    """Create content for Scenarios Comparison sidebar tab."""
    # Generate sample scenarios data
    scenarios = [
        "Baseline",
        "Optimistic",
        "Pessimistic",
        "Climate Change",
        "High Demand",
    ]
    water_supply = [75, 90, 60, 70, 65]
    cost_effectiveness = [80, 95, 65, 75, 70]
    environmental_impact = [70, 85, 55, 60, 75]

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=scenarios,
            y=water_supply,
            mode="lines+markers",
            name="Water Supply Security",
            line=dict(color="#2E8B57", width=3),
            marker=dict(size=8),
        )
    )
    fig.add_trace(
        go.Scatter(
            x=scenarios,
            y=cost_effectiveness,
            mode="lines+markers",
            name="Cost Effectiveness",
            line=dict(color="#4169E1", width=3),
            marker=dict(size=8),
        )
    )
    fig.add_trace(
        go.Scatter(
            x=scenarios,
            y=environmental_impact,
            mode="lines+markers",
            name="Environmental Impact",
            line=dict(color="#FF6347", width=3),
            marker=dict(size=8),
        )
    )

    fig.update_layout(
        title="Scenarios Comparison Analysis",
        xaxis_title="Scenario",
        yaxis_title="Score (%)",
        hovermode="x unified",
        template="plotly_white",
        height=500,
    )

    return html.Div(
        [
            html.H3("Scenarios Comparison"),
            html.P(
                "Compare different MAR project scenarios and their outcomes."
            ),
            dcc.Graph(figure=fig),
            html.Hr(),
            html.H5("Scenario Analysis:", className="mt-3"),
            html.Div(
                [
                    dbc.Row(
                        [
                            dbc.Col(
                                [
                                    html.H6(
                                        "Baseline Scenario", className="fw-bold"
                                    ),
                                    html.P(
                                        "Standard conditions with moderate growth"
                                    ),
                                    html.Ul(
                                        [
                                            html.Li("Water Supply: 75%"),
                                            html.Li("Cost Effectiveness: 80%"),
                                            html.Li("Environmental: 70%"),
                                        ]
                                    ),
                                ],
                                width=6,
                            ),
                            dbc.Col(
                                [
                                    html.H6(
                                        "Optimistic Scenario",
                                        className="fw-bold",
                                    ),
                                    html.P(
                                        "Best-case conditions with high efficiency"
                                    ),
                                    html.Ul(
                                        [
                                            html.Li("Water Supply: 90%"),
                                            html.Li("Cost Effectiveness: 95%"),
                                            html.Li("Environmental: 85%"),
                                        ]
                                    ),
                                ],
                                width=6,
                            ),
                        ]
                    )
                ]
            ),
            html.Hr(),
            html.H5("Recommendations:", className="mt-3"),
            html.P(
                "The Optimistic scenario shows the highest potential across all metrics. Consider implementing efficiency measures to achieve optimistic outcomes while preparing contingency plans for pessimistic conditions."
            ),
        ]
    )


