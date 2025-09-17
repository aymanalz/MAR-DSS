"""
General tab content for MAR DSS dashboard.
"""

from dash import html, dcc
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from dash.dependencies import Input, Output
import requests
import json
import dash_table


def get_location_details(lat, lon):
    """Get city, state, and country details from coordinates using reverse geocoding."""
    try:
        # Using Nominatim (OpenStreetMap) reverse geocoding service
        url = f"https://nominatim.openstreetmap.org/reverse?format=json&lat={lat}&lon={lon}&zoom=10&addressdetails=1"
        headers = {'User-Agent': 'MAR-DSS-Dashboard/1.0'}
        
        response = requests.get(url, headers=headers, timeout=5)
        if response.status_code == 200:
            data = response.json()
            address = data.get('address', {})
            
            city = address.get('city') or address.get('town') or address.get('village') or address.get('hamlet')
            state = address.get('state')
            country = address.get('country')
            
            # Format location name
            if city and state and country:
                return f"{city}, {state}, {country}"
            elif city and country:
                return f"{city}, {country}"
            elif state and country:
                return f"{state}, {country}"
            else:
                return country or "Unknown Location"
        else:
            return "Unknown Location"
    except:
        return "Unknown Location"


def create_location_map(lat=38.5816, lon=-121.4944, location_name="Sacramento, CA", zoom=10):
    """Create a map centered on specified location with default Sacramento, California."""
    fig = go.Figure()
    
    # Add location marker
    fig.add_trace(go.Scattermapbox(
        lat=[lat],
        lon=[lon],
        mode='markers',
        marker=dict(
            size=20,
            color='red',
            symbol='circle'
        ),
        text=[location_name],
        textposition="top center",
        name=location_name
    ))
    
    # Update layout for specified area
    fig.update_layout(
        mapbox=dict(
            style="open-street-map",
            center=dict(lat=lat, lon=lon),
            zoom=zoom
        ),
        margin=dict(l=0, r=0, t=0, b=0),
        height=480
        # Removed width constraint to fill available space
    )
    
    return fig


def create_monthly_flow_chart(flow_data=None):
    """Create a chart showing monthly flow and cumulative annual flow."""
    months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 
              'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    
    # Use provided data or default values
    if flow_data is None:
        monthly_flow = [4500, 4200, 2800, 2200, 1800, 1500, 
                        1200, 1000, 1300, 2000, 3800, 4100]
    else:
        monthly_flow = [flow_data.get(month, 0) for month in months]
    
    # Calculate cumulative flow
    cumulative_flow = np.cumsum(monthly_flow)
    
    # Create figure with secondary y-axis
    fig = go.Figure()
    
    # Add monthly flow bars
    fig.add_trace(go.Bar(
        x=months,
        y=monthly_flow,
        name='Monthly Flow',
        marker_color='lightblue',
        yaxis='y'
    ))
    
    # Add cumulative flow line
    fig.add_trace(go.Scatter(
        x=months,
        y=cumulative_flow,
        mode='lines+markers',
        name='Cumulative Annual Flow',
        line=dict(color='red', width=3),
        marker=dict(size=8),
        yaxis='y2'
    ))
    
    # Update layout
    fig.update_layout(
        title="Monthly Flow and Cumulative Annual Flow",
        xaxis_title="Month",
        yaxis=dict(
            title="Monthly Flow (m³/month)",
            side="left"
        ),
        yaxis2=dict(
            title="Cumulative Flow (m³)",
            side="right",
            overlaying="y"
        ),
        height=480,
        width=800,
        margin=dict(l=0, r=50, t=50, b=50),
        legend=dict(
            yanchor="top",
            y=0.95,
            xanchor="center",
            x=0.5,
            orientation="v"
        ),
        autosize=False
    )
    
    return fig


def create_editable_flow_table():
    """Create an editable table for monthly flow data."""
    # Create DataFrame for the table
    months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 
              'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    
    df = pd.DataFrame({
        'Month': months,
        'Flow (m³/month)': [4500, 4200, 2800, 2200, 1800, 1500, 
                           1200, 1000, 1300, 2000, 3800, 4100]
    })
    
    # Create DataTable
    table = html.Div([
        dash_table.DataTable(
            id='flow-data-table',
            data=df.to_dict('records'),
            columns=[
                {"name": "Month", "id": "Month", "type": "text", "editable": False},
                {"name": "Flow (m³/month)", "id": "Flow (m³/month)", "type": "numeric", "editable": True}
            ],
            style_cell={
                'textAlign': 'center',
                'padding': '8px',
                'fontFamily': 'Arial, sans-serif',
                'fontSize': '14px'
            },
            style_header={
                'backgroundColor': '#28a745',
                'color': 'white',
                'fontWeight': 'bold'
            },
            style_data={
                'backgroundColor': 'white',
                'color': 'black'
            },
            style_data_conditional=[
                {
                    'if': {'row_index': 'odd'},
                    'backgroundColor': '#f8f9fa'
                }
            ],
            editable=True,
            row_deletable=False,
            sort_action="none",
            filter_action="none",
            style_table={
                'width': '300px',
                'maxWidth': '300px'
            }
        )
    ])
    
    return table


def create_general_tab_content():
    """Create the content for the General tab."""
    
    return [
        html.H3("Water Source Information"),
        html.P("Water source details and configuration for your MAR project."),
        
        # Water Source section
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("Water Source", className="fw-bold bg-success text-white"),
                    dbc.CardBody([
                        dbc.Row([
                            dbc.Col([
                                html.Label("Water Source:", className="fw-bold"),
                                html.P("Select the water source for your MAR project:", className="text-muted small"),
                                dcc.Dropdown(
                                    id="water-source-dropdown",
                                    options=[
                                        {"label": "Drainage Basin", "value": "drainage_basin"},
                                        {"label": "Storm Water", "value": "storm_water"},
                                        {"label": "Impervious Surface Runoff", "value": "impervious_surface_runoff"},
                                        {"label": "Pervious Surface Runoff", "value": "pervious_surface_runoff"},
                                        {"label": "Waste Water Treatment Plant", "value": "waste_water_treatment_plant"},
                                        {"label": "Reservoir/Lake", "value": "reservoir_lake"},
                                        {"label": "Imported Water", "value": "imported_water"},
                                        {"label": "Others", "value": "others"}
                                    ],
                                    value="drainage_basin",  # Default selection
                                    placeholder="Select water source...",
                                    style={"margin-top": "10px"}
                                ),
                                html.Hr(className="my-3"),
                                html.Label("Proximity Distance from Recharge Site:", className="fw-bold"),
                                html.P("Enter the distance from the water source to the recharge site:", className="text-muted small"),
                                dbc.Input(
                                    id="proximity-distance-input",
                                    type="number",
                                    value=1.0,
                                    min=0.1,
                                    max=100.0,
                                    step=0.1,
                                    placeholder="Enter distance in miles",
                                    style={"margin-top": "10px"}
                                ),
                                html.Small("Distance in miles", className="text-muted")
                            ], width=6),
                            
                            dbc.Col([
                                html.Label("Water Conveyance Methods:", className="fw-bold"),
                                html.P("Select the method used to convey water to the recharge site:", className="text-muted small"),
                                dcc.Dropdown(
                                    id="water-conveyance-dropdown",
                                    options=[
                                        {"label": "Open canals/ditches", "value": "open_canals_ditches"},
                                        {"label": "Pipelines", "value": "pipelines"},
                                        {"label": "Direct Diversion", "value": "direct_diversion"},
                                        {"label": "Other", "value": "other"}
                                    ],
                                    value="open_canals_ditches",  # Default selection
                                    placeholder="Select conveyance method...",
                                    style={"margin-top": "10px"}
                                ),
                                html.Hr(className="my-3"),
                                html.Label("Water Ownership:", className="fw-bold"),
                                html.P("Select the water ownership status:", className="text-muted small"),
                                dbc.RadioItems(
                                    id="water-ownership-radio",
                                    options=[
                                        {"label": "Legal Rights", "value": "legal_rights"},
                                        {"label": "None", "value": "none"}
                                    ],
                                    value="legal_rights",  # Default selection
                                    inline=True,
                                    style={"margin-top": "10px"}
                                )
                            ], width=6)
                        ])
                    ])
                ])
            ], width=12)
        ], className="mt-3"),
        
        # Volume Estimates below
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("Volume Estimates", className="fw-bold bg-success text-white"),
                    dbc.CardBody([
                        dbc.Row([
                            dbc.Col([
                                html.H5("Monthly Average Flow", className="fw-bold mb-3"),
                                html.P("Click on any cell to edit the flow values (m³/month):", className="text-muted small mb-3"),
                                dcc.Store(id="flow-data-store", data={
                                    'Jan': 4500, 'Feb': 4200, 'Mar': 2800, 'Apr': 2200,
                                    'May': 1800, 'Jun': 1500, 'Jul': 1200, 'Aug': 1000,
                                    'Sep': 1300, 'Oct': 2000, 'Nov': 3800, 'Dec': 4100
                                }),
                                html.Div(id="flow-table-container")
                            ], width=4),
                            
                            dbc.Col([
                                html.H5("Monthly Flow Analysis", className="fw-bold mb-3"),
                                dcc.Graph(
                                    id="monthly-flow-chart",
                                    figure=create_monthly_flow_chart(),
                                    config={'displayModeBar': True}
                                )
                            ], width=8)
                        ])
                    ])
                ])
            ], width=12)
        ], className="mt-3"),
        
        # Water Quality card
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("Water Quality", className="fw-bold bg-success text-white"),
                    dbc.CardBody([
                        html.P("Water quality parameters and monitoring information will be displayed here.", 
                               className="text-muted")
                    ])
                ])
            ], width=12)
        ], className="mt-3")
    ]