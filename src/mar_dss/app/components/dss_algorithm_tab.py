"""
DSS Algorithm tab content for MAR DSS dashboard.
Multi-Criteria Decision Support System (MCDSS).
"""

import dash_bootstrap_components as dbc
from dash import dcc, html


def create_dss_algorithm_content():
    """Create content for DSS Algorithm tab."""
    return html.Div(
        [
            # Compact header with description
            dbc.Row(
                dbc.Col(
                    html.P(
                        "Weighted sum multi-criteria decision analysis (MCDA) to rank MAR options. "
                        "Adjust weights to reflect the relative importance of each criterion.",
                        className="text-muted mb-3 small"
                    ),
                    width=12
                )
            ),
            # Weights in compact grid
            dbc.Row(
                [
                    dbc.Col(
                        [
                            html.Label("Hydrogeologic", className="small fw-bold mb-1"),
                            dbc.Input(
                                id="weight-hydrogeologic",
                                type="number",
                                value=1.0,
                                min=0,
                                max=10,
                                step=0.1,
                                size="sm"
                            )
                        ],
                        width=2
                    ),
                    dbc.Col(
                        [
                            html.Label("Environmental", className="small fw-bold mb-1"),
                            dbc.Input(
                                id="weight-environmental",
                                type="number",
                                value=1.0,
                                min=0,
                                max=10,
                                step=0.1,
                                size="sm"
                            )
                        ],
                        width=2
                    ),
                    dbc.Col(
                        [
                            html.Label("Regulation", className="small fw-bold mb-1"),
                            dbc.Input(
                                id="weight-regulation",
                                type="number",
                                value=1.0,
                                min=0,
                                max=10,
                                step=0.1,
                                size="sm"
                            )
                        ],
                        width=2
                    ),
                    dbc.Col(
                        [
                            html.Label("Capital Cost Eff.", className="small fw-bold mb-1"),
                            dbc.Input(
                                id="weight-capital-cost",
                                type="number",
                                value=1.0,
                                min=0,
                                max=10,
                                step=0.1,
                                size="sm"
                            )
                        ],
                        width=2
                    ),
                    dbc.Col(
                        [
                            html.Label("Maint. Cost Eff.", className="small fw-bold mb-1"),
                            dbc.Input(
                                id="weight-maintenance-cost",
                                type="number",
                                value=1.0,
                                min=0,
                                max=10,
                                step=0.1,
                                size="sm"
                            )
                        ],
                        width=2
                    ),
                    dbc.Col(
                        [
                            html.Label("NPV Efficiency", className="small fw-bold mb-1"),
                            dbc.Input(
                                id="weight-npv",
                                type="number",
                                value=1.0,
                                min=0,
                                max=10,
                                step=0.1,
                                size="sm"
                            )
                        ],
                        width=2
                    )
                ],
                className="mb-3"
            ),
            # Main content row: Decision Matrix and Results side by side
            dbc.Row(
                [
                    # Decision Matrix - Left side
                    dbc.Col(
                        [
                            dbc.Card(
                                [
                                    dbc.CardHeader(
                                        "Decision Matrix",
                                        className="fw-bold text-white py-2",
                                        style={"backgroundColor": "#1e3a5f", "fontSize": "0.9rem"}
                                    ),
                                    dbc.CardBody(
                                        id="dss-decision-matrix-table",
                                        children=[
                                            html.Div(
                                                "Loading decision matrix...",
                                                className="text-center text-muted p-2 small"
                                            )
                                        ],
                                        style={"maxHeight": "400px", "overflowY": "auto", "padding": "0.5rem"}
                                    )
                                ],
                                className="h-100"
                            )
                        ],
                        width=7
                    ),
                    # Results - Right side (compact)
                    dbc.Col(
                        [
                            # Ranking card
                            dbc.Card(
                                [
                                    dbc.CardHeader(
                                        "Ranking",
                                        className="fw-bold text-white py-2",
                                        style={"backgroundColor": "#1e3a5f", "fontSize": "0.9rem"}
                                    ),
                                    dbc.CardBody(
                                        id="dss-ranking",
                                        style={"padding": "0.5rem", "maxHeight": "200px", "overflowY": "auto"}
                                    )
                                ],
                                className="mb-2"
                            ),
                            # Weighted Scores card
                            dbc.Card(
                                [
                                    dbc.CardHeader(
                                        "Weighted Scores",
                                        className="fw-bold text-white py-2",
                                        style={"backgroundColor": "#1e3a5f", "fontSize": "0.9rem"}
                                    ),
                                    dbc.CardBody(
                                        id="dss-weighted-scores",
                                        style={"padding": "0.5rem", "maxHeight": "180px", "overflowY": "auto"}
                                    )
                                ]
                            )
                        ],
                        width=5
                    )
                ],
                className="mb-3"
            ),
            # Visualization row
            dbc.Row(
                dbc.Col(
                    [
                        dbc.Card(
                            [
                                dbc.CardHeader(
                                    "Weighted Scores Visualization",
                                    className="fw-bold text-white py-2",
                                    style={"backgroundColor": "#1e3a5f", "fontSize": "0.9rem"}
                                ),
                                dbc.CardBody(
                                    [
                                        dcc.Graph(id="dss-sensitivity-chart", config={"displayModeBar": False})
                                    ],
                                    style={"padding": "0.5rem"}
                                )
                            ]
                        )
                    ],
                    width=12
                )
            ),
            dbc.Tooltip(
                "Relative weight for hydrogeologic feasibility scores in the MCDA (0–10)",
                target="weight-hydrogeologic",
                placement="top",
            ),
            dbc.Tooltip(
                "Relative weight for environmental suitability scores",
                target="weight-environmental",
                placement="top",
            ),
            dbc.Tooltip(
                "Relative weight for regulatory / permitting scores",
                target="weight-regulation",
                placement="top",
            ),
            dbc.Tooltip(
                "Relative weight for capital cost effectiveness",
                target="weight-capital-cost",
                placement="top",
            ),
            dbc.Tooltip(
                "Relative weight for maintenance cost effectiveness",
                target="weight-maintenance-cost",
                placement="top",
            ),
            dbc.Tooltip(
                "Relative weight for net present value efficiency",
                target="weight-npv",
                placement="top",
            ),
            dbc.Tooltip(
                "Bar chart of weighted criterion scores for ranked MAR options",
                target="dss-sensitivity-chart",
                placement="top",
            ),
        ],
        style={"padding": "0.5rem"}
    )
