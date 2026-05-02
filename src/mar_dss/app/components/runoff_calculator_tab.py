"""
Runoff Calculator tab components for MAR DSS dashboard.
"""

import dash_bootstrap_components as dbc
import plotly.graph_objects as go
from dash import dcc, html
import dash_leaflet as dl
from dash import dash_table
import mar_dss.app.utils.data_storage as dash_storage


def _get_runoff_calculations_data():
    """Get runoff calculations table data from storage or return defaults."""
    saved_data = dash_storage.get_data("runoff_calculations_table")
    if saved_data:
        return saved_data
    
    # Return default data
    return [
        {"Parameter": "Area (acres)", "Value": 10},
        {"Parameter": "Composite Curve Number", "Value": 50},
        {"Parameter": "24-hour Rainfall (inches)", "Value": 5},
        {"Parameter": "Maximum Potential Storage (inches)", "Value": 10},
        {"Parameter": "Initial Abstraction", "Value": 0.05},
        {"Parameter": "Runoff Depth (inches)", "Value": 1},
        {"Parameter": "Runoff/Precipitation Ratio", "Value": 0.2},
        {"Parameter": "Runoff Volume (ft3)", "Value": 10000}
    ]


def create_runoff_map(lat=38.5816, lon=-121.4944, zoom=10):
    """Create an interactive runoff analysis map using Leaflet."""
    return dl.Map(
        center=[lat, lon],
        zoom=zoom,
        children=[
            dl.TileLayer(url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"),
            dl.LayerGroup(id="marker-layer"),
            dl.LayerGroup(id="stations-layer"),
            dl.LayerGroup(id="watershed-layer"),
        ],
        style={'width': '100%', 'height': '500px', 'borderRadius': '8px', 'boxShadow': '0 4px 6px rgba(0, 0, 0, 0.1)'},
        id="runoff-map"
    )


def create_map_card():
    """Create the map card component."""
    return dbc.Card([
        dbc.CardHeader("Runoff Analysis Map", className="fw-bold bg-primary text-white"),
        dbc.CardBody([
            create_runoff_map(),
            dbc.Tooltip(
                "Click the map to set coordinates; use layers for markers, stations, and watershed",
                target="runoff-map",
                placement="top",
            ),
        ])
    ])


def create_coordinate_inputs():
    """Create the latitude and longitude input fields."""
    return [
        html.Label("Selected Latitude:", className="fw-bold"),
        dbc.Input(
            id="selected-latitude",
            type="number",
            placeholder="Click map to set latitude",
            step=0.000001,
            style={"margin-bottom": "10px"}
        ),
        html.Label("Selected Longitude:", className="fw-bold"),
        dbc.Input(
            id="selected-longitude",
            type="number",
            placeholder="Click map to set longitude",
            step=0.000001,
            style={"margin-bottom": "15px"}
        ),
    ]


def create_action_buttons():
    """Create the action buttons for runoff analysis."""
    return [
        dbc.Button(
            "Obtain nearby streams",
            id="obtain-streams-btn",
            color="success",
            className="me-2 mb-3",
            title="Find stream features near the selected map location",
        ),
        dbc.Button(
            "Get Watershed Info",
            id="get-watershed-btn",
            color="info",
            className="mb-3",
            title="Retrieve watershed boundaries and attributes for the area",
        ),
        dbc.Button(
            "Calculate Runoff",
            id="calculate-runoff-btn",
            color="primary",
            className="me-2",
            title="Run runoff estimates using current watershed and CN inputs",
        ),
    ]


def create_controls_card():
    """Create the analysis controls card component."""
    return dbc.Card([
        dbc.CardHeader("Analysis Controls", className="fw-bold bg-primary text-white"),
        dbc.CardBody([
            *create_action_buttons(),
            html.Div(id="status-message", className="mt-3 mb-3"),
            html.Hr(),
            *create_coordinate_inputs(),
            html.Hr(),
            html.Div(id="runoff-results", className="mt-3"),
            html.Small(
                "Click on the map to add monitoring points or draw watershed boundaries.",
                className="text-muted"
            ),
            dbc.Tooltip(
                "Latitude from map click or manual entry (decimal degrees)",
                target="selected-latitude",
                placement="top",
            ),
            dbc.Tooltip(
                "Longitude from map click or manual entry (decimal degrees)",
                target="selected-longitude",
                placement="top",
            ),
        ])
    ])


def create_impervious_curve_number_content():
    """Create the impervious curve number selection component."""
    # Curve number data for impervious surfaces
    curve_number_options = [
        {"label": "Concrete - Fresh/Uncracked (CN: 99)", "value": "concrete_fresh"},
        {"label": "Concrete - Weathered/Cracked (CN: 97)", "value": "concrete_weathered"},
        {"label": "Asphalt - Fresh/Uncracked (CN: 99)", "value": "asphalt_fresh"},
        {"label": "Asphalt - Weathered/Cracked (CN: 97)", "value": "asphalt_weathered"},
    ]
    
    return dbc.Card([
        dbc.CardHeader("Estimated Impervious Curve Number Values", className="fw-bold bg-primary text-white"),
        dbc.CardBody([
            html.Label("Select Surface Condition:", className="fw-bold mb-2"),
            dbc.Select(
                id="impervious-curve-number-select",
                options=curve_number_options,
                placeholder="Select a surface condition...",
                className="mb-3"
            ),
            html.Div(id="selected-impervious-curve-number-display", className="mt-3"),
            dbc.Tooltip(
                "Curve number for fully impervious surfaces (SCS CN tables)",
                target="impervious-curve-number-select",
                placement="top",
            ),
        ])
    ])


def create_cover_soil_curve_number_content():
    """Create the cover description and soil type curve number selection component."""
    # Cover Description options (rows)
    cover_description_options = [
        {"label": "Open Space - Poor Condition", "value": "open_space_poor"},
        {"label": "Open Space - Fair Condition", "value": "open_space_fair"},
        {"label": "Open Space - Good Condition", "value": "open_space_good"},
        {"label": "Natural Desert Landscaping (pervious areas only)", "value": "natural_desert"},
        {"label": "Developing Urban Areas - Newly Graded Areas", "value": "developing_urban"},
    ]
    
    # Hydrologic Soil Type options (columns)
    soil_type_options = [
        {"label": "Hydrologic Soil Type A", "value": "type_a"},
        {"label": "Hydrologic Soil Type B", "value": "type_b"},
        {"label": "Hydrologic Soil Type C", "value": "type_c"},
        {"label": "Hydrologic Soil Type D", "value": "type_d"},
    ]
    
    return dbc.Card([
        dbc.CardHeader("Estimated Pervious Curve Number Values", className="fw-bold bg-primary text-white"),
        dbc.CardBody([
            dbc.Row([
                dbc.Col([
                    html.Label("Cover Description:", className="fw-bold mb-2"),
                    dbc.Select(
                        id="cover-description-select",
                        options=cover_description_options,
                        placeholder="Select cover description...",
                        className="mb-3"
                    ),
                ], width=6),
                dbc.Col([
                    html.Label("Hydrologic Soil Type:", className="fw-bold mb-2"),
                    dbc.Select(
                        id="soil-type-select",
                        options=soil_type_options,
                        placeholder="Select soil type...",
                        className="mb-3"
                    ),
                ], width=6)
            ]),
            html.Div(id="selected-curve-number-display", className="mt-3"),
            dbc.Tooltip(
                "Land cover condition for pervious portion of the watershed",
                target="cover-description-select",
                placement="top",
            ),
            dbc.Tooltip(
                "NRCS hydrologic soil group for pervious CN lookup",
                target="soil-type-select",
                placement="top",
            ),
        ])
    ])


def create_results_card():
    """Create the runoff calculation results card component with tabs."""
    return dbc.Card([
        dbc.CardHeader("Runoff Calculation Results", className="fw-bold bg-primary text-white"),
        dbc.CardBody([
            dbc.Tabs([
                dbc.Tab(
                    label="Watershed Info",
                    tab_id="watershed-tab",
                    children=[
                        html.Div(id="watershed-info-content", style={'minHeight': '400px', 'overflow': 'auto'})
                    ]
                ),
                dbc.Tab(
                    label="Rain Information",
                    tab_id="rain-tab",
                    children=[
                        html.Div(id="rain-info-content", style={'minHeight': '400px', 'overflow': 'auto'})
                    ]
                )
            ], id="results-tabs", active_tab="watershed-tab")
        ])
    ], style={'minHeight': '500px'})


def create_curve_number_tab():
    """Create the content for the Runoff Calculator tab."""
    return [
        html.H3("Runoff Calculator", className="mb-4"),
        html.P("The runoff calculations was developed based on STORME-PFAS tool that was developed as part of SERDP Project ER23-3741 (PFAS in Stormwater) (Vines et al., in review)", 
               className="mb-3 text-danger fst-italic fw-bold"),
        html.P("Calculate curve numbers and runoff patterns for your MAR project location.", className="mb-4"),
        dbc.Card([
            dbc.CardBody([
                html.H5("Step 1: Composite Curve Number Based on % Impervious Cover Calculator (Pick 1A or 1B)", 
                        className="fw-bold mb-3"),
                            dbc.Row([
                                dbc.Col([
                                    dbc.RadioItems(
                                        id="impervious-outlet-option",
                                        options=[
                                            {
                                                "label": "1A: Pick this one if all of your impervious areas outlet directly to the drainage system (see figure below).",
                                                "value": "1A"
                                            },
                                            {
                                                "label": "1B: Pick this one if all/some of impervious area flow spreads over pervious areas before entering the drainage system.",
                                                "value": "1B"
                                            }
                                        ],
                                        value=None,
                                        className="mb-4"
                                    ),
                                    html.Div(id="composite-cn-table", className="mt-3"),
                                    html.Div(
                                        dash_table.DataTable(
                                            id="composite-cn-datatable",
                                            data=[],
                                            columns=[
                                                {"name": "Parameter", "id": "Parameter", "editable": False},
                                                {"name": "Value", "id": "Value", "editable": True, "type": "numeric"}
                                            ]
                                        ),
                                        style={"display": "none"},
                                        id="composite-cn-datatable-wrapper"
                                    ),
                                    dcc.Store(id="composite-cn-table-store", data=None)
                                ], width=6),
                                dbc.Col([
                                    html.Img(
                                        src="/assets/curve_number.jpg",
                                        alt="Curve Number Diagram",
                                        style={"maxWidth": "70%", "height": "auto"}
                                    )
                                ], width=6)
                            ])
                        ])
                    ], className="mt-4 mb-4"),
                    dbc.Row([
                        dbc.Col([
                            create_impervious_curve_number_content()
                        ], width=6),
                        dbc.Col([
                            create_cover_soil_curve_number_content()
                        ], width=6)
                    ]),
                    dbc.Row([
                        dbc.Col([
                            dbc.Card([
                                dbc.CardHeader("Runoff for Single Storm", className="fw-bold bg-primary text-white"),
                                dbc.CardBody([
                                    html.H5("Step 2: Provide watershed area upstream of the diversion point of interest, and compute runoff.", 
                                            className="fw-bold mb-3"),
                                    html.Small(
                                        "The single storm runoff calculation is useful for the design of the MAR spreading pond sizing and site storage needed. The storm intensity will be downloaded from NOAA at the coordinate provided.",
                                        className="text-muted d-block mb-3"
                                    ),
                                    dbc.Row([
                                        dbc.Col([
                                            html.Label("Latitude:", className="fw-bold mb-2"),
                                            dbc.Input(
                                                id="runoff-single-storm-latitude",
                                                type="number",
                                                value=38.5816,
                                                placeholder="Enter latitude",
                                                className="mb-3"
                                            )
                                        ], width=6),
                                        dbc.Col([
                                            html.Label("Longitude:", className="fw-bold mb-2"),
                                            dbc.Input(
                                                id="runoff-single-storm-longitude",
                                                type="number",
                                                value=-121.4944,
                                                placeholder="Enter longitude",
                                                className="mb-3"
                                            )
                                        ], width=6)
                                    ]),
                                    dbc.Button(
                                        "Download Rain Statistics",
                                        id="download-rain-statistics-btn",
                                        color="secondary",
                                        className="mb-3",
                                        title="Fetch NOAA precipitation statistics for the coordinates entered",
                                    ),
                                    html.Div(id="runoff-calculations-content", className="mt-3"),
                                    dbc.Row([
                                        dbc.Col([
                                            html.H6("Runoff Calculations", className="fw-bold mb-2"),
                                            dash_table.DataTable(
                                                id="runoff-calculations-table",
                                                data=_get_runoff_calculations_data(),
                                                columns=[
                                                    {"name": "Parameter", "id": "Parameter", "editable": False},
                                                    {"name": "Value", "id": "Value", "editable": True, "type": "numeric"}
                                                ],
                                                style_cell={
                                                    'textAlign': 'left',
                                                    'padding': '10px',
                                                    'fontFamily': 'Arial, sans-serif',
                                                    'fontSize': '14px',
                                                    'border': '1px solid #4a90e2',
                                                    'backgroundColor': '#e8f4f8'
                                                },
                                                style_header={
                                                    'backgroundColor': '#2c5aa0',
                                                    'color': 'white',
                                                    'fontWeight': 'bold',
                                                    'border': '1px solid #1a3d6b',
                                                    'textAlign': 'center'
                                                },
                                                style_data={
                                                    'backgroundColor': '#f0f8ff',
                                                    'border': '1px solid #4a90e2',
                                                    'color': '#1a1a1a'
                                                },
                                                style_data_conditional=[
                                                    {
                                                        'if': {'row_index': 'odd'},
                                                        'backgroundColor': '#d6e9f5'
                                                    },
                                                    {
                                                        'if': {'column_id': 'Parameter'},
                                                        'backgroundColor': '#b8d4e3',
                                                        'fontWeight': 'bold'
                                                    }
                                                ]
                                            )
                                        ], width=6),
                                        dbc.Col([
                                            html.Div(id="rain-statistics-table-placeholder")
                                        ], width=6)
                                    ])
                                ])
                            ])
                        ], width=12)
                    ], className="mt-4"),
                    dbc.Row([
                        dbc.Col([
                            dbc.Card([
                                dbc.CardHeader("Monthly Runoff Estimation", className="fw-bold bg-primary text-white"),
                                dbc.CardBody([
                                    html.H5("Step 3: Estimate Annual Runoff", 
                                            className="fw-bold mb-3"),
                                    dbc.Row([
                                        dbc.Col([
                                            html.Label("Average number of rain events per month:", 
                                                       className="form-label mb-2"),
                                            dbc.Input(
                                                id="rain-events-per-month",
                                                type="number",
                                                value=3.0,
                                                min=0.1,
                                                step=0.1,
                                                className="mb-3"
                                            )
                                        ], width="auto"),
                                    ]),
                                    dbc.Row([
                                        dbc.Col([
                                            dbc.Button(
                                                "Get Monthly Rainfall and Runoff",
                                                id="get-monthly-rain-btn",
                                                color="primary",
                                                className="mb-3",
                                                title="Compute monthly rainfall depth and runoff using storm statistics",
                                            )
                                        ], width="auto"),
                                        dbc.Col([
                                            dbc.Checkbox(
                                                id="use-runoff-for-recharge-check",
                                                label="Use Runoff For Recharge",
                                                value=False,
                                                className="mb-3 ms-3"
                                            )
                                        ], width="auto")
                                    ]),
                                    html.Div(id="monthly-runoff-estimation-content")
                                ])
                            ])
                        ], width=12)
                    ], className="mt-4"),
        dbc.Tooltip(
            "Choose how impervious drainage connects to the storm system (affects composite CN)",
            target="impervious-outlet-option",
            placement="top",
        ),
        dbc.Tooltip(
            "Latitude for NOAA rain download and single-storm runoff (decimal degrees)",
            target="runoff-single-storm-latitude",
            placement="top",
        ),
        dbc.Tooltip(
            "Longitude for NOAA rain download and single-storm runoff (decimal degrees)",
            target="runoff-single-storm-longitude",
            placement="top",
        ),
        dbc.Tooltip(
            "Editable runoff calculation inputs and intermediate results",
            target="runoff-calculations-table",
            placement="top",
        ),
        dbc.Tooltip(
            "Typical number of runoff-producing storms per month for annualization",
            target="rain-events-per-month",
            placement="top",
        ),
        dbc.Tooltip(
            "When checked, monthly runoff estimates can feed MAR recharge inputs elsewhere",
            target="use-runoff-for-recharge-check",
            placement="top",
        ),
    ]


def create_runoff_calculator_tab():
    """Create the content for the Watershed Information tab."""
    return [
        html.H3("Watershed Information", className="mb-4"),
        html.P("Calculate and analyze runoff patterns for your MAR project location.", className="mb-4"),

        dbc.Tabs([
            dbc.Tab(
                label="Rainfall and Watershed Information",
                tab_id="rainfall-watershed-tab",
                children=[
                    dbc.Row([
                        dbc.Col([
                            create_map_card()
                        ], width=8),
                        dbc.Col([
                            create_controls_card()
                        ], width=4)
                    ], className="mb-4"),

                    dbc.Row([
                        dbc.Col([
                            create_results_card()
                        ])
                    ])
                ]
            )
        ], id="runoff-calculator-tabs", active_tab="rainfall-watershed-tab")
    ]