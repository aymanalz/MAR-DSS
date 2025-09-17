"""
General tab content for MAR DSS dashboard.
"""

from dash import html, dcc
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
import requests
import json


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


def create_general_tab_content():
    """Create the content for the General tab."""
    
    # Create location map
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
    
    return [
        html.H3("General Information"),
        html.P("General information about the MAR DSS system and project details."),
        
        # Map and MAR Purpose side by side
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("MAR Purpose", className="fw-bold bg-success text-white"),
                    dbc.CardBody([
                        html.P("MAR DSS - Managed Aquifer Recharge Decision Support System"),
                        html.P("Version: 0.1.0"),
                        html.P("Author: Ayman H. Alzraiee"),
                        html.P("Email: aalzraiee@gsi-net.com"),
                        html.Hr(),
                        html.Label("Goals:", className="fw-bold"),
                        dcc.Dropdown(
                            id="goals-dropdown",
                            options=[
                                {"label": "Goal 1", "value": "goal1"},
                                {"label": "Goal 2", "value": "goal2"},
                                {"label": "Goal 3", "value": "goal3"}
                            ],
                            value="goal1",
                            style={"margin-top": "10px"}
                        )
                    ])
                ])
            ], width=6),
            
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("Project Location - Sacramento, California, United States", id="location-card-header", className="fw-bold bg-success text-white"),
                    dbc.CardBody([
                        dcc.Graph(
                            figure=create_location_map(),
                            config={'displayModeBar': True},
                            id="location-map"
                        )
                    ])
                ])
            ], width=6)
        ], className="mt-3"),
        
        # Project Details below
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("Project Details", className="fw-bold bg-success text-white"),
                    dbc.CardBody([
                        html.P("This dashboard provides monitoring and analysis capabilities for managed aquifer recharge systems."),
                        html.P("Features include water level monitoring, recharge rate analysis, and water quality assessment.")
                    ])
                ])
            ], width=12)
        ], className="mt-3")
    ]