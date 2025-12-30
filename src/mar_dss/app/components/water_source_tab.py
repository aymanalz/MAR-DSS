"""
General tab content and utilities for MAR DSS dashboard (Water Source).
"""

import dash_bootstrap_components as dbc
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import requests
from dash import dcc, dash_table, html
from dash.dash_table.Format import Format, Scheme
import mar_dss.app.utils.data_storage as dash_storage
from .runoff_calculator_tab import create_runoff_calculator_tab, create_curve_number_tab


def get_location_details(lat, lon):
    """Get city, state, and country from coordinates via reverse geocoding."""
    try:
        url = (
            "https://nominatim.openstreetmap.org/reverse?format=json&lat="
            f"{lat}&lon={lon}&zoom=10&addressdetails=1"
        )
        headers = {"User-Agent": "MAR-DSS-Dashboard/1.0"}
        response = requests.get(url, headers=headers, timeout=5)
        if response.status_code == 200:
            data = response.json()
            address = data.get("address", {})
            city = (
                address.get("city")
                or address.get("town")
                or address.get("village")
                or address.get("hamlet")
            )
            state = address.get("state")
            country = address.get("country")
            if city and state and country:
                return f"{city}, {state}, {country}"
            elif city and country:
                return f"{city}, {country}"
            elif state and country:
                return f"{state}, {country}"
            else:
                return country or "Unknown Location"
        return "Unknown Location"
    except Exception:
        return "Unknown Location"


def create_location_map(lat=38.5816, lon=-121.4944, location_name="Sacramento, CA", zoom=10):
    """Create a map centered on specified location with default Sacramento."""
    fig = go.Figure()
    fig.add_trace(
        go.Scattermapbox(
            lat=[lat],
            lon=[lon],
            mode="markers",
            marker=dict(size=20, color="red", symbol="circle"),
            text=[location_name],
            textposition="top center",
            name=location_name,
        )
    )
    fig.update_layout(
        mapbox=dict(style="open-street-map", center=dict(lat=lat, lon=lon), zoom=zoom),
        margin=dict(l=0, r=0, t=0, b=0),
        height=480,
    )
    return fig


def create_monthly_flow_chart(flow_data=None):
    """Create a chart showing monthly flow and cumulative annual flow."""
    months = [
        "Jan",
        "Feb",
        "Mar",
        "Apr",
        "May",
        "Jun",
        "Jul",
        "Aug",
        "Sep",
        "Oct",
        "Nov",
        "Dec",
    ]
    if flow_data is None:
        monthly_flow = [
            4500,
            4200,
            2800,
            2200,
            1800,
            1500,
            1200,
            1000,
            1300,
            2000,
            3800,
            4100,
        ]
    else:
        monthly_flow = [flow_data.get(month, 0) for month in months]
    cumulative_flow = np.cumsum(monthly_flow)
    fig = go.Figure()
    fig.add_trace(
        go.Bar(
            x=months,
            y=monthly_flow,
            name="Monthly Flow",
            marker_color="lightblue",
            yaxis="y",
        )
    )
    fig.add_trace(
        go.Scatter(
            x=months,
            y=cumulative_flow,
            mode="lines+markers",
            name="Cumulative Annual Flow",
            line=dict(color="red", width=3),
            marker=dict(size=8),
            yaxis="y2",
        )
    )
    fig.update_layout(
        title="Monthly Flow and Cumulative Annual Flow",
        xaxis_title="Month",
        yaxis=dict(title="Monthly Flow (ft³/month)", side="left"),
        yaxis2=dict(title="Cumulative Flow (ft³)", side="right", overlaying="y"),
        height=480,
        width=800,
        margin=dict(l=0, r=50, t=50, b=50),
        legend=dict(
            yanchor="top", y=0.95, xanchor="center", x=0.5, orientation="v"
        ),
        autosize=False,
    )
    return fig


def _get_flow_store_data():
    """Get flow data in dictionary format for flow-data-store from dash_storage."""
    months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    default_flows = [4500, 4200, 2800, 2200, 1800, 1500, 1200, 1000, 1300, 2000, 3800, 4100]
    monthly_flows = dash_storage.get_data("monthly_flow") or default_flows
    
    # Ensure we have exactly 12 values
    if len(monthly_flows) != 12:
        monthly_flows = default_flows
    
    # Convert list to dictionary format
    return {month: flow for month, flow in zip(months, monthly_flows)}


def create_editable_flow_table():
    """Create an editable table for monthly flow data."""
    months = [
        "Jan",
        "Feb",
        "Mar",
        "Apr",
        "May",
        "Jun",
        "Jul",
        "Aug",
        "Sep",
        "Oct",
        "Nov",
        "Dec",
    ]
    # Get existing values from data storage if available
    default_flows = [4500, 4200, 2800, 2200, 1800, 1500, 1200, 1000, 1300, 2000, 3800, 4100]
    monthly_flows = dash_storage.get_data("monthly_flow") or default_flows
    
    # Ensure we have exactly 12 values
    if len(monthly_flows) != 12:
        monthly_flows = default_flows
    
    df = pd.DataFrame(
        {
            "Month": months,
            "Flow (ft³/month)": monthly_flows,
        }
    )
    table = html.Div(
        [
            dash_table.DataTable(
                id="flow-data-table",
                data=df.to_dict("records"),
                columns=[
                    {"name": "Month", "id": "Month", "type": "text", "editable": False},
                    {
                        "name": "Flow (ft³/month)",
                        "id": "Flow (ft³/month)",
                        "type": "numeric",
                        "editable": True,
                        "format": Format(precision=1, scheme=Scheme.fixed),
                    },
                ],
                style_cell={
                    "textAlign": "center",
                    "padding": "8px",
                    "fontFamily": "Arial, sans-serif",
                    "fontSize": "14px",
                },
                style_header={
                    "backgroundColor": "#28a745",
                    "color": "white",
                    "fontWeight": "bold",
                },
                style_data={"backgroundColor": "white", "color": "black"},
                style_data_conditional=[
                    {"if": {"row_index": "odd"}, "backgroundColor": "#f8f9fa"}
                ],
                editable=True,
                row_deletable=False,
                sort_action="none",
                filter_action="none",
                style_table={"width": "300px", "maxWidth": "300px"},
            )
        ]
    )
    return table


def create_water_source_info_tab():
    """Create the content for the Water Source Information tab."""
    # Get existing values from data storage if available
    water_source = dash_storage.get_data("water_source") or "surface_water_sources"
    proximity_distance = dash_storage.get_data("proximity_distance") or 1.0
    water_conveyance = dash_storage.get_data("water_conveyance") or "open_canals_ditches"
    water_ownership = dash_storage.get_data("water_ownership") or "legal_rights"
    pumping_needed = dash_storage.get_data("pumping_needed") or "no"
    physical_parameters = dash_storage.get_data("physical_parameters") or []
    chemical_parameters = dash_storage.get_data("chemical_parameters") or []
    biological_indicators = dash_storage.get_data("biological_indicators") or []
    emerging_contaminants = dash_storage.get_data("emerging_contaminants") or []
    
    return [
        html.H3("Water Source Information"),
        html.P("Water source details and configuration for your MAR project."),
        dbc.Row(
            [
                dbc.Col(
                    [
                        dbc.Card(
                            [
                                dbc.CardHeader(
                                    "Water Source",
                                    className="fw-bold bg-primary text-white",
                                ),
                                dbc.CardBody(
                                    [
                                        dbc.Row(
                                            [
                                                dbc.Col(
                                                    [
                                                        html.Label(
                                                            "Water Source:",
                                                            className="fw-bold",
                                                        ),
                                                        html.P(
                                                            "Select the water source for your MAR project:",
                                                            className="text-muted small",
                                                        ),
                                                        dcc.Dropdown(
                                                            id="water-source-dropdown",
                                                            options=[
                                                                {
                                                                    "label": "(1) Surface Water Sources (streams, Reservoir, canals)",
                                                                    "value": "surface_water_sources",
                                                                },
                                                                {
                                                                    "label": "(2) Urban Stormwater Runoff",
                                                                    "value": "urban_stormwater_runoff",
                                                                },
                                                                {
                                                                    "label": "(3) Rural/Agricultural Runoff",
                                                                    "value": "rural_agricultural_runoff",
                                                                },
                                                                {
                                                                    "label": "(4) Reclaimed Water",
                                                                    "value": "reclaimed_water",
                                                                },
                                                                {
                                                                    "label": "(5) Other Groundwater Basin",
                                                                    "value": "other_groundwater_basin",
                                                                },
                                                                {
                                                                    "label": "(6) Other Non-Conventional Sources",
                                                                    "value": "other_non_conventional_sources",
                                                                },
                                                            ],
                                                            value=water_source,
                                                            placeholder="Select water source...",
                                                            style={"margin-top": "10px"},
                                                        ),
                                                        html.Hr(className="my-3"),
                                                        html.Label(
                                                            "Proximity Distance from Recharge Site:",
                                                            className="fw-bold",
                                                        ),
                                                        html.P(
                                                            "Enter the distance from the water source to the recharge site:",
                                                            className="text-muted small",
                                                        ),
                                                        dbc.Input(
                                                            id="proximity-distance-input",
                                                            type="number",
                                                            value=proximity_distance,
                                                            min=0.1,
                                                            max=100.0,
                                                            step=0.1,
                                                            placeholder="Enter distance in miles",
                                                            style={"margin-top": "10px"},
                                                        ),
                                                        html.Small(
                                                            "Distance in miles",
                                                            className="text-muted",
                                                        ),
                                                    ],
                                                    width=6,
                                                ),
                                                dbc.Col(
                                                    [
                                                        html.Label(
                                                            "Water Conveyance Methods:",
                                                            className="fw-bold",
                                                        ),
                                                        html.P(
                                                            "Select the method used to convey water to the recharge site:",
                                                            className="text-muted small",
                                                        ),
                                                        dcc.Dropdown(
                                                            id="water-conveyance-dropdown",
                                                            options=[
                                                                {
                                                                    "label": "Open canals/ditches",
                                                                    "value": "open_canals_ditches",
                                                                },
                                                                {
                                                                    "label": "Pipelines",
                                                                    "value": "pipelines",
                                                                },
                                                                {
                                                                    "label": "Direct Diversion",
                                                                    "value": "direct_diversion",
                                                                },
                                                                {"label": "Other", "value": "other"},
                                                            ],
                                                            value=water_conveyance,
                                                            placeholder="Select conveyance method...",
                                                            style={"margin-top": "10px"},
                                                        ),
                                                        html.Hr(className="my-3"),
                                                        html.Label(
                                                            "Water Ownership:",
                                                            className="fw-bold",
                                                        ),
                                                        html.P(
                                                            "Select the water ownership status:",
                                                            className="text-muted small",
                                                        ),
                                                        dbc.RadioItems(
                                                            id="water-ownership-radio",
                                                            options=[
                                                                {
                                                                    "label": "Legal Rights",
                                                                    "value": "legal_rights",
                                                                },
                                                                {"label": "None", "value": "none"},
                                                            ],
                                                            value=water_ownership,
                                                            inline=True,
                                                            style={"margin-top": "10px"},
                                                        ),
                                                        html.Hr(className="my-3"),
                                                        html.Label(
                                                            "Is pumping needed to move water from a source location to a recharge site for MAR?",
                                                            className="fw-bold",
                                                        ),
                                                        html.P(
                                                            "Select whether pumping is required:",
                                                            className="text-muted small",
                                                        ),
                                                        dbc.RadioItems(
                                                            id="pumping-needed-radio",
                                                            options=[
                                                                {
                                                                    "label": "Yes",
                                                                    "value": "yes",
                                                                },
                                                                {"label": "No", "value": "no"},
                                                            ],
                                                            value=pumping_needed,
                                                            inline=True,
                                                            style={"margin-top": "10px"},
                                                        ),
                                                    ],
                                                    width=6,
                                                ),
                                            ]
                                        )
                                    ]
                                ),
                            ]
                        )
                    ]
                ),
            ],
            className="mt-3",
        ),
        dbc.Row(
            [
                dbc.Col(
                    [
                        dbc.Card(
                            [
                                dbc.CardHeader(
                                    "Volume Estimates",
                                    className="fw-bold bg-primary text-white",
                                ),
                                dbc.CardBody(
                                    [
                                        dbc.Row(
                                            [
                                                dbc.Col(
                                                    [
                                                        html.H5(
                                                            "Monthly Average Flow",
                                                            className="fw-bold mb-3",
                                                        ),
                                                        html.P(
                                                            "Click on any cell to edit the flow values (ft³/month):",
                                                            className="text-muted small mb-3",
                                                        ),
                                                        dcc.Store(
                                                            id="flow-data-store",
                                                            data=_get_flow_store_data(),
                                                        ),
                                                        html.Div(id="flow-table-container"),
                                                    ],
                                                    width=4,
                                                ),
                                                dbc.Col(
                                                    [
                                                        html.H5(
                                                            "Monthly Flow Analysis",
                                                            className="fw-bold mb-3",
                                                        ),
                                                        dcc.Graph(
                                                            id="monthly-flow-chart",
                                                            figure=create_monthly_flow_chart(),
                                                            config={"displayModeBar": True},
                                                        ),
                                                    ],
                                                    width=8,
                                                ),
                                            ]
                                        )
                                    ]
                                ),
                            ]
                        )
                    ],
                    width=12,
                )
            ],
            className="mt-3",
        ),
    ]


def create_general_tab_content():
    """Create the main tab structure with Water Source Information, Curve Number, and Runoff Calculator tabs."""
    return [
        dbc.Tabs(
            [
                dbc.Tab(
                    label="Water Source Information",
                    tab_id="water-source-info",
                    children=create_water_source_info_tab(),
                    label_style={
                        "color": "#ffffff", 
                        "fontWeight": "bold",
                        "backgroundColor": "#2c5aa0",
                        "border": "1px solid #2c5aa0"
                    },
                    active_label_style={
                        "color": "#ffffff", 
                        "backgroundColor": "#1e3d72",
                        "border": "1px solid #1e3d72"
                    },
                ),
                dbc.Tab(
                    label="Runoff Calculator",
                    tab_id="curve-number",
                    children=create_curve_number_tab(),
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
                    label="Watershed Information",
                    tab_id="runoff-calculator",
                    children=create_runoff_calculator_tab(),
                    label_style={
                        "color": "#ffffff", 
                        "fontWeight": "bold",
                        "backgroundColor": "#dc3545",
                        "border": "1px solid #dc3545"
                    },
                    active_label_style={
                        "color": "#ffffff", 
                        "backgroundColor": "#a71e2a",
                        "border": "1px solid #a71e2a"
                    },
                ),
            ],
            id="water-source-tabs",
            active_tab="water-source-info",
        )
    ]


