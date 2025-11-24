"""
Hydrogeology tab content for MAR DSS dashboard.
"""

import dash_bootstrap_components as dbc
from dash import dcc, html
import pandas as pd
import mar_dss.app.utils.data_storage as dash_storage

columns=["parameter", "Depth/Thickness (ft)", "Hydraulic Conductivity", "Storage Term"]
default_stratigraphy_unconfined = pd.DataFrame(columns=columns)
parameters = ["Depth of No MAR Storage Zone", "MAR Storage Zone", "Max. Groundwater Table Elevation", "Average Groundwater Table Elevation", "Min Groundwater Table Elevation", "Bedrock Depth"]


def _get_stratigraphy_data():
    """Get stratigraphy data from dash_storage or return defaults."""
    stored_data = dash_storage.get_data("stratigraphy_data")
    if stored_data:
        return stored_data
    return [
        {"layer": "Sand", "thickness": 60.0, "conductivity": 10.0, "storage": 0.0001, "yield": 0.25, "selected": False},
        {"layer": "Silt", "thickness": 60.0, "conductivity": 0.01, "storage": 0.0001, "yield": 0.10, "selected": False},
        {"layer": "Gravel", "thickness": 60.0, "conductivity": 100.0, "storage": 0.0001, "yield": 0.30, "selected": False}
    ]


def _get_groundwater_data():
    """Get groundwater data from dash_storage or return defaults."""
    stored_data = dash_storage.get_data("groundwater_data")
    if stored_data:
        return stored_data
    return [
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
    ]


def create_hydrogeologic_settings_content():
    """Create the content for the Hydrogeologic Settings sub-tab (3.1)."""
    return [
        *_build_hydro_tab_header(),
        _build_geometry_and_view_cards(),
    ]


def create_hydrogeologic_feasibility_content():
    """Create the content for the Hydrogeologic Feasibility sub-tab (3.2)."""
    return [
        html.H3("Hydrogeologic Feasibility"),
        html.P(
            "Assess the feasibility of MAR implementation based on hydrogeologic conditions.",
            className="mb-4"
        ),
        dbc.Alert(
            "This section will contain feasibility assessment tools and analysis.",
            color="info"
        ),
    ]


def create_hydro_tab_content():
    """Create the content for the Hydrogeology tab with sub-tabs."""
    return [
        dbc.Tabs([
            dbc.Tab(
                label="(3.1) Hydrogeologic Settings",
                tab_id="hydrogeologic-settings-tab",
                children=create_hydrogeologic_settings_content()
            ),
            dbc.Tab(
                label="(3.2) Hydrogeologic Feasibility",
                tab_id="hydrogeologic-feasibility-tab",
                children=create_hydrogeologic_feasibility_content()
            )
        ], id="hydrogeology-subtabs", active_tab="hydrogeologic-settings-tab")
    ]


def _build_hydro_tab_header():
    """Build the hydrogeology tab header."""
    # Get existing values from data storage if available
    aquifer_type = dash_storage.get_data("aquifer_type") or "unconfined"
    max_allowed_head = dash_storage.get_data("max_allowed_head")
    # Ensure max_allowed_head is a float, default to 1.0
    if max_allowed_head is not None:
        try:
            max_allowed_head = float(max_allowed_head)
        except (ValueError, TypeError):
            max_allowed_head = 1.0
    else:
        max_allowed_head = 1.0
    
    return [
        html.H3("Hydrogeology"),
        html.P(
            "Configure hydrogeological parameters for MAR project analysis."
        ),
        _build_aquifer_type_selector(aquifer_type),
        html.Div(
            id="confined-head-input-container",
            style={"display": "none"},
            children=[
                html.Label("Maximum Allowed Head (Pressure) (ft/foot of depth to the top of the confining layer):", className="fw-bold mb-2"),
                dbc.Input(
                    id="max-allowed-head-input",
                    type="number",
                    placeholder="Enter maximum allowed head",
                    step=0.1,
                    value=max_allowed_head,
                    className="mb-3"
                )
            ],
            className="mb-3"
        ),
    ]


def _build_aquifer_type_selector(default_value="unconfined"):
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
                value=default_value,
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
        label_style={
            "color": "#ffffff", 
            "fontWeight": "bold",
            "backgroundColor": "#28a745",
            "border": "1px solid #28a745"
        },
        active_label_style={
            "color": "#ffffff", 
            "backgroundColor": "#1e7e34",
            "border": "1px solid #1e7e34"
        },
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
                    
                    # Store for table data - load from dash_storage if available
                    dcc.Store(id="stratigraphy-data-store", data=_get_stratigraphy_data())
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
        label_style={
            "color": "#ffffff", 
            "fontWeight": "bold",
            "backgroundColor": "#17a2b8",
            "border": "1px solid #17a2b8"
        },
        active_label_style={
            "color": "#ffffff", 
            "backgroundColor": "#138496",
            "border": "1px solid #138496"
        },
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
                        ], width=12)
                    ], className="mb-3"),
                    
                    # Input fields for elevation and storage depth
                    dbc.Row([
                        dbc.Col([
                            html.Label("Ground Surface Elevation (ft):", className="fw-bold", style={"fontSize": "12px"}),
                            dbc.Input(
                                id="ground-surface-elevation",
                                type="number",
                                value=dash_storage.get_data("ground_surface_elevation") or 120.0,
                                step=0.1,
                                placeholder="Enter elevation",
                                size="sm",
                                className="mb-2"
                            ),
                            html.Label("Maximum MAR Storage Depth (ft):", className="fw-bold", style={"fontSize": "12px"}),
                            dbc.Input(
                                id="max-mar-storage-depth",
                                type="number",
                                value=dash_storage.get_data("max_mar_storage_depth") or 20.0,
                                step=0.1,
                                placeholder="Enter storage depth",
                                size="sm"
                            )
                        ], width=6),
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
                        ], width=6)
                    ], className="mb-3"),
                    
                    # Store for groundwater data - load from dash_storage if available
                    dcc.Store(id="groundwater-data-store", data=_get_groundwater_data())
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
        label_style={
            "color": "#ffffff", 
            "fontWeight": "bold",
            "backgroundColor": "#6c757d",
            "border": "1px solid #6c757d"
        },
        active_label_style={
            "color": "#ffffff", 
            "backgroundColor": "#545b62",
            "border": "1px solid #545b62"
        },
        children=[
            html.Div(
                [
                    html.H5("Horizontal Extension Configuration", className="mb-3"),
                    html.P("Configure the horizontal extension parameters for MAR project analysis.", className="mb-4"),
                    
                    # Input fields in two columns
                    dbc.Row([
                        dbc.Col([
                            html.Label("Length (ft):", className="fw-bold mb-2"),
                            dbc.Input(
                                id="extension-length",
                                type="number",
                                value=dash_storage.get_data("extension_length") or 100.0,
                                step=0.1,
                                placeholder="Enter length"
                            )
                        ], width=6),
                        dbc.Col([
                            html.Label("Width (ft):", className="fw-bold mb-2"),
                            dbc.Input(
                                id="extension-width",
                                type="number",
                                value=dash_storage.get_data("extension_width") or 50.0,
                                step=0.1,
                                placeholder="Enter width"
                            )
                        ], width=6)
                    ], className="mb-3"),
                    
                    dbc.Row([
                        dbc.Col([
                            html.Label("Rotation from North (degrees):", className="fw-bold mb-2"),
                            dbc.Input(
                                id="extension-rotation",
                                type="number",
                                value=dash_storage.get_data("extension_rotation") or 0.0,
                                step=1.0,
                                placeholder="Enter rotation angle"
                            )
                        ], width=6),
                        dbc.Col([
                            html.Label("Upstream Head (ft):", className="fw-bold mb-2"),
                            dbc.Input(
                                id="upstream-head",
                                type="number",
                                value=dash_storage.get_data("upstream_head") or 10.0,
                                step=0.1,
                                placeholder="Enter upstream head"
                            )
                        ], width=6)
                    ], className="mb-3"),
                    
                    dbc.Row([
                        dbc.Col([
                            html.Label("Downstream Head (ft):", className="fw-bold mb-2"),
                            dbc.Input(
                                id="downstream-head",
                                type="number",
                                value=dash_storage.get_data("downstream_head") or 5.0,
                                step=0.1,
                                placeholder="Enter downstream head"
                            )
                        ], width=6),
                        dbc.Col([
                            # Empty column for spacing
                        ], width=6)
                    ], className="mb-3")
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
                "Geometry and Stratigraphy",
                className="fw-bold bg-primary text-white",
            ),
            dbc.CardBody(
                [
                    _build_geometry_tabs(),
                ]
            ),
        ],
        className="mb-4",
    )


def _build_view_card():
    """Build the View card with three colored tabs."""
    return dbc.Card(
        [
            dbc.CardHeader(
                "View",
                className="fw-bold bg-primary text-white",
            ),
            dbc.CardBody(
                [
                    dbc.Tabs(
                        [
                            dbc.Tab(
                                label="Stratigraphy Cross Section",
                                tab_id="stratigraphy-cross-section",
                                children=[
                                    html.Div(
                                        [
                                            html.H6("Stratigraphy Cross Section", className="mb-3"),
                                            html.P("Visual representation of subsurface stratigraphy layers.", className="mb-3"),
                                            
                                            # Cross-section plot
                                            dcc.Graph(
                                                id="stratigraphy-cross-section-plot",
                                                style={'height': '500px'}
                                            )
                                        ],
                                        id="stratigraphy-cross-section-content"
                                    )
                                ],
                                label_style={
                                    "color": "#ffffff", 
                                    "fontWeight": "bold",
                                    "backgroundColor": "#dc3545",
                                    "border": "1px solid #dc3545"
                                },
                                active_label_style={
                                    "color": "#ffffff", 
                                    "backgroundColor": "#b02a37",
                                    "border": "1px solid #b02a37"
                                },
                            ),
                            dbc.Tab(
                                label="Available MAR Storage",
                                tab_id="available-mar-storage",
                                children=[
                                    html.Div(
                                        [
                                            html.H6("Available MAR Storage", className="mb-3"),
                                            html.P("Analysis of available storage capacity for MAR operations.", className="mb-3"),
                                            
                                            # Groundwater level plot
                                            dcc.Graph(
                                                id="groundwater-plot",
                                                style={'height': '600px'}
                                            )
                                        ],
                                        id="available-mar-storage-content"
                                    )
                                ],
                                label_style={
                                    "color": "#ffffff", 
                                    "fontWeight": "bold",
                                    "backgroundColor": "#28a745",
                                    "border": "1px solid #28a745"
                                },
                                active_label_style={
                                    "color": "#ffffff", 
                                    "backgroundColor": "#1e7e34",
                                    "border": "1px solid #1e7e34"
                                },
                            ),
                            dbc.Tab(
                                label="XY View",
                                tab_id="xy-view",
                                children=[
                                    html.Div(
                                        [
                                            html.H6("XY View", className="mb-3"),
                                            html.P("Plan view visualization of hydrogeological features.", className="mb-3"),
                                            
                                            # XY View plot
                                            dcc.Graph(
                                                id="xy-view-plot",
                                                style={'height': '500px'}
                                            )
                                        ],
                                        id="xy-view-content"
                                    )
                                ],
                                label_style={
                                    "color": "#ffffff", 
                                    "fontWeight": "bold",
                                    "backgroundColor": "#007bff",
                                    "border": "1px solid #007bff"
                                },
                                active_label_style={
                                    "color": "#ffffff", 
                                    "backgroundColor": "#0056b3",
                                    "border": "1px solid #0056b3"
                                },
                            ),
                        ],
                        id="view-tabs",
                        active_tab="stratigraphy-cross-section",
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