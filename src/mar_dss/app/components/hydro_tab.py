"""
Hydrogeology tab content for MAR DSS dashboard.
"""

import dash_bootstrap_components as dbc
from dash import dcc, html


def create_hydro_tab_content():
    """Create the content for the Hydrogeology tab."""
    return [
        *_build_hydro_tab_header(),
        _build_geometry_and_view_cards(),
    ]


def _build_hydro_tab_header():
    """Build the hydrogeology tab header."""
    return [
        html.H3("Hydrogeology"),
        html.P(
            "Configure hydrogeological parameters for MAR project analysis."
        ),
    ]


def _build_aquifer_type_selector():
    """Build the aquifer type radio button selector."""
    return html.Div(
        [
            html.Label("Aquifer Type:", className="fw-bold mb-2"),
            dbc.RadioItems(
                id="aquifer-type-radio",
                options=[
                    {"label": "Unconfined", "value": "unconfined"},
                    {"label": "Confined", "value": "confined"},
                    {"label": "Semi-Confined", "value": "semi-confined"},
                ],
                value="unconfined",
                inline=True,
                className="mb-3"
            )
        ],
        className="mb-3"
    )


def _build_stratigraphy_table_header():
    """Build the stratigraphy table header."""
    return html.Thead(
        html.Tr(
            [
                html.Th("Parameter", className="fw-bold text-white", style={"background-color": "#2c3e50"}),
                html.Th("Depth/Thickness (ft)", className="fw-bold text-white", style={"background-color": "#2c3e50"}),
                html.Th("Hydraulic Conductivity", className="fw-bold text-white", style={"background-color": "#2c3e50"}),
                html.Th("Storage Term", className="fw-bold text-white", style={"background-color": "#2c3e50"}),
            ]
        )
    )


def _build_stratigraphy_table_row(parameter, depth_id, conductivity_id, storage_id, bg_color, text_color=None):
    """Build a single row for the stratigraphy table."""
    style = {"background-color": bg_color}
    if text_color:
        style["color"] = text_color
    
    return html.Tr(
        [
            html.Td(parameter, className="fw-bold", style=style),
            html.Td(
                dbc.Input(
                    id=depth_id,
                    type="number",
                    placeholder="0.0",
                    size="sm",
                    className="border-0"
                ),
                style=style
            ),
            html.Td(
                dbc.Input(
                    id=conductivity_id,
                    type="number",
                    placeholder="0.0",
                    size="sm",
                    className="border-0"
                ),
                style=style
            ),
            html.Td(
                dbc.Input(
                    id=storage_id,
                    type="number",
                    placeholder="0.0",
                    size="sm",
                    className="border-0"
                ),
                style=style
            ),
        ],
        style=style
    )


def _build_stratigraphy_table_body():
    """Build the stratigraphy table body with all rows."""
    return html.Tbody(
        [
            _build_stratigraphy_table_row(
                "Ground Surface Elevation",
                "ground-surface-depth",
                "ground-surface-conductivity",
                "ground-surface-storage",
                "#ecf0f1"
            ),
            _build_stratigraphy_table_row(
                "Top of MAR Storage Zone",
                "mar-storage-depth",
                "mar-storage-conductivity",
                "mar-storage-storage",
                "#d5dbdb"
            ),
            _build_stratigraphy_table_row(
                "Max. Groundwater Table Elevation",
                "max-gw-depth",
                "max-gw-conductivity",
                "max-gw-storage",
                "#ecf0f1"
            ),
            _build_stratigraphy_table_row(
                "Average Groundwater Table Elevation",
                "avg-gw-depth",
                "avg-gw-conductivity",
                "avg-gw-storage",
                "#d5dbdb"
            ),
            _build_stratigraphy_table_row(
                "Min Groundwater Table Elevation",
                "min-gw-depth",
                "min-gw-conductivity",
                "min-gw-storage",
                "#ecf0f1"
            ),
            _build_stratigraphy_table_row(
                "Bedrock Depth",
                "bedrock-depth",
                "bedrock-conductivity",
                "bedrock-storage",
                "#a9a9a9",
                "white"
            ),
        ]
    )


def _build_stratigraphy_table():
    """Build the complete stratigraphy table."""
    return dbc.Table(
        [
            _build_stratigraphy_table_header(),
            _build_stratigraphy_table_body()
        ],
        striped=True,
        bordered=True,
        hover=True,
        responsive=True,
        className="mb-3"
    )


def _build_stratigraphy_tab():
    """Build the stratigraphy tab content."""
    return dbc.Tab(
        label="Stratigraphy",
        tab_id="stratigraphy-tab",
        children=[
            html.Div(
                [_build_stratigraphy_table()],
                id="stratigraphy-content"
            )
        ]
    )


def _build_horizontal_extension_tab():
    """Build the horizontal extension tab content."""
    return dbc.Tab(
        label="Horizontal Extension",
        tab_id="horizontal-extension-tab",
        children=[
            html.Div(
                [
                    html.P(
                        "Horizontal extension configuration will be added here.",
                        className="text-muted text-center mt-3"
                    )
                ],
                id="horizontal-extension-content"
            )
        ]
    )


def _build_geometry_tabs():
    """Build the geometry tabs container."""
    return dbc.Tabs(
        id="geometry-tabs",
        children=[
            _build_stratigraphy_tab(),
            _build_horizontal_extension_tab(),
        ],
        active_tab="stratigraphy-tab"
    )


def _build_geometry_card():
    """Build the Geometry card."""
    return dbc.Card(
        [
            dbc.CardHeader(
                "Geometry",
                className="fw-bold bg-primary text-white",
            ),
            dbc.CardBody(
                [
                    _build_aquifer_type_selector(),
                    _build_geometry_tabs(),
                ]
            ),
        ],
        className="mb-4",
    )


def _build_view_card():
    """Build the View card."""
    return dbc.Card(
        [
            dbc.CardHeader(
                "View",
                className="fw-bold bg-secondary text-white",
            ),
            dbc.CardBody(
                [
                    html.P(
                        "View options will be added here.",
                        className="text-muted text-center"
                    )
                ]
            ),
        ],
        className="mb-4",
    )


def _build_geometry_and_view_cards():
    """Build the Geometry and View cards side by side."""
    return dbc.Row(
        [
            dbc.Col(_build_geometry_card(), width=6),
            dbc.Col(_build_view_card(), width=6),
        ]
    )