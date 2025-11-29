"""
Engineering Options tab component.
"""

import dash_bootstrap_components as dbc
from dash import html


def create_engineering_options_content():
    """Create the Engineering Options tab content."""
    return [
        dbc.Row(
            [
                dbc.Col(
                    [
                        dbc.Card(
                            [
                                dbc.CardBody(
                                    [
                                        html.H4("Row 1"),
                                        html.P("Content for row 1"),
                                    ]
                                ),
                            ],
                            className="mb-4",
                        ),
                        dbc.Card(
                            [
                                dbc.CardBody(
                                    [
                                        html.H4("Row 2"),
                                        html.P("Content for row 2"),
                                    ]
                                ),
                            ],
                            className="mb-4",
                        ),
                        dbc.Card(
                            [
                                dbc.CardBody(
                                    [
                                        html.H4("Row 3"),
                                        html.P("Content for row 3"),
                                    ]
                                ),
                            ],
                            className="mb-4",
                        ),
                        dbc.Card(
                            [
                                dbc.CardBody(
                                    [
                                        html.H4("Row 4"),
                                        html.P("Content for row 4"),
                                    ]
                                ),
                            ],
                            className="mb-4",
                        ),
                    ],
                    width=8,
                ),
                dbc.Col(
                    [
                        dbc.Card(
                            [
                                dbc.CardBody(
                                    [
                                        html.Img(
                                            src="assets/Engineering.jpg",
                                            alt="Engineering",
                                            style={
                                                "width": "100%",
                                                "height": "auto",
                                                "display": "block"
                                            }
                                        ),
                                    ]
                                ),
                            ],
                            className="mb-4",
                            style={
                                "height": "100%",
                                "display": "flex",
                                "flex-direction": "column"
                            }
                        )
                    ],
                    width=4,
                ),
            ],
            className="mb-4",
        )
    ]

