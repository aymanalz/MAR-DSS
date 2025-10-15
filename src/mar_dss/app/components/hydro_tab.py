"""
Hydrogeology tab content for MAR DSS dashboard.
"""

import dash_bootstrap_components as dbc
from dash import dcc, html
import pandas as pd

columns=["parameter", "Depth/Thickness (ft)", "Hydraulic Conductivity", "Storage Term"]
default_stratigraphy_unconfined = pd.DataFrame(columns=columns)
parameters = ["Depth of No MAR Storage Zone", "MAR Storage Zone", "Max. Groundwater Table Elevation", "Average Groundwater Table Elevation", "Min Groundwater Table Elevation", "Bedrock Depth"]


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
                [
                    html.H5("Stratigraphy Configuration", className="mb-3"),
                    html.P("Configure soil layers and their hydrogeological properties.", className="mb-4"),
                    
                    # Table controls
                    dbc.Row([
                        dbc.Col([
                            dbc.ButtonGroup([
                                dbc.Button("Add Layer", id="add-layer-btn", color="success", size="sm"),
                                dbc.Button("Delete Selected", id="delete-layer-btn", color="danger", size="sm"),
                                dbc.Button("Move Up", id="move-up-btn", color="info", size="sm"),
                                dbc.Button("Move Down", id="move-down-btn", color="info", size="sm"),
                            ])
                        ], width=8),
                        dbc.Col([
                            html.Small("Select rows to delete or move", className="text-muted")
                        ], width=4)
                    ], className="mb-3"),
                    
                    # Stratigraphy table
                    dbc.Table(
                        [
                            html.Thead([
                                html.Tr([
                                    html.Th("Select", style={"width": "5%"}),
                                    html.Th("Layer", style={"width": "20%"}),
                                    html.Th("Thickness (ft)", style={"width": "15%"}),
                                    html.Th("Hydraulic Conductivity (ft/day)", style={"width": "20%"}),
                                    html.Th("Specific Storage (1/ft)", style={"width": "20%"}),
                                    html.Th("Specific Yield", style={"width": "20%"})
                                ])
                            ]),
                            html.Tbody(id="stratigraphy-table-body")
                        ],
                        striped=True,
                        bordered=True,
                        hover=True,
                        responsive=True,
                        className="mb-3"
                    ),
                    
                    # Store for table data
                    dcc.Store(id="stratigraphy-data-store", data=[
                        {"layer": "Sand", "thickness": 60.0, "conductivity": 10.0, "storage": 0.0001, "yield": 0.25, "selected": False},
                        {"layer": "Silt", "thickness": 60.0, "conductivity": 0.01, "storage": 0.0001, "yield": 0.10, "selected": False},
                        {"layer": "Gravel", "thickness": 60.0, "conductivity": 100.0, "storage": 0.0001, "yield": 0.30, "selected": False}
                    ])
                ],
                id="stratigraphy-content"
            )
        ]
    )


def _build_groundwater_level_tab():
    """Build the groundwater level tab content."""
    return dbc.Tab(
        label="Groundwater Level",
        tab_id="groundwater-level-tab",
        children=[
            html.Div(
                [
                    html.H5("Groundwater Level Configuration", className="mb-3"),
                    html.P("Configure monthly groundwater level variations.", className="mb-4"),
                    
                    # Table controls
                    dbc.Row([
                        dbc.Col([
                            dbc.ButtonGroup([
                                dbc.Button("Add Month", id="add-month-btn", color="success", size="sm"),
                                dbc.Button("Delete Selected", id="delete-month-btn", color="danger", size="sm"),
                                dbc.Button("Reset to Default", id="reset-gw-btn", color="info", size="sm"),
                            ])
                        ], width=8),
                        dbc.Col([
                            html.Small("Select rows to delete", className="text-muted")
                        ], width=4)
                    ], className="mb-3"),
                    
                    # Table and plot side by side
                    dbc.Row([
                        dbc.Col([
                            # Groundwater level table
                            dbc.Table(
                                [
                                    html.Thead([
                                        html.Tr([
                                            html.Th("Select", style={"width": "15%"}),
                                            html.Th("Month", style={"width": "35%"}),
                                            html.Th("Elevation (ft)", style={"width": "50%"})
                                        ])
                                    ]),
                                    html.Tbody(id="groundwater-table-body")
                                ],
                                striped=True,
                                bordered=True,
                                hover=True,
                                responsive=True,
                                className="mb-3"
                            )
                        ], width=6),
                        dbc.Col([
                            # Input fields for elevation and storage depth
                            dbc.Row([
                                dbc.Col([
                                    html.Label("Ground Surface Elevation (ft):", className="fw-bold"),
                                    dbc.Input(
                                        id="ground-surface-elevation",
                                        type="number",
                                        value=120.0,
                                        step=0.1,
                                        placeholder="Enter elevation"
                                    )
                                ], width=6),
                                dbc.Col([
                                    html.Label("Maximum MAR Storage Depth (ft):", className="fw-bold"),
                                    dbc.Input(
                                        id="max-mar-storage-depth",
                                        type="number",
                                        value=20.0,
                                        step=0.1,
                                        placeholder="Enter storage depth"
                                    )
                                ], width=6)
                            ], className="mb-3"),
                            
                            # Groundwater level plot
                            dcc.Graph(
                                id="groundwater-plot",
                                style={'height': '400px'}
                            )
                        ], width=6)
                    ], className="mb-3"),
                    
                    # Store for groundwater data
                    dcc.Store(id="groundwater-data-store", data=[
                        {"month": "January", "elevation": 75.0, "selected": False},
                        {"month": "February", "elevation": 72.0, "selected": False},
                        {"month": "March", "elevation": 78.0, "selected": False},
                        {"month": "April", "elevation": 82.0, "selected": False},
                        {"month": "May", "elevation": 85.0, "selected": False},
                        {"month": "June", "elevation": 88.0, "selected": False},
                        {"month": "July", "elevation": 90.0, "selected": False},
                        {"month": "August", "elevation": 89.0, "selected": False},
                        {"month": "September", "elevation": 86.0, "selected": False},
                        {"month": "October", "elevation": 83.0, "selected": False},
                        {"month": "November", "elevation": 79.0, "selected": False},
                        {"month": "December", "elevation": 76.0, "selected": False}
                    ])
                ],
                id="groundwater-level-content"
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
            _build_groundwater_level_tab(),
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