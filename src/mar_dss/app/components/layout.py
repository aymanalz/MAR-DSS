"""
Layout setup for the MAR DSS dashboard.

This module provides a function to build and assign the Dash layout using
the provided application context (the main DashboardApp instance).
"""

import dash_bootstrap_components as dbc
from dash import dcc, html
from mar_dss.app.utils.defaults import defaults
import mar_dss.app.utils.data_storage as dash_storage


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
    _create_initial_data(app_ctx)
    _create_charts(app_ctx)
    app_ctx.app.layout = _build_root_layout(app_ctx)


# ------------------------------
# Theme helpers
# ------------------------------

_THEME_URLS = {
    "CERULEAN": (
        "https://cdn.jsdelivr.net/npm/bootswatch@5.3.2/dist/"
        "cerulean/bootstrap.min.css"
    ),
    "DARKLY": (
        "https://cdn.jsdelivr.net/npm/bootswatch@5.3.2/dist/"
        "darkly/bootstrap.min.css"
    ),
    "FLATLY": (
        "https://cdn.jsdelivr.net/npm/bootswatch@5.3.2/dist/"
        "flatly/bootstrap.min.css"
    ),
    "CYBORG": (
        "https://cdn.jsdelivr.net/npm/bootswatch@5.3.2/dist/"
        "cyborg/bootstrap.min.css"
    ),
    "SLATE": (
        "https://cdn.jsdelivr.net/npm/bootswatch@5.3.2/dist/"
        "slate/bootstrap.min.css"
    ),
}


def _get_theme_url(theme_name: str) -> str:
    return _THEME_URLS.get(theme_name.upper(), _THEME_URLS["CERULEAN"])


def _create_theme_link(initial_theme: str = "CERULEAN") -> html.Link:
    return html.Link(
        id="theme-css",
        rel="stylesheet",
        href=_get_theme_url(initial_theme),
    )


# ------------------------------
# Data and charts
# ------------------------------

def _create_initial_data(app_ctx) -> None:
    app_ctx.data = app_ctx.create_sample_data()


def _create_charts(app_ctx) -> None:
    app_ctx.water_level_chart = app_ctx.create_water_level_chart(app_ctx.data)
    app_ctx.recharge_chart = app_ctx.create_recharge_chart(app_ctx.data)
    app_ctx.quality_chart = app_ctx.create_quality_chart(app_ctx.data)
    app_ctx.summary_cards = app_ctx.create_summary_cards(app_ctx.data)


# ------------------------------
# Header builders
# ------------------------------

def _build_title_block() -> html.Div:
    return html.Div(
        [
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
            html.Div(
                [
                    html.H1(
                        [
                            "Managed Aquifer Recharge",
                            html.Br(),
                            "Decision Support System",
                        ],
                        className=("text-center mb-4"),
                        style={
                            "font-family": ("'Segoe UI', Tahoma, sans-serif"),
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
    )


def _build_action_buttons() -> dbc.ButtonGroup:
    return dbc.ButtonGroup(
        [
            dbc.Button(
                [html.I(className=("fas fa-save me-1")), "Save"],
                id="btn-save",
                color=("outline-success"),
                size="sm",
                className="me-1",
                style={"padding": "4px 8px"},
            ),
            dbc.Button(
                [html.I(className=("fas fa-plus me-1")), "New"],
                id="btn-new",
                color="outline-info",
                size="sm",
                style={"padding": "4px 8px"},
            ),
        ],
        className="mb-2",
    )


def _build_theme_selector_and_logo() -> html.Div:
    return html.Div(
        [
            html.Div(
                [
                    html.Label("Theme", className=("small text-muted")),
                    dbc.Select(
                        id="theme-selector",
                        options=[
                            {"label": "Cerulean", "value": "CERULEAN"},
                            {"label": "Darkly", "value": "DARKLY"},
                            {"label": "Flatly", "value": "FLATLY"},
                            {"label": "Cyborg", "value": "CYBORG"},
                            {"label": "Slate", "value": "SLATE"},
                        ],
                        value="CERULEAN",
                        size="sm",
                        style={"width": "120px"},
                    ),
                ],
                style={"display": "inline-block", "margin-right": "20px"},
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
        style={"top": "10px", "right": "20px"},
    )


def _build_header() -> dbc.Row:
    return dbc.Row(
        [
            dbc.Col(
                [
                    html.Div(
                        [_build_title_block(), _build_action_buttons(),
                         _build_theme_selector_and_logo()],
                        className="position-relative",
                    ),
                    html.Hr(),
                ]
            )
        ]
    )


# ------------------------------
# Main content builders
# ------------------------------

def _build_tabs() -> dbc.Tabs:
    return dbc.Tabs(
        [
            dbc.Tab(
                label="(1) Overview", 
                tab_id="overview",
                label_style={
                    "color": "#ffffff", 
                    "fontWeight": "bold",
                    "backgroundColor": "#6f42c1",
                    "border": "1px solid #6f42c1"
                },
                active_label_style={
                    "color": "#ffffff", 
                    "backgroundColor": "#5a32a3",
                    "border": "1px solid #5a32a3"
                }
            ),
            dbc.Tab(
                label=("(2) Water Source"), 
                tab_id="water-source",
                label_style={
                    "color": "#ffffff", 
                    "fontWeight": "bold",
                    "backgroundColor": "#8e44ad",
                    "border": "1px solid #8e44ad"
                },
                active_label_style={
                    "color": "#ffffff", 
                    "backgroundColor": "#7d3c98",
                    "border": "1px solid #7d3c98"
                }
            ),
            dbc.Tab(
                label=("(3) Hydrogeology"), 
                tab_id="hydrogeology",
                label_style={
                    "color": "#ffffff", 
                    "fontWeight": "bold",
                    "backgroundColor": "#a569bd",
                    "border": "1px solid #a569bd"
                },
                active_label_style={
                    "color": "#ffffff", 
                    "backgroundColor": "#9b59b6",
                    "border": "1px solid #9b59b6"
                }
            ),
            dbc.Tab(
                label=("(4) Environmental Impact"), 
                tab_id="environmental",
                label_style={
                    "color": "#ffffff", 
                    "fontWeight": "bold",
                    "backgroundColor": "#3498db",
                    "border": "1px solid #3498db"
                },
                active_label_style={
                    "color": "#ffffff", 
                    "backgroundColor": "#2980b9",
                    "border": "1px solid #2980b9"
                }
            ),
            dbc.Tab(
                label=("(5) Legal Constraints"), 
                tab_id="legal",
                label_style={
                    "color": "#ffffff", 
                    "fontWeight": "bold",
                    "backgroundColor": "#5dade2",
                    "border": "1px solid #5dade2"
                },
                active_label_style={
                    "color": "#ffffff", 
                    "backgroundColor": "#4a9fd1",
                    "border": "1px solid #4a9fd1"
                }
            ),
            dbc.Tab(
                label="(6) Analysis", 
                tab_id="analysis",
                label_style={
                    "color": "#ffffff", 
                    "fontWeight": "bold",
                    "backgroundColor": "#85c1e9",
                    "border": "1px solid #85c1e9"
                },
                active_label_style={
                    "color": "#ffffff", 
                    "backgroundColor": "#73b3e0",
                    "border": "1px solid #73b3e0"
                }
            ),
            dbc.Tab(
                label="(7) Reports", 
                tab_id="reports",
                label_style={
                    "color": "#ffffff", 
                    "fontWeight": "bold",
                    "backgroundColor": "#aed6f1",
                    "border": "1px solid #aed6f1"
                },
                active_label_style={
                    "color": "#ffffff", 
                    "backgroundColor": "#9bc7e8",
                    "border": "1px solid #9bc7e8"
                }
            ),
        ],
        id="top-tabs",
        active_tab="overview",
    )


def _build_overview_content(app_ctx) -> list:
    return [
        # Main Content Area - switches based on navigation
        html.Div(
            id="main-content",
            children=[
                # Default content (overview)
                dbc.Row(
                    [
                        dbc.Col(card, width=4)
                        for card in (app_ctx.summary_cards)
                    ],
                    className="mb-4",
                ),
                dbc.Row(
                    [
                        dbc.Col(
                            [dcc.Graph(figure=(app_ctx.water_level_chart))],
                            width=6,
                        ),
                        dbc.Col(
                            [dcc.Graph(figure=(app_ctx.recharge_chart))],
                            width=6,
                        ),
                    ]
                ),
                dbc.Row(
                    [
                        dbc.Col(
                            [dcc.Graph(figure=(app_ctx.quality_chart))],
                            width=12,
                        )
                    ],
                    className="mt-4",
                ),
            ],
        )
    ]


def _build_main_card(app_ctx) -> dbc.Card:
    return dbc.Card([
        dbc.CardHeader([_build_tabs()]),
        dbc.CardBody(_build_overview_content(app_ctx)),
    ])


# ------------------------------
# Sidebar builders
# ------------------------------

def _build_sidebar_nav() -> dbc.Nav:
    return dbc.Nav(
        [
            dbc.NavItem([
                dbc.NavLink("Dashboard", id=("nav-dashboard"), href="#",
                            active=True)
            ]),
            dbc.NavItem([
                dbc.NavLink("DSS Algorithm", id=("nav-water-levels"),
                            href="#")
            ]),
            dbc.NavItem([
                dbc.NavLink("Decision Sensitivity", id=("nav-recharge"),
                            href="#")
            ]),
            dbc.NavItem([
                dbc.NavLink("Decision Interpretation", id=("nav-quality"),
                            href="#")
            ]),
            dbc.NavItem([
                dbc.NavLink("Scenarios Comparison", id=("nav-scenarios"),
                            href="#")
            ]),
            dbc.NavItem([
                dbc.NavLink("AI Generated Decision", id=("nav-ai-decision"),
                            href="#")
            ]),
            dbc.NavItem([
                dbc.NavLink("Data Export", id=("nav-export"), href="#")
            ]),
        ],
        vertical=True,
        pills=True,
    )


def _build_sidebar() -> dbc.Col:
    return dbc.Col(
        [
            dbc.Card(
                [
                    dbc.CardHeader("Analysis", className="fw-bold"),
                    dbc.CardBody([_build_sidebar_nav()]),
                ]
            )
        ],
        width=3,
        style={"flex": "0 0 20%", "maxWidth": "20%"},
    )


# ------------------------------
# Page layout builders
# ------------------------------

def _build_content_area(app_ctx) -> dbc.Row:
    return dbc.Row(
        [
            dbc.Col(
                [_build_main_card(app_ctx)],
                width=12,  # Full width since sidebar is removed
            ),
        ]
    )


def _build_root_layout(app_ctx) -> html.Div:
    return html.Div(
        [
            _create_theme_link("CERULEAN"),
            dbc.Container(
                [
                    _build_header(),
                    _build_content_area(app_ctx),
                ],
                fluid=True,
                id="app-container",
            ),
            dcc.Store(
                id="stratigraphy-data-store", data=[], storage_type="memory"
            ),
        ]
    )


