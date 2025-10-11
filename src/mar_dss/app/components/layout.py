"""
Layout setup for the MAR DSS dashboard.

This module provides a function to build and assign the Dash layout using
the provided application context (the main DashboardApp instance).
"""

import dash_bootstrap_components as dbc
from dash import dcc, html


def setup_layout(app_ctx):
    """Set up the main dashboard layout on the given app context.

    The app_ctx is expected to be an instance that provides:
    - app (Dash instance)
    - create_sample_data
    - create_water_level_chart
    - create_recharge_chart
    - create_quality_chart
    - create_summary_cards
    """
    # Sample data
    app_ctx.data = app_ctx.create_sample_data()

    # Create charts
    app_ctx.water_level_chart = app_ctx.create_water_level_chart(app_ctx.data)
    app_ctx.recharge_chart = app_ctx.create_recharge_chart(app_ctx.data)
    app_ctx.quality_chart = app_ctx.create_quality_chart(app_ctx.data)
    app_ctx.summary_cards = app_ctx.create_summary_cards(app_ctx.data)

    # Main layout
    app_ctx.app.layout = html.Div(
        [
            # Dynamic theme CSS link
            html.Link(
                id="theme-css",
                rel="stylesheet",
                href=(
                    "https://cdn.jsdelivr.net/npm/bootswatch@5.3.2/dist/"
                    "cerulean/bootstrap.min.css"
                ),
            ),
            dbc.Container(
                [
                    # Header with Logo and Theme Selector
                    dbc.Row(
                        [
                            dbc.Col(
                                [
                                    html.Div(
                                        [
                                            # Title
                                            html.Div(
                                                [
                                                    # Left-pinned logo
                                                    html.Div(
                                                        [
                                                            html.Img(
                                                                src="assets/logo2.png",
                                                                alt="MAR DSS Logo 2",
                                                                style={
                                                                    "height": "100px",
                                                                    "width": "auto",
                                                                    "vertical-align": "middle",
                                                                },
                                                            )
                                                        ],
                                                        style={
                                                            "position": "absolute",
                                                            "left": "0",
                                                            "top": "50%",
                                                            "transform": "translateY(-50%)",
                                                        },
                                                    ),
                                                    # Centered title across full width
                                                    html.Div(
                                                        [
                                                            html.H1(
                                                                [
                                                                    "Managed Aquifer Recharge",
                                                                    html.Br(),
                                                                    "Decision Support System",
                                                                ],
                                                                className=(
                                                                    "text-center mb-4"
                                                                ),
                                                                style={
                                                                    "font-family": (
                                                                        "'Segoe UI', Tahoma, sans-serif"
                                                                    ),
                                                                    "font-size": "2.75rem",
                                                                    "font-weight": "700",
                                                                    "color": "#2C3E50",
                                                                    "background-color": "transparent",
                                                                    "padding": "0px",
                                                                    "border-radius": "8px",
                                                                    "border": "none",
                                                                    "vertical-align": "middle",
                                                                },
                                                            )
                                                        ],
                                                        style={
                                                            "width": "100%",
                                                            "display": "flex",
                                                            "align-items": "center",
                                                            "justify-content": "center",
                                                        },
                                                    ),
                                                ],
                                                style={
                                                    "position": "relative",
                                                    "min-height": "100px",
                                                    "width": "100%",
                                                },
                                            ),
                                            # Action Icons Row
                                            html.Div(
                                                [
                                                    dbc.ButtonGroup(
                                                        [
                                                            dbc.Button(
                                                                [
                                                                    html.I(
                                                                        className=(
                                                                            "fas fa-folder-open me-1"
                                                                        )
                                                                    ),
                                                                    "Open",
                                                                ],
                                                                id="btn-open",
                                                                color=(
                                                                    "outline-primary"
                                                                ),
                                                                size="sm",
                                                                className="me-1",
                                                                style={
                                                                    "padding": "4px 8px"
                                                                },
                                                            ),
                                                            dbc.Button(
                                                                [
                                                                    html.I(
                                                                        className=(
                                                                            "fas fa-save me-1"
                                                                        )
                                                                    ),
                                                                    "Save",
                                                                ],
                                                                id="btn-save",
                                                                color=(
                                                                    "outline-success"
                                                                ),
                                                                size="sm",
                                                                className="me-1",
                                                                style={
                                                                    "padding": "4px 8px"
                                                                },
                                                            ),
                                                            dbc.Button(
                                                                [
                                                                    html.I(
                                                                        className=(
                                                                            "fas fa-plus me-1"
                                                                        )
                                                                    ),
                                                                    "New",
                                                                ],
                                                                id="btn-new",
                                                                color="outline-info",
                                                                size="sm",
                                                                style={
                                                                    "padding": "4px 8px"
                                                                },
                                                            ),
                                                        ],
                                                        className="mb-2",
                                                    )
                                                ],
                                                style={"margin-top": "5px"},
                                            ),
                                            # Theme Selector and Logo Row
                                            html.Div(
                                                [
                                                    html.Div(
                                                        [
                                                            html.Label(
                                                                "Theme",
                                                                className=(
                                                                    "small text-muted"
                                                                ),
                                                            ),
                                                            dbc.Select(
                                                                id="theme-selector",
                                                                options=[
                                                                    {
                                                                        "label": "Cerulean",
                                                                        "value": "CERULEAN",
                                                                    },
                                                                    {
                                                                        "label": "Darkly",
                                                                        "value": "DARKLY",
                                                                    },
                                                                    {
                                                                        "label": "Flatly",
                                                                        "value": "FLATLY",
                                                                    },
                                                                    {
                                                                        "label": "Cyborg",
                                                                        "value": "CYBORG",
                                                                    },
                                                                    {
                                                                        "label": "Slate",
                                                                        "value": "SLATE",
                                                                    },
                                                                ],
                                                                value="CERULEAN",
                                                                size="sm",
                                                                style={
                                                                    "width": "120px"
                                                                },
                                                            ),
                                                        ],
                                                        style={
                                                            "display": "inline-block",
                                                            "margin-right": "20px",
                                                        },
                                                    ),
                                                    html.Img(
                                                        src="assets/logo.jpg",
                                                        alt="MAR DSS Logo",
                                                        style={
                                                            "height": "160px",
                                                            "width": "auto",
                                                            "max-width": "300px",
                                                            "vertical-align": "middle",
                                                        },
                                                    ),
                                                ],
                                                className="position-absolute",
                                                style={
                                                    "top": "10px",
                                                    "right": "20px",
                                                },
                                            ),
                                        ],
                                        className="position-relative",
                                    ),
                                    html.Hr(),
                                ]
                            )
                        ]
                    ),
                    # Main Content Area with Tabs and Sidebar
                    dbc.Row(
                        [
                            # Left Content Area with Tabs
                            dbc.Col(
                                [
                                    dbc.Card(
                                        [
                                            dbc.CardHeader(
                                                [
                                                    dbc.Tabs(
                                                        [
                                                            dbc.Tab(
                                                                label="(1) Overview",
                                                                tab_id="overview",
                                                            ),
                                                            dbc.Tab(
                                                                label=(
                                                                    "(2) Water Source"
                                                                ),
                                                                tab_id="analysis",
                                                            ),
                                                            dbc.Tab(
                                                                label=(
                                                                    "(3) Hydrogeology"
                                                                ),
                                                                tab_id="settings",
                                                            ),
                                                            dbc.Tab(
                                                                label=(
                                                                    "(4) Environmental Impact"
                                                                ),
                                                                tab_id="environmental",
                                                            ),
                                                            dbc.Tab(
                                                                label=(
                                                                    "(5) Legal Constraints"
                                                                ),
                                                                tab_id="legal",
                                                            ),
                                                            dbc.Tab(
                                                                label="(6) Reports",
                                                                tab_id="reports",
                                                            ),
                                                        ],
                                                        id="top-tabs",
                                                        active_tab="overview",
                                                    )
                                                ]
                                            ),
                                            dbc.CardBody(
                                                [
                                                    # Main Content Area - switches based on navigation
                                                    html.Div(
                                                        id="main-content",
                                                        children=[
                                                            # Default content (overview)
                                                            dbc.Row(
                                                                [
                                                                    dbc.Col(
                                                                        card,
                                                                        width=4,
                                                                    )
                                                                    for card in (
                                                                        app_ctx.summary_cards
                                                                    )
                                                                ],
                                                                className="mb-4",
                                                            ),
                                                            dbc.Row(
                                                                [
                                                                    dbc.Col(
                                                                        [
                                                                            dcc.Graph(
                                                                                figure=(
                                                                                    app_ctx.water_level_chart
                                                                                )
                                                                            )
                                                                        ],
                                                                        width=6,
                                                                    ),
                                                                    dbc.Col(
                                                                        [
                                                                            dcc.Graph(
                                                                                figure=(
                                                                                    app_ctx.recharge_chart
                                                                                )
                                                                            )
                                                                        ],
                                                                        width=6,
                                                                    ),
                                                                ]
                                                            ),
                                                            dbc.Row(
                                                                [
                                                                    dbc.Col(
                                                                        [
                                                                            dcc.Graph(
                                                                                figure=(
                                                                                    app_ctx.quality_chart
                                                                                )
                                                                            )
                                                                        ],
                                                                        width=12,
                                                                    )
                                                                ],
                                                                className="mt-4",
                                                            ),
                                                        ],
                                                    )
                                                ]
                                            ),
                                        ]
                                    )
                                ],
                                width=9,
                                style={
                                    "flex": "0 0 80%",
                                    "maxWidth": "80%",
                                },
                            ),
                            # Right Sidebar (Analysis)
                            dbc.Col(
                                [
                                    dbc.Card(
                                        [
                                            dbc.CardHeader(
                                                "Analysis",
                                                className="fw-bold",
                                            ),
                                            dbc.CardBody(
                                                [
                                                    dbc.Nav(
                                                        [
                                                            dbc.NavItem(
                                                                [
                                                                    dbc.NavLink(
                                                                        "Dashboard",
                                                                        id=(
                                                                            "nav-dashboard"
                                                                        ),
                                                                        href="#",
                                                                        active=True,
                                                                    )
                                                                ]
                                                            ),
                                                            dbc.NavItem(
                                                                [
                                                                    dbc.NavLink(
                                                                        "DSS Algorithm",
                                                                        id=(
                                                                            "nav-water-levels"
                                                                        ),
                                                                        href="#",
                                                                    )
                                                                ]
                                                            ),
                                                            dbc.NavItem(
                                                                [
                                                                    dbc.NavLink(
                                                                        "Decision Sensitivity",
                                                                        id=(
                                                                            "nav-recharge"
                                                                        ),
                                                                        href="#",
                                                                    )
                                                                ]
                                                            ),
                                                            dbc.NavItem(
                                                                [
                                                                    dbc.NavLink(
                                                                        "Decision Interpretation",
                                                                        id=(
                                                                            "nav-quality"
                                                                        ),
                                                                        href="#",
                                                                    )
                                                                ]
                                                            ),
                                                            dbc.NavItem(
                                                                [
                                                                    dbc.NavLink(
                                                                        "Scenarios Comparison",
                                                                        id=(
                                                                            "nav-scenarios"
                                                                        ),
                                                                        href="#",
                                                                    )
                                                                ]
                                                            ),
                                                            dbc.NavItem(
                                                                [
                                                                    dbc.NavLink(
                                                                        "AI Generated Decision",
                                                                        id=(
                                                                            "nav-ai-decision"
                                                                        ),
                                                                        href="#",
                                                                    )
                                                                ]
                                                            ),
                                                            dbc.NavItem(
                                                                [
                                                                    dbc.NavLink(
                                                                        "Data Export",
                                                                        id=(
                                                                            "nav-export"
                                                                        ),
                                                                        href="#",
                                                                    )
                                                                ]
                                                            ),
                                                        ],
                                                        vertical=True,
                                                        pills=True,
                                                    )
                                                ]
                                            ),
                                        ]
                                    )
                                ],
                                width=3,
                                style={
                                    "flex": "0 0 20%",
                                    "maxWidth": "20%",
                                },
                            ),
                        ]
                    ),
                ],
                fluid=True,
                id="app-container",
            ),
            # Global data store for stratigraphy layers
            dcc.Store(
                id="stratigraphy-data-store", data=[], storage_type="memory"
            ),
        ]
    )


