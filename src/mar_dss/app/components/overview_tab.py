"""Overview tab components for MAR DSS dashboard."""
# todo: make sure the location map is saved to the data storage and get updated.

from datetime import datetime
import dash_bootstrap_components as dbc
from dash import html, dcc
import mar_dss.app.utils.data_storage as dash_storage
import mar_dss.app.utils.helpers as helpers

try:
    from mar_dss.app.components.water_source_tab import create_location_map
except ImportError:
    from .water_source_tab import create_location_map


def create_mar_purpose_section():
    """Create MAR Project Purpose section for overview."""
    project_name = dash_storage.get_data("project_name")
    workspace = dash_storage.get_data("workspace")
    filename = dash_storage.get_data("filename")
    analysis_date_raw = dash_storage.get_data("analysis_date")
    
    if analysis_date_raw:
        try:
            if (isinstance(analysis_date_raw, str) and 
                len(analysis_date_raw) == 10 and 
                analysis_date_raw[4] == '-' and 
                analysis_date_raw[7] == '-'):
                analysis_date = analysis_date_raw
            else:
                parsed_date = helpers.parse_unknown_date(analysis_date_raw)
                analysis_date = parsed_date.strftime("%Y-%m-%d")
        except:
            analysis_date = datetime.now().strftime("%Y-%m-%d")
    else:
        analysis_date = datetime.now().strftime("%Y-%m-%d")
    
    project_location = dash_storage.get_data("project_location") or ""
    mar_purpose = dash_storage.get_data("mar_purpose") or ["secure_water_supply"] 
    
    return dbc.Card([
        dbc.CardHeader(
            "MAR Project Purpose",
            className="fw-bold bg-primary text-white",
        ),
        dbc.CardBody([
            html.Label("Project Name:", className="fw-bold"),
            dbc.Input(
                id="project-name-input",
                type="text",
                placeholder="Enter your MAR project name...",
                value=project_name,
                style={"margin-bottom": "15px"},
            ),
            dbc.Row([
                dbc.Col([
                    html.Label("Workspace:", className="fw-bold"),
                    dbc.Input(
                        id="workspace-input",
                        type="text",
                        placeholder="Enter workspace path...",
                        value=workspace,
                        style={"margin-bottom": "15px"},
                    )
                ], width=6),
                dbc.Col([
                    html.Label("File Name:", className="fw-bold"),
                    dbc.InputGroup([
                        dbc.Input(
                            id="filename-input",
                            type="text",
                            placeholder="Enter filename...",
                            value=filename,
                        ),
                        dbc.Button(
                            [html.I(className="fas fa-upload me-1"), "Load"],
                            id="btn-open",
                            color="outline-primary",
                            size="sm",
                            style={"padding": "4px 8px"},
                        )
                    ], style={"margin-bottom": "15px"})
                ], width=6)
            ]),
            html.Label("Analysis Date:", className="fw-bold"),
            dbc.Input(
                id="analysis-date-input",
                type="date",
                style={"margin-bottom": "15px"},
            ),
            html.Label("Project Location:", className="fw-bold"),
            dbc.Input(
                id="project-location-input",
                type="text",
                placeholder="Enter project location (e.g., Sacramento, CA)...",
                value=project_location,
                style={"margin-bottom": "20px"},
            ),
            html.Label("MAR Project Purpose:", className="fw-bold"),
            html.P(
                "Select one or more purposes for your MAR project:",
                className="text-muted small",
            ),
            dbc.Checklist(
                id="mar-purpose-checklist",
                options=[
                    {
                        "label": "Secure Water Supply",
                        "value": "secure_water_supply",
                    },
                    {
                        "label": "Restore Depleted Aquifer Storage",
                        "value": "restore_aquifer_storage",
                    },
                    {
                        "label": "Reduce Flood Impact",
                        "value": "reduce_flood_impact",
                    },
                    {
                        "label": "Mitigate Seawater Intrusion",
                        "value": "mitigate_seawater_intrusion",
                    },
                    {
                        "label": "Improve Water Quality",
                        "value": "improve_water_quality",
                    },
                ],
                value=mar_purpose,
                inline=False,
                style={"margin-top": "10px"},
            ),
        ])
    ])


def create_location_map_section():
    """Create location map section for overview."""
    return dbc.Card([
        dbc.CardHeader(
            "Project Location - Sacramento, California, United States",
            id="location-card-header",
            className="fw-bold bg-primary text-white",
        ),
        dbc.CardBody([
            dcc.Graph(
                figure=create_location_map(),
                config={"displayModeBar": True},
                id="location-map",
            )
        ])
    ])


def create_site_description_section():
    """Create Site Description section for overview."""
    # Get existing values from data storage if available
    ground_slope = dash_storage.get_data("ground_surface_slope") or 0.5
    max_area = dash_storage.get_data("max_available_area") or 1.0
    land_use = dash_storage.get_data("land_use") or "Urban Residential"
    
    return dbc.Card([
        dbc.CardHeader(
            "Site Description",
            className="fw-bold bg-primary text-white",
        ),
        dbc.CardBody([
            html.Label("Ground Surface Slope (%):", className="fw-bold"),
            dbc.Input(
                id="ground-slope-input",
                type="number",
                placeholder="Enter ground surface slope percentage...",
                value=ground_slope,
                min=0,
                step=0.1,
                style={"margin-bottom": "15px"},
            ),
            html.Label("Maximum Available Area for Recharge (acres):", className="fw-bold"),
            html.Small("This area is the total area available for the MAR site", className="text-muted d-block mb-2"),
            dbc.Input(
                id="max-area-input",
                type="number",
                placeholder="Enter maximum available area...",
                value=max_area,
                min=0,
                step=0.1,
                style={"margin-bottom": "15px"},
            ),
            html.Label("Land Use:", className="fw-bold"),
            html.P(
                "Select the primary land use type for the recharge site:",
                className="text-muted small",
            ),
            dcc.Dropdown(
                id="land-use-dropdown",
                options=[
                    {"label": "Urban Residential", "value": "Urban Residential"},
                    {"label": "Urban Nonresidential", "value": "Urban Nonresidential"},
                    {"label": "Rural Agricultural", "value": "Rural Agricultural"},
                    {"label": "Rural Open Space", "value": "Rural Open Space"},
                ],
                value=land_use,
                style={"margin-top": "10px"},
            ),
        ])
    ])


def create_overview_content():
    """Create the complete overview tab content."""
    return [
        dbc.Row([
            dbc.Col([create_mar_purpose_section()], width=6),
            dbc.Col([create_location_map_section()], width=6),
        ], className="mb-4"),
        dbc.Row([
            dbc.Col([create_site_description_section()], width=6),
        ], className="mb-4")
    ]
