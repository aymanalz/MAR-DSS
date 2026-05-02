"""Overview tab components for MAR DSS dashboard."""
# Overview map lat/lon/zoom persist via dash_storage (CSV Save/Load); see overview_callbacks.

from datetime import datetime
import dash_bootstrap_components as dbc
from dash import html, dcc
import mar_dss.app.utils.data_storage as dash_storage
import mar_dss.app.utils.helpers as helpers

try:
    from mar_dss.app.components.water_source_tab import create_location_map
except ImportError:
    from .water_source_tab import create_location_map

DEFAULT_OVERVIEW_MAP_LAT = 38.5816
DEFAULT_OVERVIEW_MAP_LON = -121.4944
DEFAULT_OVERVIEW_MAP_ZOOM = 10
DEFAULT_OVERVIEW_MAP_BASEMAP = "open-street-map"

OVERVIEW_BASEMAP_OPTIONS = [
    {"label": "OpenStreetMap", "value": "open-street-map"},
    {"label": "Carto Positron (light)", "value": "carto-positron"},
    {"label": "Carto Dark Matter", "value": "carto-darkmatter"},
    {"label": "Terrain (OpenTopoMap)", "value": "opentopomap"},
    {"label": "Satellite + streets (Esri)", "value": "satellite-streets"},
    {"label": "White background", "value": "white-bg"},
]

ALLOWED_OVERVIEW_BASEMAP_STYLES = frozenset(o["value"] for o in OVERVIEW_BASEMAP_OPTIONS)


def _float_storage(key, default):
    raw = dash_storage.get_data(key)
    if raw is None:
        return default
    try:
        return float(raw)
    except (TypeError, ValueError):
        return default


def get_overview_map_header_text():
    """Card header line for the overview map (saved view or default)."""
    label = dash_storage.get_data("overview_map_location_label")
    if label:
        return label
    project_location = (dash_storage.get_data("project_location") or "").strip()
    if project_location:
        return f"Project Location — {project_location}"
    return (
        "Project Location — Sacramento, California, United States "
        "(pan/zoom map to update saved view)"
    )


def get_overview_map_basemap():
    """Plotly Mapbox layout style string for the overview map."""
    raw = dash_storage.get_data("overview_map_basemap")
    # Legacy CSVs: Plotly preset stamen-terrain often freezes interaction (Stamen/Stadia migration).
    if raw == "stamen-terrain":
        return "opentopomap"
    if raw in ALLOWED_OVERVIEW_BASEMAP_STYLES:
        return raw
    return DEFAULT_OVERVIEW_MAP_BASEMAP


def get_overview_map_figure_params():
    """Lat, lon, zoom, marker label, and basemap style for the overview location map."""
    lat = _float_storage("overview_map_lat", DEFAULT_OVERVIEW_MAP_LAT)
    lon = _float_storage("overview_map_lon", DEFAULT_OVERVIEW_MAP_LON)
    zoom = _float_storage("overview_map_zoom", DEFAULT_OVERVIEW_MAP_ZOOM)
    marker = (dash_storage.get_data("project_location") or "").strip()
    if not marker:
        marker = f"{lat:.4f}, {lon:.4f}"
    return lat, lon, zoom, marker, get_overview_map_basemap()


def create_mar_purpose_section():
    """Create MAR Project Purpose section for overview with tooltips."""
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
                value=project_name or "",
                style={"margin-bottom": "15px"},
            ),
            dbc.Row([
                dbc.Col([
                    html.Label("Workspace:", className="fw-bold"),
                    dbc.Input(
                        id="workspace-input",
                        type="text",
                        placeholder="Enter workspace path...",
                        value=workspace or "",
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
                            value=filename if filename is not None else "",
                        ),
                        dbc.Button(
                            [html.I(className="fas fa-upload me-1"), "Load"],
                            id="btn-open",
                            color="outline-primary",
                            size="sm",
                            title="Load an existing project file from the specified workspace",
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
            dbc.Tooltip(
                'Enter a descriptive name for your MAR project '
                '(e.g., "Sacramento Groundwater Recharge")',
                target="project-name-input",
                placement="top",
            ),
            dbc.Tooltip(
                "Specify the filesystem path where project files will be stored "
                "(default: current directory)",
                target="workspace-input",
                placement="top",
            ),
            dbc.Tooltip(
                "Filename for saving/loading the project (auto-generated if left blank)",
                target="filename-input",
                placement="top",
            ),
            dbc.Tooltip(
                "Select the date for the analysis (defaults to today)",
                target="analysis-date-input",
                placement="top",
            ),
            dbc.Tooltip(
                "Geographic location of the MAR project (used for mapping and analysis)",
                target="project-location-input",
                placement="top",
            ),
            dbc.Tooltip(
                "Select the objectives your MAR project aims to achieve",
                target="mar-purpose-checklist",
                placement="top",
            ),
        ])
    ])


def create_location_map_section():
    """Create location map section for overview with tooltips."""
    lat, lon, zoom, marker_name, basemap = get_overview_map_figure_params()
    header_text = get_overview_map_header_text()
    return dbc.Card([
        dbc.CardHeader(
            header_text,
            id="location-card-header",
            className="fw-bold bg-primary text-white",
        ),
        dbc.CardBody([
            html.Label("Basemap:", className="fw-bold small me-2"),
            dcc.Dropdown(
                id="overview-map-basemap",
                options=OVERVIEW_BASEMAP_OPTIONS,
                value=basemap,
                clearable=False,
                className="mb-2",
                style={"maxWidth": "320px"},
            ),
            dbc.Tooltip(
                "Switch background tiles; center and zoom stay as last saved from the map. "
                "Terrain uses OpenTopoMap (© OpenStreetMap contributors). "
                "Satellite + streets uses Esri imagery and reference overlays; comply with Esri terms.",
                target="overview-map-basemap",
                placement="top",
            ),
            dcc.Graph(
                figure=create_location_map(
                    lat=lat,
                    lon=lon,
                    location_name=marker_name,
                    zoom=float(zoom),
                    map_style=basemap,
                ),
                config={"displayModeBar": True, "scrollZoom": True},
                id="location-map",
            ),
            dbc.Tooltip(
                "Interactive map showing project location. Hover or click to explore geographic details",
                target="location-map",
                placement="top",
            ),
        ])
    ])


def create_site_description_section():
    """Create Site Description section for overview with tooltips."""
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
            dbc.Tooltip(
                "Enter slope as percentage (e.g., 5% = 0.05). Affects recharge calculations",
                target="ground-slope-input",
                placement="top",
            ),
            dbc.Tooltip(
                "Total land area available for recharge activities (impacts design capacity)",
                target="max-area-input",
                placement="top",
            ),
            dbc.Tooltip(
                "Land use type affects infiltration rates and suitability for recharge",
                target="land-use-dropdown",
                placement="top",
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
