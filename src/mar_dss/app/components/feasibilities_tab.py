"""
Feasibilities tab content for MAR DSS dashboard.
"""

import dash_bootstrap_components as dbc
from dash import html, dcc


def create_feasibilities_content():
    """Create content for Feasibilities tab."""
    return html.Div(
        [
            dbc.Row(
                [
                    # Executive Summary (Left Panel)
                    dbc.Col(
                        [
                            dbc.Card(
                                [
                                    dbc.CardHeader(
                                        "Executive Summary",
                                        className="fw-bold text-white",
                                        style={"backgroundColor": "#1e3a5f"}
                                    ),
                                    dbc.CardBody(
                                        id="executive-summary-content",
                                        children=[
                                            html.Div(
                                                "Loading feasibility analysis...",
                                                className="text-center text-muted p-4"
                                            )
                                        ]
                                    )
                                ],
                                className="h-100"
                            )
                        ],
                        width=6
                    ),
                    # Decision Funnel (Right Panel)
                    dbc.Col(
                        [
                            dbc.Card(
                                [
                                    dbc.CardHeader(
                                        "Decision Funnel",
                                        className="fw-bold text-white",
                                        style={"backgroundColor": "#1e3a5f"}
                                    ),
                                    dbc.CardBody(
                                        [
                                            dcc.Graph(
                                                id="decision-funnel-chart",
                                                style={"height": "300px"}  # Fixed height container
                                            ),
                                            html.Div(id="decision-funnel-stats", className="mt-3")
                                        ]
                                    )
                                ],
                                className="h-100"
                            )
                        ],
                        width=6
                    )
                ],
                className="mb-4"
            ),
            # Constraints Heatmaps (separated by type)
            dbc.Row(
                [
                    dbc.Col(
                        [
                            dbc.Card(
                                [
                                    dbc.CardHeader(
                                        "Hydrogeologic Constraints Heatmap",
                                        className="fw-bold text-white",
                                        style={"backgroundColor": "#1e3a5f"}
                                    ),
                                    dbc.CardBody(
                                        [
                                            dcc.Graph(
                                                id="hydrogeologic-constraints-heatmap-chart",
                                                style={"height": "400px"}
                                            ),
                                            html.Div(id="hydrogeologic-constraints-heatmap-legend", className="mt-3")
                                        ]
                                    )
                                ]
                            )
                        ],
                        width=12,
                        className="mb-3"
                    )
                ],
                className="mb-4"
            ),
            dbc.Row(
                [
                    dbc.Col(
                        [
                            dbc.Card(
                                [
                                    dbc.CardHeader(
                                        "Environmental Constraints Heatmap",
                                        className="fw-bold text-white",
                                        style={"backgroundColor": "#1e3a5f"}
                                    ),
                                    dbc.CardBody(
                                        [
                                            dcc.Graph(
                                                id="environmental-constraints-heatmap-chart",
                                                style={"height": "400px"}
                                            ),
                                            html.Div(id="environmental-constraints-heatmap-legend", className="mt-3")
                                        ]
                                    )
                                ]
                            )
                        ],
                        width=12,
                        className="mb-3"
                    )
                ],
                className="mb-4"
            ),
            dbc.Row(
                [
                    dbc.Col(
                        [
                            dbc.Card(
                                [
                                    dbc.CardHeader(
                                        "Regulation Constraints Heatmap",
                                        className="fw-bold text-white",
                                        style={"backgroundColor": "#1e3a5f"}
                                    ),
                                    dbc.CardBody(
                                        [
                                            dcc.Graph(
                                                id="regulation-constraints-heatmap-chart",
                                                style={"height": "400px"}
                                            ),
                                            html.Div(id="regulation-constraints-heatmap-legend", className="mt-3")
                                        ]
                                    )
                                ]
                            )
                        ],
                        width=12
                    )
                ],
                className="mb-4"
            ),
            # Spider Plots for Each MAR Option
            dbc.Row(
                [
                    dbc.Col(
                        [
                            dbc.Card(
                                [
                                    dbc.CardHeader(
                                        "MAR Option Performance Comparison",
                                        className="fw-bold text-white",
                                        style={"backgroundColor": "#1e3a5f"}
                                    ),
                                    dbc.CardBody(
                                        [
                                            html.Div(id="spider-plots-container")
                                        ]
                                    )
                                ]
                            )
                        ],
                        width=12,
                        className="mb-4"
                    )
                ]
            ),
            # Cost Comparison Charts
            dbc.Row(
                [
                    dbc.Col(
                        [
                            dbc.Card(
                                [
                                    dbc.CardHeader(
                                        "Cost Comparison",
                                        className="fw-bold text-white",
                                        style={"backgroundColor": "#1e3a5f"}
                                    ),
                                    dbc.CardBody(
                                        [
                                            dbc.Row(
                                                [
                                                    dbc.Col(
                                                        [
                                                            dcc.Graph(
                                                                id="capital-cost-chart",
                                                                style={"height": "350px"}
                                                            )
                                                        ],
                                                        width=4
                                                    ),
                                                    dbc.Col(
                                                        [
                                                            dcc.Graph(
                                                                id="maintenance-cost-chart",
                                                                style={"height": "350px"}
                                                            )
                                                        ],
                                                        width=4
                                                    ),
                                                    dbc.Col(
                                                        [
                                                            dcc.Graph(
                                                                id="npv-cost-chart",
                                                                style={"height": "350px"}
                                                            )
                                                        ],
                                                        width=4
                                                    )
                                                ]
                                            )
                                        ]
                                    )
                                ]
                            )
                        ],
                        width=12
                    )
                ]
            )
        ]
    )

