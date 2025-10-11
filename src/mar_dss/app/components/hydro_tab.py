"""
Hydrogeology tab content for MAR DSS dashboard.
"""

import dash_bootstrap_components as dbc
from dash import dcc, html


def create_hydro_tab_content():
    """Create the content for the Hydrogeology tab."""
    return [
        *_build_hydro_tab_header(),
        _build_aquifer_geometry_card(),
        _build_additional_parameters_card(),
    ]


def _build_hydro_tab_header():
    """Build the hydrogeology tab header."""
    return [
        html.H3("Hydrogeology"),
        html.P(
            "Configure hydrogeological parameters for MAR project analysis."
        ),
    ]


def _build_aquifer_geometry_card():
    """Build the main aquifer geometry and stratigraphy card."""
    return dbc.Card(
        [
            dbc.CardHeader(
                "Aquifer Geometry & Stratigraphy",
                className="fw-bold bg-primary text-white",
            ),
            dbc.CardBody(
                [
                    *_build_stratigraphy_table(),
                    html.Hr(),
                    _build_water_table_section(),
                    html.Hr(),
                    *_build_stratigraphy_section(),
                    html.Hr(),
                    *_build_aquifer_extent_section(),
                    html.Hr(),
                    *_build_impermeable_layers_section(),
                ]
            ),
        ],
        className="mb-4",
    )


def _build_additional_parameters_card():
    """Build the additional parameters card."""
    return dbc.Card(
        [
            dbc.CardHeader(
                "Additional Parameters",
                className="fw-bold bg-primary text-white",
            ),
            dbc.CardBody(
                [
                    dbc.Row(
                        [
                            dbc.Col(
                                [
                                    html.Label("Hydraulic Conductivity (m/day):", className="fw-bold"),
                                    dbc.Input(
                                        id="hydraulic-conductivity",
                                        type="number",
                                        placeholder="e.g., 5.2",
                                        step="0.1",
                                        min="0",
                                    ),
                                ],
                                width=4,
                            ),
                            dbc.Col(
                                [
                                    html.Label("Porosity (%):", className="fw-bold"),
                                    dbc.Input(
                                        id="porosity",
                                        type="number",
                                        placeholder="e.g., 25",
                                        step="1",
                                        min="0",
                                        max="100",
                                    ),
                                ],
                                width=4,
                            ),
                            dbc.Col(
                                [
                                    html.Label("Specific Yield (%):", className="fw-bold"),
                                    dbc.Input(
                                        id="specific-yield",
                                        type="number",
                                        placeholder="e.g., 15",
                                        step="1",
                                        min="0",
                                        max="100",
                                    ),
                                ],
                                width=4,
                            ),
                        ]
                    )
                ]
            ),
        ]
    )


# ------------------------------
# Helper functions for aquifer geometry card
# ------------------------------


def _build_stratigraphy_table():
    """Build the stratigraphy table with add/remove functionality."""
    return [
        html.H5(
            "Stratigraphy: Aquifer and Aquitard Layers",
            className="fw-bold mb-3"
        ),
        dbc.Table(
            [
                html.Thead(
                    html.Tr([
                        html.Th("Parameter", className="fw-bold"),
                        html.Th("Elevation/Depth (m)", className="fw-bold"),
                        html.Th("Actions", className="fw-bold text-center"),
                    ])
                ),
                html.Tbody(
                    id="stratigraphy-table-body",
                    children=[
                        _build_stratigraphy_row(0, 3, {"parameter": "Top Soil Thickness", "depth": "1"}),
                        _build_stratigraphy_row(1, 3, {"parameter": "Water Table Depth", "depth": "20"}),
                        _build_stratigraphy_row(2, 3, {"parameter": "Bedrock Depth", "depth": "50"})
                    ]
                )
            ],
            striped=True,
            bordered=True,
            hover=True,
            responsive=True,
            className="mb-3"
        ),
        dbc.Row([
            dbc.Col([
                dbc.Button(
                    [html.I(className="fas fa-plus me-2"), "Add Row"],
                    id="add-stratigraphy-row-btn",
                    color="success",
                    size="sm",
                    className="me-2"
                ),
                dbc.Button(
                    [html.I(className="fas fa-trash me-2"), "Remove Last Row"],
                    id="remove-stratigraphy-row-btn",
                    color="danger",
                    size="sm",
                    disabled=True
                )
            ], width=12)
        ]),
        dcc.Store(
            id="stratigraphy-table-data",
            data={
                "parameter": ["Top Soil Thickness", "Water Table Depth", "Bedrock Depth"],
                "depth": ["1", "20", "50"]
            },
            storage_type="memory"
        )
    ]


def _build_stratigraphy_row(index, total_rows=1, row_data=None):
    """Build a single row for the stratigraphy table."""
    if row_data is None:
        row_data = {"parameter": "Top Soil Thickness", "depth": ""}
    
    # Define mandatory parameters that cannot be removed
    mandatory_params = ["Top Soil Thickness", "Water Table Depth", "Bedrock Depth"]
    is_mandatory = row_data.get("parameter") in mandatory_params
    
    # Determine button states based on parameter type and position
    can_move_up = not (row_data.get("parameter") == "Top Soil Thickness")
    can_move_down = not (row_data.get("parameter") == "Bedrock Depth")
    can_remove = not is_mandatory
    
    return html.Tr([
        html.Td([
            dbc.Select(
                id={"type": "stratigraphy-parameter", "index": index},
                options=[
                    {
                        "label": "Top Soil Thickness",
                        "value": "Top Soil Thickness"
                    },
                    {
                        "label": "Water Table Depth",
                        "value": "Water Table Depth"
                    },
                    {
                        "label": "Bedrock Depth",
                        "value": "Bedrock Depth"
                    },
                    {
                        "label": "Gravel Layer Thickness",
                        "value": "Gravel Layer Thickness"
                    },
                    {
                        "label": "Sand Layer Thickness",
                        "value": "Sand Layer Thickness"
                    },
                    {
                        "label": "Silt Layer Thickness",
                        "value": "Silt Layer Thickness"
                    },
                    {
                        "label": "Loam Layer Thickness",
                        "value": "Loam Layer Thickness"
                    },
                    {
                        "label": "Clay Layer Thickness",
                        "value": "Clay Layer Thickness"
                    },
                ],
                value=row_data.get("parameter", "Top Soil Thickness"),
                size="sm"
            )
        ]),
        html.Td([
            dbc.Input(
                id={"type": "stratigraphy-depth", "index": index},
                type="number",
                placeholder="e.g., 2.5",
                step="0.1",
                min="0",
                size="sm",
                value=row_data.get("depth", "")
            )
        ]),
        html.Td([
            dbc.ButtonGroup([
                dbc.Button(
                    [html.I(className="fas fa-arrow-up")],
                    id={"type": "move-stratigraphy-up", "index": index},
                    color="secondary",
                    size="sm",
                    className="btn-sm",
                    disabled=(not can_move_up or index == 0)
                ),
                dbc.Button(
                    [html.I(className="fas fa-arrow-down")],
                    id={"type": "move-stratigraphy-down", "index": index},
                    color="secondary",
                    size="sm",
                    className="btn-sm",
                    disabled=(not can_move_down or index == total_rows - 1)
                ),
                dbc.Button(
                    [html.I(className="fas fa-trash")],
                    id={"type": "remove-stratigraphy-row", "index": index},
                    color="danger",
                    size="sm",
                    className="btn-sm",
                    disabled=(not can_remove)
                )
            ], size="sm")
        ], className="text-center")
    ])

def _build_water_table_section():
    """Build the water table depth and aquifer thickness section."""
    return dbc.Row(
        [
            dbc.Col([*_build_water_table_inputs()], width=6),
            dbc.Col([*_build_aquifer_thickness_inputs()], width=6),
        ],
        className="mb-4",
    )


def _build_water_table_inputs():
    """Build water table depth inputs."""
    return [
        html.H5("Depth to Water Table", className="fw-bold mb-3"),
        dbc.Row(
            [
                dbc.Col(
                    [
                        html.Label("Seasonal High (m):", className="fw-bold"),
                        dbc.Input(
                            id="water-table-high",
                            type="number",
                            placeholder="e.g., 2.5",
                            step="0.1",
                            min="0",
                        ),
                    ],
                    width=6,
                ),
                dbc.Col(
                    [
                        html.Label("Seasonal Low (m):", className="fw-bold"),
                        dbc.Input(
                            id="water-table-low",
                            type="number",
                            placeholder="e.g., 4.2",
                            step="0.1",
                            min="0",
                        ),
                    ],
                    width=6,
                ),
            ],
            className="mb-3",
        ),
        html.P(
            "Enter the seasonal variation in water table depth. "
            "High values typically occur during wet seasons, "
            "low values during dry seasons.",
            className="text-muted small",
        ),
    ]


def _build_aquifer_thickness_inputs():
    """Build aquifer thickness inputs."""
    return [
        html.H5("Aquifer Thickness", className="fw-bold mb-3"),
        dbc.Row(
            [
                dbc.Col(
                    [
                        html.Label("Saturated Thickness (m):", className="fw-bold"),
                        dbc.Input(
                            id="aquifer-thickness",
                            type="number",
                            placeholder="e.g., 15.0",
                            step="0.1",
                            min="0",
                        ),
                    ],
                    width=12,
                )
            ],
            className="mb-3",
        ),
        html.P(
            "Total thickness of the saturated aquifer zone "
            "available for recharge.",
            className="text-muted small",
        ),
    ]


def _build_stratigraphy_section():
    """Build the stratigraphy section with layer management."""
    return [
        html.H5("Stratigraphy: Aquifer and Aquitard Layers", className="fw-bold mb-3"),
        dbc.Row(
            [
                dbc.Col([*_build_layer_input_form()], width=6),
                dbc.Col([*_build_vertical_profile_display()], width=6),
            ],
            className="mb-4",
        ),
    ]


def _build_layer_input_form():
    """Build the layer input form."""
    return [
        html.H6("Add New Layer", className="fw-bold mb-3"),
        dbc.Row(
            [
                dbc.Col(
                    [
                        html.Label("Layer Type:", className="fw-bold"),
                        dbc.Select(
                            id="layer-type-select",
                            options=[
                                {"label": "Aquifer (High Permeability)", "value": "aquifer"},
                                {"label": "Aquitard (Low Permeability)", "value": "aquitard"},
                                {"label": "Confining Layer", "value": "confining"},
                                {"label": "Bedrock", "value": "bedrock"},
                                {"label": "Topsoil", "value": "topsoil"},
                                {"label": "Clay Lens", "value": "clay"},
                                {"label": "Silt Layer", "value": "silt"},
                            ],
                            value="aquifer",
                            className="mb-2",
                        ),
                    ],
                    width=6,
                ),
                dbc.Col(
                    [
                        html.Label("Thickness (m):", className="fw-bold"),
                        dbc.Input(
                            id="layer-thickness-input",
                            type="number",
                            placeholder="e.g., 7.5",
                            step="0.1",
                            min="0",
                            className="mb-2",
                        ),
                    ],
                    width=6,
                ),
            ]
        ),
        dbc.Row(
            [
                dbc.Col(
                    [
                        dbc.Button(
                            [html.I(className="fas fa-plus me-2"), "Add Layer"],
                            id="add-layer-btn",
                            color="primary",
                            className="w-100",
                        )
                    ],
                    width=12,
                )
            ]
        ),
        html.Hr(),
        *_build_layer_properties_form(),
    ]


def _build_layer_properties_form():
    """Build the layer properties form."""
    return [
        html.H6("Layer Properties", className="fw-bold mb-3"),
        dbc.Row(
            [
                dbc.Col(
                    [
                        html.Label("Hydraulic Conductivity (m/day):", className="fw-bold"),
                        dbc.Input(
                            id="layer-conductivity",
                            type="number",
                            placeholder="e.g., 5.2",
                            step="0.1",
                            min="0",
                        ),
                    ],
                    width=6,
                ),
                dbc.Col(
                    [
                        html.Label("Porosity (%):", className="fw-bold"),
                        dbc.Input(
                            id="layer-porosity",
                            type="number",
                            placeholder="e.g., 25",
                            step="1",
                            min="0",
                            max="100",
                        ),
                    ],
                    width=6,
                ),
            ]
        ),
    ]


def _build_vertical_profile_display():
    """Build the vertical profile display."""
    return [
        html.H6("Vertical Profile (Top to Bottom)", className="fw-bold mb-3"),
        html.Div(
            id="stratigraphy-profile",
            children=[
                html.Div(
                    [
                        html.P(
                            "No layers added yet. Use the form on the left to add layers.",
                            className="text-muted text-center p-3",
                        )
                    ]
                )
            ],
            style={
                "border": "2px dashed #dee2e6",
                "border-radius": "8px",
                "min-height": "300px",
                "background-color": "#f8f9fa",
            },
        ),
        dcc.Store(
            id="stratigraphy-data-store-local",
            data=[],
            storage_type="memory",
        ),
        html.Hr(),
        *_build_profile_summary(),
    ]


def _build_profile_summary():
    """Build the profile summary section."""
    return [
        html.H6("Profile Summary", className="fw-bold mb-3"),
        html.Div(
            id="profile-summary",
            children=[
                html.P("Total Depth: 0 m", className="mb-1"),
                html.P("Aquifer Layers: 0", className="mb-1"),
                html.P("Aquitard Layers: 0", className="mb-0"),
            ],
        ),
    ]


def _build_aquifer_extent_section():
    """Build the aquifer extent and boundaries section."""
    return [
        html.H5("Aquifer Extent and Boundaries", className="fw-bold mb-3"),
        dbc.Row(
            [
                dbc.Col(
                    [
                        html.Label("Lateral Extent (km²):", className="fw-bold"),
                        dbc.Input(
                            id="aquifer-extent",
                            type="number",
                            placeholder="e.g., 25.5",
                            step="0.1",
                            min="0",
                        ),
                    ],
                    width=4,
                ),
                dbc.Col(
                    [
                        html.Label("Boundary Type:", className="fw-bold"),
                        dbc.Select(
                            id="boundary-type",
                            options=[
                                {"label": "No-flow (Impermeable)", "value": "no-flow"},
                                {"label": "Constant Head", "value": "constant-head"},
                                {"label": "River/Stream", "value": "river"},
                                {"label": "Ocean/Sea", "value": "ocean"},
                                {"label": "Unknown/Uncertain", "value": "unknown"},
                            ],
                            value="unknown",
                        ),
                    ],
                    width=4,
                ),
                dbc.Col(
                    [
                        html.Label("Boundary Distance (m):", className="fw-bold"),
                        dbc.Input(
                            id="boundary-distance",
                            type="number",
                            placeholder="e.g., 500",
                            step="1",
                            min="0",
                        ),
                    ],
                    width=4,
                ),
            ],
            className="mb-4",
        ),
    ]


def _build_impermeable_layers_section():
    """Build the impermeable layers section."""
    return [
        html.H5("Depth to Impermeable Layers", className="fw-bold mb-3"),
        dbc.Row(
            [
                dbc.Col(
                    [
                        html.Label("Bedrock Depth (m):", className="fw-bold"),
                        dbc.Input(
                            id="bedrock-depth",
                            type="number",
                            placeholder="e.g., 25.0",
                            step="0.1",
                            min="0",
                        ),
                    ],
                    width=4,
                ),
                dbc.Col(
                    [
                        html.Label("Clay Lens Depth (m):", className="fw-bold"),
                        dbc.Input(
                            id="clay-depth",
                            type="number",
                            placeholder="e.g., 12.5",
                            step="0.1",
                            min="0",
                        ),
                    ],
                    width=4,
                ),
                dbc.Col(
                    [
                        html.Label("Additional Impermeable Layers:", className="fw-bold"),
                        dbc.Textarea(
                            id="impermeable-layers",
                            placeholder=(
                                "Describe any other impermeable layers:\n- Silt layer at 8m\n- Dense clay at 18m"
                            ),
                            rows=3,
                        ),
                    ],
                    width=4,
                ),
            ]
        ),
    ]


