import osmnx as ox
import geopandas as gpd
from dash import Dash, dcc, html, Input, Output, State, callback_context, no_update
import dash_leaflet as dl
from dash import dash_table
import json
import streamstats
import pandas as pd 

# Initialize the app
# Use suppress_callback_exceptions=True to allow the new separated structure to work seamlessly
app = Dash(__name__, suppress_callback_exceptions=True) 
app.title = "Stream Explorer Dashboard"

# Global variables
df = pd.DataFrame()  # Global DataFrame for watershed parameters

# --- Utility Functions (Kept as provided) ---

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

# Current coordinates state
current_lat = 38.58 # Defaulting to Sacramento, CA
current_lon = -121.49

# --- App Layout ---
def create_layout():
    layout = html.Div(className="container mx-auto p-4 font-sans", children=[
        html.H1("StreamStat Explorer Dashboard", style={'textAlign': 'center', 'color': '#1E3A8A', 'marginBottom': '20px'}),
        
        html.Div(className="flex flex-col lg:flex-row gap-4", children=[
            
            # Instructions Panel
            html.Div(className="lg:w-1/4 p-4 bg-gray-50 rounded-lg shadow-md", children=[
                html.H3("Instructions", className="text-xl font-semibold mb-3 text-gray-700"),
                html.P("1. Click anywhere on the map to select a point.", className="mb-2"),          
                html.P("2. Click 'Find Streams' to search around selected point (10 mi radius).", className="mb-2"),
                html.P("3. Adjust the red marker to be very close to a point.", className="mb-2"),
                html.P("3. Click 'Get Stream and Watershed Info' to get the stream and watershed info.", className="mb-2"),
                
                
            ]),
            
            # Map and Controls Panel
            html.Div(className="lg:w-3/4", children=[
                
                # Controls
                html.Div(className="flex flex-wrap items-center gap-4 mb-4 p-3 bg-white rounded-lg shadow-md", children=[
                    html.Label("Latitude:", className="font-medium"),
                    dcc.Input(id='lat-input', type='number', value=current_lat, step=0.0001, className="border p-2 rounded w-32"),
                    html.Label("Longitude:", className="font-medium"),
                    dcc.Input(id='lon-input', type='number', value=current_lon, step=0.0001, className="border p-2 rounded w-32"),
                    html.Button('Find Streams', id='find-streams-btn', n_clicks=0, 
                                className="bg-blue-600 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded transition duration-300 shadow-lg"),
                    html.Button('Get Stream and Watershed Info', id='get-combined-info-btn', n_clicks=0, 
                                className="bg-purple-600 hover:bg-purple-700 text-white font-bold py-2 px-4 rounded transition duration-300 shadow-lg"),
                ]),
                
                # Map component
                dl.Map(
                    center=[current_lat, current_lon],
                    zoom=10,
                    children=[
                        dl.TileLayer(url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"),
                        dl.LayerGroup(id="marker-layer"),
                        dl.LayerGroup(id="streams-layer"),
                    ],
                    style={'width': '100%', 'height': '600px', 'borderRadius': '8px', 'boxShadow': '0 4px 6px rgba(0, 0, 0, 0.1)'},
                    id="map"
                ),
                
                # Debug info (hidden)
                html.Div(id='debug-info', style={'display': 'none'}),
                
                # Data table below the map
                html.Div(className="mt-6", children=[
                    html.H3("Data Table", className="text-xl font-semibold mb-3 text-gray-700"),
                    html.Div(id='data-table', 
                            className="bg-white rounded-lg shadow-md p-4",
                            children=[
                                html.P("Click on the map and use the buttons above to populate data here.", 
                                    className="text-gray-500 italic")
                            ]),
                    
                    # DataFrame table
                    html.Div(className="mt-4", children=[
                        html.H4("Watershed Parameters DataFrame", className="text-lg font-semibold mb-3 text-gray-700"),
                        html.Div(id='dataframe-table', 
                                className="bg-white rounded-lg shadow-md p-4",
                                children=[
                                    html.P("No data available. Click 'Find Watershed' to populate the table.", 
                                        className="text-gray-500 italic")
                                ])
                    ])
                ])
            ])
        ])
    ])
    return layout

# --- Callbacks ---

# 1. NEW CALLBACK: Handles only map clicks to update coordinates
@app.callback(
    [Output('lat-input', 'value'),
     Output('lon-input', 'value'),
     Output('debug-info', 'children')],
    [Input('map', 'clickData')]
)
def update_coordinates_on_click(clickData):
    print(f"Callback triggered with: {clickData}")  # Debug print
    
    if clickData is None:
        # Return default values on initial load
        return 38.58, -121.49, "Map ready - click to update coordinates"
    
    # Extract coordinates from clickData
    lat = clickData['latlng']['lat']
    lon = clickData['latlng']['lng']
    
    # Return the new coordinates directly to the input fields
    return lat, lon, f"Map Click Coordinates: {lat:.4f}, {lon:.4f}"

# 2. NEW CALLBACK: Handles marker and map center updates based on input fields.
# This ensures the marker moves when the map is clicked (triggering Callback 1) 
# OR when the user manually enters coordinates.
@app.callback(
    [Output('marker-layer', 'children'),
     Output('map', 'center')],
    [Input('lat-input', 'value'),
     Input('lon-input', 'value')]
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


# 3. ORIGINAL CALLBACK: Remains separate for stream search logic
@app.callback(
    Output('streams-layer', 'children'),
    [Input('find-streams-btn', 'n_clicks')],
    [State('lat-input', 'value'),
     State('lon-input', 'value')]
)
def update_streams(n_clicks, lat, lon):
    if n_clicks > 0 and lat is not None and lon is not None:
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



# 6. NEW CALLBACK: Combined streams and watershed info
@app.callback(
    [Output('streams-layer', 'children', allow_duplicate=True),
     Output('dataframe-table', 'children', allow_duplicate=True)],
    [Input('get-combined-info-btn', 'n_clicks')],
    [State('lat-input', 'value'),
     State('lon-input', 'value')],
    prevent_initial_call=True
)
def get_combined_info(n_clicks, lat, lon):
    global df  # Access the global df variable
    
    if n_clicks > 0 and lat is not None and lon is not None:
        print(f"Getting combined streams and watershed info for: {lat}, {lon}")
        
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
            
            # Update global DataFrame
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


# Set up the app layout
app.layout = create_layout()

if __name__ == "__main__":
    app.run(debug=True)
