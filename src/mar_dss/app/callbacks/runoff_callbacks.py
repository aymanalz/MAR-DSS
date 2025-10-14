"""
Callbacks for the Runoff Calculator tab.
"""

import dash
from dash import Input, Output, html, no_update, State
import dash_leaflet as dl
import pandas as pd
import osmnx as ox
import geopandas as gpd
import streamstats
import json
from dash import dash_table


try:
    from mar_dss.app.components.runoff_calculator_tab import create_runoff_map
except ImportError:
    from ..components.runoff_calculator_tab import create_runoff_map
df = pd.DataFrame()

def get_streams_near_point(lat, lon, distance_m=16093):
    """Find streams within specified distance of a point"""
    try:
        print(f"Searching for streams near: {lat}, {lon}")
        # Download waterway features using osmnx features module
        gdf_waterways = ox.features_from_point(
            center_point=(lat, lon), 
            dist=distance_m, 
            tags={'waterway': True}
        )
        
        # Filter for stream-like features
        stream_types = ['stream', 'river', 'canal', 'drain', 'ditch']
        waterways = gdf_waterways[gdf_waterways['waterway'].isin(stream_types)]
        
        print(f"Found {len(waterways)} waterway features")
        return waterways
    except Exception as e:
        print(f"Error finding streams: {e}")
        return gpd.GeoDataFrame(columns=["geometry"])

def streams_to_geojson(streams):
    """Convert streams GeoDataFrame to GeoJSON"""
    if streams is None or streams.empty:
        print("No streams to convert to GeoJSON")
        return {}
    
    # Convert to GeoJSON
    geojson = json.loads(streams.to_json())
    print(f"Converted {len(geojson.get('features', []))} features to GeoJSON")
    return geojson

def setup_runoff_callbacks(app):
    """Register callbacks related to the runoff calculator tab."""
    print("Setting up runoff callbacks...")

    # Callback 1: Handle map clicks to update coordinates (exact same as open3.py)
    @app.callback(
        [Output('selected-latitude', 'value'),
         Output('selected-longitude', 'value'),
         Output('runoff-results', 'children')],
        [Input('runoff-map', 'clickData')]
    )
    def update_coordinates_on_click(clickData):
        print(f"Callback triggered with: {clickData}")  # Debug print
        
        if clickData is None:
            # Return default values on initial load
            return 38.5816, -121.4944, "Map ready - click to update coordinates"
        
        # Extract coordinates from clickData (Leaflet format)
        lat = clickData['latlng']['lat']
        lon = clickData['latlng']['lng']
        
        # Return the new coordinates directly to the input fields
        return lat, lon, f"Map Click Coordinates: {lat:.4f}, {lon:.4f}"

    # Callback 2: Update marker and map center based on input fields (exact same as open3.py)
    @app.callback(
        [Output('marker-layer', 'children'),
         Output('runoff-map', 'center')],
        [Input('selected-latitude', 'value'),
         Input('selected-longitude', 'value')]
    )
    def update_marker_on_coordinate_change(lat, lon):
        if lat is None or lon is None:
            return no_update, no_update

        marker = dl.Marker(
            position=[lat, lon], 
            children=[dl.Tooltip(f"Selected: {lat:.4f}, {lon:.4f}")],
            icon={'iconUrl': 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-red.png', 'iconSize': [25, 41], 'iconAnchor': [12, 41]}
        )
        
        # Center the map on the new coordinates when they change
        return [marker], [lat, lon]

    # Callback 3: Handle "Obtain nearby streams" button (exact same as open3.py)
    @app.callback(
        Output('stations-layer', 'children'),
        [Input('obtain-streams-btn', 'n_clicks')],
        [State('selected-latitude', 'value'),
         State('selected-longitude', 'value')]
    )
    def update_streams(n_clicks, lat, lon):
        if n_clicks and n_clicks > 0 and lat is not None and lon is not None:
            print(f"Searching streams for: {lat}, {lon}")
            # The distance is set in the function call to 16093 meters (approx 10 miles)
            streams = get_streams_near_point(lat, lon) 
            geojson_data = streams_to_geojson(streams)
            
            if geojson_data and 'features' in geojson_data and len(geojson_data['features']) > 0:
                return [dl.GeoJSON(
                    data=geojson_data, 
                    style={'color': 'blue', 'weight': 3, 'opacity': 0.8}
                )]
        
        return []

    # Callback 4: Handle "Get Watershed Info" button (exact same as open3.py)
    @app.callback(
        [Output('watershed-layer', 'children'),
         Output('runoff-calculation-output', 'children')],
        [Input('get-watershed-btn', 'n_clicks')],
        [State('selected-latitude', 'value'),
         State('selected-longitude', 'value')],
        prevent_initial_call=True
    )
    def get_watershed_info(n_clicks, lat, lon):
        if n_clicks and n_clicks > 0 and lat is not None and lon is not None:
            print(f"Getting watershed info for: {lat}, {lon}")
            
            # Get watershed data for the map
            try:
                ws = streamstats.Watershed(lat=lat, lon=lon)
                watershed_geojson = ws.boundary
                df_data = []
                for par in ws.parameters:
                    name = par['name']
                    description = par['description']
                    code = par['code']
                    unit = par['unit'] 
                    value = par['value']
                    df_data.append([name, description, code, unit, value])
                
                # Create DataFrame
                df = pd.DataFrame(df_data, columns=['Name', 'Description', 'Code', 'Unit', 'Value'])
                
                # Create watershed layer for the map
                watershed_layer = dl.GeoJSON(
                    data=watershed_geojson, 
                    style={'color': 'red', 'weight': 3, 'opacity': 0.8, 'fillOpacity': 0.2}
                )
                
                # Generate table from df with error handling
                try:
                    if df.empty:
                        table = html.P("No watershed parameters available.", className="text-orange-500 italic")
                    else:
                        table = dash_table.DataTable(
                            data=df.to_dict('records'),
                            columns=[{"name": i, "id": i} for i in df.columns],
                            style_cell={
                                'textAlign': 'left',
                                'padding': '10px',
                                'fontFamily': 'Arial, sans-serif',
                                'fontSize': '14px',
                                'border': '1px solid #ddd'
                            },
                            style_header={
                                'backgroundColor': '#f8f9fa',
                                'fontWeight': 'bold',
                                'border': '1px solid #ddd'
                            },
                            style_data={
                                'backgroundColor': 'white',
                                'border': '1px solid #ddd'
                            },
                            style_data_conditional=[
                                {
                                    'if': {'row_index': 'odd'},
                                    'backgroundColor': '#f8f9fa'
                                }
                            ],
                            page_size=0,  # Set to 0 to disable pagination
                            sort_action="native",
                            filter_action="native",
                            export_format="csv"
                        )
                except Exception as table_error:
                    print(f"Error creating table: {table_error}")
                    table = html.P(f"Error creating table: {str(table_error)}", className="text-red-500")
                print(f"Table generated with {len(df)} rows")
                return [watershed_layer], table
                
            except Exception as e:
                print(f"Error getting watershed data: {e}")
                return [], html.P(f"Error getting watershed data: {str(e)}", className="text-red-500")
        
        return [], html.Div("Click 'Get Watershed Info' to retrieve watershed data.")


