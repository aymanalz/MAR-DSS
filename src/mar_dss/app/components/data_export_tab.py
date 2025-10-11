"""
Data Export tab content for MAR DSS dashboard.
"""

import dash_bootstrap_components as dbc
from dash import html


def create_data_export_content():
    """Create content for Data Export sidebar tab."""
    return html.Div(
        [
            html.H3("Data Export"),
            html.P("Export analysis results and data."),
            dbc.Card(
                [
                    dbc.CardBody(
                        [
                            html.H5("Export Options"),
                            dbc.Row(
                                [
                                    dbc.Col(
                                        [
                                            dbc.Button(
                                                "Export CSV",
                                                color="primary",
                                                className="mb-2",
                                            ),
                                            dbc.Button(
                                                "Export Excel",
                                                color="success",
                                                className="mb-2",
                                            ),
                                            dbc.Button(
                                                "Export PDF",
                                                color="warning",
                                                className="mb-2",
                                            ),
                                        ],
                                        width=6,
                                    ),
                                    dbc.Col(
                                        [
                                            html.P("Select data range:"),
                                            dbc.Select(
                                                options=[
                                                    {
                                                        "label": "Last 7 days",
                                                        "value": "7days",
                                                    },
                                                    {
                                                        "label": "Last 30 days",
                                                        "value": "30days",
                                                    },
                                                    {
                                                        "label": "Last 90 days",
                                                        "value": "90days",
                                                    },
                                                    {
                                                        "label": "All data",
                                                        "value": "all",
                                                    },
                                                ],
                                                value="30days",
                                            ),
                                        ],
                                        width=6,
                                    ),
                                ]
                            ),
                        ]
                    )
                ]
            ),
        ]
    )


