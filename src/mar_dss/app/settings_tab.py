"""
Hydrogeology tab content for MAR DSS dashboard.
"""

from dash import html, dcc
import dash_bootstrap_components as dbc


def create_settings_tab_content():
    """Create the content for the Hydrogeology tab."""
    return [
        html.H3("Hydrogeology"),
        html.P("Configure hydrogeological parameters for MAR project analysis."),
        
        # Aquifer Geometry & Stratigraphy Section
        dbc.Card([
            dbc.CardHeader("Aquifer Geometry & Stratigraphy", className="fw-bold bg-primary text-white"),
            dbc.CardBody([
                dbc.Row([
                    # Left Column - Depth to Water Table
                    dbc.Col([
                        html.H5("Depth to Water Table", className="fw-bold mb-3"),
                        dbc.Row([
                            dbc.Col([
                                html.Label("Seasonal High (m):", className="fw-bold"),
                                dbc.Input(
                                    id="water-table-high",
                                    type="number",
                                    placeholder="e.g., 2.5",
                                    step="0.1",
                                    min="0"
                                )
                            ], width=6),
                            dbc.Col([
                                html.Label("Seasonal Low (m):", className="fw-bold"),
                                dbc.Input(
                                    id="water-table-low",
                                    type="number",
                                    placeholder="e.g., 4.2",
                                    step="0.1",
                                    min="0"
                                )
                            ], width=6)
                        ], className="mb-3"),
                        html.P("Enter the seasonal variation in water table depth. High values typically occur during wet seasons, low values during dry seasons.", className="text-muted small")
                    ], width=6),
                    
                    # Right Column - Aquifer Thickness
                    dbc.Col([
                        html.H5("Aquifer Thickness", className="fw-bold mb-3"),
                        dbc.Row([
                            dbc.Col([
                                html.Label("Saturated Thickness (m):", className="fw-bold"),
                                dbc.Input(
                                    id="aquifer-thickness",
                                    type="number",
                                    placeholder="e.g., 15.0",
                                    step="0.1",
                                    min="0"
                                )
                            ], width=12)
                        ], className="mb-3"),
                        html.P("Total thickness of the saturated aquifer zone available for recharge.", className="text-muted small")
                    ], width=6)
                ], className="mb-4"),
                
                # Stratigraphy Section
                html.Hr(),
                html.H5("Stratigraphy: Aquifer and Aquitard Layers", className="fw-bold mb-3"),
                dbc.Row([
                    # Left Column - Layer Input Form
                    dbc.Col([
                        html.H6("Add New Layer", className="fw-bold mb-3"),
                        dbc.Row([
                            dbc.Col([
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
                                        {"label": "Silt Layer", "value": "silt"}
                                    ],
                                    value="aquifer",
                                    className="mb-2"
                                )
                            ], width=6),
                            dbc.Col([
                                html.Label("Thickness (m):", className="fw-bold"),
                                dbc.Input(
                                    id="layer-thickness-input",
                                    type="number",
                                    placeholder="e.g., 7.5",
                                    step="0.1",
                                    min="0",
                                    className="mb-2"
                                )
                            ], width=6)
                        ]),
                        dbc.Row([
                            dbc.Col([
                                dbc.Button(
                                    [
                                        html.I(className="fas fa-plus me-2"),
                                        "Add Layer"
                                    ],
                                    id="add-layer-btn",
                                    color="primary",
                                    className="w-100"
                                )
                            ], width=12)
                        ]),
                        html.Hr(),
                        html.H6("Layer Properties", className="fw-bold mb-3"),
                        dbc.Row([
                            dbc.Col([
                                html.Label("Hydraulic Conductivity (m/day):", className="fw-bold"),
                                dbc.Input(
                                    id="layer-conductivity",
                                    type="number",
                                    placeholder="e.g., 5.2",
                                    step="0.1",
                                    min="0"
                                )
                            ], width=6),
                            dbc.Col([
                                html.Label("Porosity (%):", className="fw-bold"),
                                dbc.Input(
                                    id="layer-porosity",
                                    type="number",
                                    placeholder="e.g., 25",
                                    step="1",
                                    min="0",
                                    max="100"
                                )
                            ], width=6)
                        ])
                    ], width=6),
                    
                    # Right Column - Vertical Profile Display
                    dbc.Col([
                        html.H6("Vertical Profile (Top to Bottom)", className="fw-bold mb-3"),
                        html.Div(
                            id="stratigraphy-profile",
                            children=[
                                html.Div([
                                    html.P("No layers added yet. Use the form on the left to add layers.", 
                                           className="text-muted text-center p-3")
                                ])
                            ],
                            style={
                                "border": "2px dashed #dee2e6",
                                "border-radius": "8px",
                                "min-height": "300px",
                                "background-color": "#f8f9fa"
                            }
                        ),
                        # Hidden store to maintain layer data
                        dcc.Store(id="stratigraphy-data-store", data=[]),
                        html.Hr(),
                        html.H6("Profile Summary", className="fw-bold mb-3"),
                        html.Div(
                            id="profile-summary",
                            children=[
                                html.P("Total Depth: 0 m", className="mb-1"),
                                html.P("Aquifer Layers: 0", className="mb-1"),
                                html.P("Aquitard Layers: 0", className="mb-0")
                            ]
                        )
                    ], width=6)
                ], className="mb-4"),
                
                # Aquifer Extent and Boundaries
                html.Hr(),
                html.H5("Aquifer Extent and Boundaries", className="fw-bold mb-3"),
                dbc.Row([
                    dbc.Col([
                        html.Label("Lateral Extent (km²):", className="fw-bold"),
                        dbc.Input(
                            id="aquifer-extent",
                            type="number",
                            placeholder="e.g., 25.5",
                            step="0.1",
                            min="0"
                        )
                    ], width=4),
                    dbc.Col([
                        html.Label("Boundary Type:", className="fw-bold"),
                        dbc.Select(
                            id="boundary-type",
                            options=[
                                {"label": "No-flow (Impermeable)", "value": "no-flow"},
                                {"label": "Constant Head", "value": "constant-head"},
                                {"label": "River/Stream", "value": "river"},
                                {"label": "Ocean/Sea", "value": "ocean"},
                                {"label": "Unknown/Uncertain", "value": "unknown"}
                            ],
                            value="unknown"
                        )
                    ], width=4),
                    dbc.Col([
                        html.Label("Boundary Distance (m):", className="fw-bold"),
                        dbc.Input(
                            id="boundary-distance",
                            type="number",
                            placeholder="e.g., 500",
                            step="1",
                            min="0"
                        )
                    ], width=4)
                ], className="mb-4"),
                
                # Depth to Impermeable Layers
                html.Hr(),
                html.H5("Depth to Impermeable Layers", className="fw-bold mb-3"),
                dbc.Row([
                    dbc.Col([
                        html.Label("Bedrock Depth (m):", className="fw-bold"),
                        dbc.Input(
                            id="bedrock-depth",
                            type="number",
                            placeholder="e.g., 25.0",
                            step="0.1",
                            min="0"
                        )
                    ], width=4),
                    dbc.Col([
                        html.Label("Clay Lens Depth (m):", className="fw-bold"),
                        dbc.Input(
                            id="clay-depth",
                            type="number",
                            placeholder="e.g., 12.5",
                            step="0.1",
                            min="0"
                        )
                    ], width=4),
                    dbc.Col([
                        html.Label("Additional Impermeable Layers:", className="fw-bold"),
                        dbc.Textarea(
                            id="impermeable-layers",
                            placeholder="Describe any other impermeable layers:\n- Silt layer at 8m\n- Dense clay at 18m",
                            rows=3
                        )
                    ], width=4)
                ])
            ])
        ], className="mb-4"),
        
        # Additional Hydrogeological Parameters
        dbc.Card([
            dbc.CardHeader("Additional Parameters", className="fw-bold bg-primary text-white"),
            dbc.CardBody([
                dbc.Row([
                    dbc.Col([
                        html.Label("Hydraulic Conductivity (m/day):", className="fw-bold"),
                        dbc.Input(
                            id="hydraulic-conductivity",
                            type="number",
                            placeholder="e.g., 5.2",
                            step="0.1",
                            min="0"
                        )
                    ], width=4),
                    dbc.Col([
                        html.Label("Porosity (%):", className="fw-bold"),
                        dbc.Input(
                            id="porosity",
                            type="number",
                            placeholder="e.g., 25",
                            step="1",
                            min="0",
                            max="100"
                        )
                    ], width=4),
                    dbc.Col([
                        html.Label("Specific Yield (%):", className="fw-bold"),
                        dbc.Input(
                            id="specific-yield",
                            type="number",
                            placeholder="e.g., 15",
                            step="1",
                            min="0",
                            max="100"
                        )
                    ], width=4)
                ])
            ])
        ])
    ]
