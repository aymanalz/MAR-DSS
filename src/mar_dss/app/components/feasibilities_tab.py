"""
Feasibilities tab content for MAR DSS dashboard.
"""

import dash_bootstrap_components as dbc
from dash import html, dcc


def create_feasibilities_content():
    """Create content for Feasibilities tab."""
    return html.Div(
        [
            # First row: Executive Summary and Decision Funnel
            dbc.Row(
                [
                    dbc.Col(
                        [
                            dbc.Card(
                                [
                                    dbc.CardHeader(
                                        "Executive Summary",
                                        className="fw-bold text-white py-2",
                                        style={"backgroundColor": "#1e3a5f", "fontSize": "0.9rem"}
                                    ),
                                    dbc.CardBody(
                                        id="executive-summary-content",
                                        children=[
                                            html.Div(
                                                "Loading feasibility analysis...",
                                                className="text-center text-muted p-2 small"
                                            )
                                        ],
                                        style={"padding": "0.75rem"}
                                    )
                                ],
                                className="h-100"
                            )
                        ],
                        width=6
                    ),
                    dbc.Col(
                        [
                            dbc.Card(
                                [
                                    dbc.CardHeader(
                                        "Decision Funnel",
                                        className="fw-bold text-white py-2",
                                        style={"backgroundColor": "#1e3a5f", "fontSize": "0.9rem"}
                                    ),
                                    dbc.CardBody(
                                        [
                                            dcc.Graph(
                                                id="decision-funnel-chart",
                                                style={"height": "250px"},
                                                config={"displayModeBar": False}
                                            ),
                                            html.Div(id="decision-funnel-stats", className="mt-2")
                                        ],
                                        style={"padding": "0.75rem"}
                                    )
                                ],
                                className="h-100"
                            )
                        ],
                        width=6
                    )
                ],
                className="mb-2"
            ),
            # Second row: Spider Plots
            dbc.Row(
                [
                    dbc.Col(
                        [
                            dbc.Card(
                                [
                                    dbc.CardHeader(
                                        "MAR Option Performance Comparison",
                                        className="fw-bold text-white py-2",
                                        style={"backgroundColor": "#1e3a5f", "fontSize": "0.9rem"}
                                    ),
                                    dbc.CardBody(
                                        [
                                            html.Div(id="spider-plots-container")
                                        ],
                                        style={"padding": "0.5rem"}
                                    )
                                ]
                            )
                        ],
                        width=12
                    )
                ],
                className="mb-2"
            ),
            # Third row: Constraints Heatmaps (2 per row)
            dbc.Row(
                [
                    dbc.Col(
                        [
                            dbc.Card(
                                [
                                    dbc.CardHeader(
                                        "Hydrogeologic Constraints",
                                        className="fw-bold text-white py-2",
                                        style={"backgroundColor": "#1e3a5f", "fontSize": "0.9rem"}
                                    ),
                                    dbc.CardBody(
                                        [
                                            dcc.Graph(
                                                id="hydrogeologic-constraints-heatmap-chart",
                                                style={"height": "300px"},
                                                config={"displayModeBar": False}
                                            ),
                                            html.Div(id="hydrogeologic-constraints-heatmap-legend", className="mt-2")
                                        ],
                                        style={"padding": "0.5rem"}
                                    )
                                ]
                            )
                        ],
                        width=6
                    ),
                    dbc.Col(
                        [
                            dbc.Card(
                                [
                                    dbc.CardHeader(
                                        "Environmental Constraints",
                                        className="fw-bold text-white py-2",
                                        style={"backgroundColor": "#1e3a5f", "fontSize": "0.9rem"}
                                    ),
                                    dbc.CardBody(
                                        [
                                            dcc.Graph(
                                                id="environmental-constraints-heatmap-chart",
                                                style={"height": "300px"},
                                                config={"displayModeBar": False}
                                            ),
                                            html.Div(id="environmental-constraints-heatmap-legend", className="mt-2")
                                        ],
                                        style={"padding": "0.5rem"}
                                    )
                                ]
                            )
                        ],
                        width=6
                    )
                ],
                className="mb-2"
            ),
            # Fourth row: Regulation Heatmap and Cost Comparison
            dbc.Row(
                [
                    dbc.Col(
                        [
                            dbc.Card(
                                [
                                    dbc.CardHeader(
                                        "Regulation Constraints",
                                        className="fw-bold text-white py-2",
                                        style={"backgroundColor": "#1e3a5f", "fontSize": "0.9rem"}
                                    ),
                                    dbc.CardBody(
                                        [
                                            dcc.Graph(
                                                id="regulation-constraints-heatmap-chart",
                                                style={"height": "300px"},
                                                config={"displayModeBar": False}
                                            ),
                                            html.Div(id="regulation-constraints-heatmap-legend", className="mt-2")
                                        ],
                                        style={"padding": "0.5rem", "minHeight": "350px"}
                                    )
                                ]
                            )
                        ],
                        width=6
                    ),
                    dbc.Col(
                        [
                            dbc.Card(
                                [
                                    dbc.CardHeader(
                                        "Cost Comparison",
                                        className="fw-bold text-white py-2",
                                        style={"backgroundColor": "#1e3a5f", "fontSize": "0.9rem"}
                                    ),
                                    dbc.CardBody(
                                        [
                                            dbc.Row(
                                                [
                                                    dbc.Col(
                                                        [
                                                            dcc.Graph(
                                                                id="capital-cost-chart",
                                                                style={"height": "300px"},
                                                                config={"displayModeBar": False}
                                                            )
                                                        ],
                                                        width=4
                                                    ),
                                                    dbc.Col(
                                                        [
                                                            dcc.Graph(
                                                                id="maintenance-cost-chart",
                                                                style={"height": "300px"},
                                                                config={"displayModeBar": False}
                                                            )
                                                        ],
                                                        width=4
                                                    ),
                                                    dbc.Col(
                                                        [
                                                            dcc.Graph(
                                                                id="npv-cost-chart",
                                                                style={"height": "300px"},
                                                                config={"displayModeBar": False}
                                                            )
                                                        ],
                                                        width=4
                                                    )
                                                ],
                                                className="justify-content-center align-items-center"
                                            )
                                        ],
                                        style={
                                            "padding": "0.5rem", 
                                            "minHeight": "350px",
                                            "display": "flex",
                                            "flexDirection": "column",
                                            "justifyContent": "center",
                                            "alignItems": "center"
                                        }
                                    )
                                ]
                            )
                        ],
                        width=6
                    )
                ],
                className="mb-2"
            ),
            dbc.Tooltip(
                "Text summary of integrated feasibility conclusions",
                target="executive-summary-content",
                placement="top",
            ),
            dbc.Tooltip(
                "Share of MAR options passing filters at each decision stage",
                target="decision-funnel-chart",
                placement="top",
            ),
            dbc.Tooltip(
                "Constraint intensity by option for hydrogeologic criteria",
                target="hydrogeologic-constraints-heatmap-chart",
                placement="top",
            ),
            dbc.Tooltip(
                "Constraint intensity for environmental criteria",
                target="environmental-constraints-heatmap-chart",
                placement="top",
            ),
            dbc.Tooltip(
                "Constraint intensity for permitting and regulatory criteria",
                target="regulation-constraints-heatmap-chart",
                placement="top",
            ),
            dbc.Tooltip(
                "Capital cost comparison across MAR technology options",
                target="capital-cost-chart",
                placement="top",
            ),
            dbc.Tooltip(
                "Annual maintenance cost comparison across options",
                target="maintenance-cost-chart",
                placement="top",
            ),
            dbc.Tooltip(
                "Net present value comparison across options",
                target="npv-cost-chart",
                placement="top",
            ),
        ],
        style={"padding": "0.5rem"}
    )
