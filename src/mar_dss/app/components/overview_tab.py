"""
Overview tab components for MAR DSS dashboard.
"""

import dash_bootstrap_components as dbc
from dash import html, dcc
from datetime import datetime

# Import the function from components.water_source_tab
try:
    from mar_dss.app.components.water_source_tab import create_location_map
except ImportError:
    from .water_source_tab import create_location_map


def create_mar_purpose_section():
    """Create MAR Project Purpose section for overview."""
    return dbc.Card(
        [
            dbc.CardHeader(
                "MAR Project Purpose",
                className="fw-bold bg-primary text-white",
            ),
            dbc.CardBody(
                [
                    html.Label("Project Name:", className="fw-bold"),
                    dbc.Input(
                        id="project-name-input",
                        type="text",
                        placeholder="Enter your MAR project name...",
                        value="",
                        style={"margin-bottom": "15px"},
                    ),
                    html.Label("Analysis Date:", className="fw-bold"),
                    dbc.Input(
                        id="analysis-date-input",
                        type="date",
                        value=datetime.now().strftime("%Y-%m-%d"),
                        style={"margin-bottom": "15px"},
                    ),
                    html.Label("Project Location:", className="fw-bold"),
                    dbc.Input(
                        id="project-location-input",
                        type="text",
                        placeholder="Enter project location (e.g., Sacramento, CA)...",
                        value="",
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
                        value=["secure_water_supply"],  # Default selection
                        inline=False,
                        style={"margin-top": "10px"},
                    ),
                ]
            ),
        ]
    )


def create_location_map_section():
    """Create location map section for overview."""
    return dbc.Card(
        [
            dbc.CardHeader(
                "Project Location - Sacramento, California, United States",
                id="location-card-header",
                className="fw-bold bg-primary text-white",
            ),
            dbc.CardBody(
                [
                    dcc.Graph(
                        figure=create_location_map(),
                        config={"displayModeBar": True},
                        id="location-map",
                    )
                ]
            ),
        ]
    )


def create_overview_content():
    """Create the complete overview tab content."""
    return [
        dbc.Row(
            [
                dbc.Col([create_mar_purpose_section()], width=6),
                dbc.Col([create_location_map_section()], width=6),
            ],
            className="mb-4",
        )
    ]
