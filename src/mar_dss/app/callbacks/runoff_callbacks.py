"""
Callbacks for the Runoff Calculator tab.
"""
import os
import dash
from dash import Input, Output, html, no_update, State, dcc
import dash_bootstrap_components as dbc
import dash_leaflet as dl
import pandas as pd
import osmnx as ox
import geopandas as gpd
import streamstats
import json
from dash import dash_table
from mar_dss.pfdf.data.noaa.atlas14 import download
import requests
import numpy as np
import plotly.graph_objects as go
from scipy.special import exp1


try:
    from mar_dss.app.components.runoff_calculator_tab import create_runoff_map
except ImportError:
    from ..components.runoff_calculator_tab import create_runoff_map
df = pd.DataFrame()


    
def get_monthly_rain(latitude, longitude):
    START_YEAR = 1981
    END_YEAR = 2021 
    API_URL = "https://power.larc.nasa.gov/api/temporal/climatology/point"
    PARAMETERS = "PRECTOTCORR"
    COMMUNITY = "AG"  # Agroclimatology community, provides standard units (mm/day)
    TIME_FRAME = "ANNUAL"

    # 2. Construct the API call URL
    payload = {
        'parameters': PARAMETERS,
        'community': COMMUNITY,
        'latitude': latitude,
        'longitude': longitude,
        'start': START_YEAR,
        'end': END_YEAR,
        'format': 'JSON'
    }

    # 3. Make the API request
    try:
        response = requests.get(API_URL, params=payload, timeout=10)
        response.raise_for_status() # Raise an HTTPError for bad responses (4xx or 5xx)
        data = response.json()        
        all_data = list(data['properties']['parameter']['PRECTOTCORR'].values())
        annual_data = all_data[-1]*365.25/25.4
        monthly_data = np.array(all_data[0:12]) * 30.4375/25.4
        df = pd.DataFrame(columns=['Month', 'Rain (inches)'])
        df['Month'] = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
        df['Rain (inches)'] = monthly_data

        return df       

    except requests.exceptions.RequestException as e:
        print(f"Error fetching data: {e}")
    except KeyError:
        print("Error: Could not find the expected data structure in the API response. The parameter or time frame might be incorrect.")

def get_rain_data(lat, lon):
    """Get rain data from NOAA Atlas 14 and return as DataFrame."""
    file_path = download(lat=lat, lon=lon, units='english', data='depth', overwrite=True)
    fidr = open(file_path, 'r')
    lines = fidr.readlines()
    fidr.close()

    # remove the file
    os.remove(file_path)

    readdata = False
    readheader = False
    data = []
    for line in lines:
        if "PRECIPITATION FREQUENCY ESTIMATES" in line:
            readdata = True
            readheader = True
            continue
        
        if readdata:
            if readheader:
                header = [hval.strip() for hval in line.split(',')]
                readheader = False
                continue
            parts = line.split(',')
            duration = parts[0]
            if duration.strip() == '':
                break
            frequency = [float(fval) for fval in parts[1:]]
            record = [duration] + frequency
            data.append(record)
    df_rain = pd.DataFrame(data, columns=header)
    return df_rain

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
    
    # Client-side callback to resize map when tab becomes active
    app.clientside_callback(
        """
        function(activeTab) {
            if (activeTab === "rainfall-watershed-tab") {
                setTimeout(function() {
                    try {
                        window.dispatchEvent(new Event("resize"));
                    } catch (e) {
                        var evt = document.createEvent("UIEvents");
                        evt.initUIEvent("resize", true, false, window, 0);
                        window.dispatchEvent(evt);
                    }
                }, 100);
            }
            return window.dash_clientside.no_update;
        }
        """,
        Output("runoff-map", "id", allow_duplicate=True),  # dummy output
        Input("runoff-calculator-tabs", "active_tab"),
        prevent_initial_call=True,
    )

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

    # Callback 3: Handle "Obtain nearby streams" button with working message
    @app.callback(
        [Output('stations-layer', 'children'),
         Output('status-message', 'children')],
        [Input('obtain-streams-btn', 'n_clicks')],
        [State('selected-latitude', 'value'),
         State('selected-longitude', 'value')],
        prevent_initial_call=True
    )
    def update_streams(n_clicks, lat, lon):
        if n_clicks and n_clicks > 0 and lat is not None and lon is not None:
            print(f"Searching streams for: {lat}, {lon}")
            
            # Show working message first
            working_msg = html.Div("Working on obtaining nearby streams...", 
                                  className="alert alert-info", role="alert")
            
            # The distance is set in the function call to 16093 meters (approx 10 miles)
            streams = get_streams_near_point(lat, lon) 
            geojson_data = streams_to_geojson(streams)
            
            if geojson_data and 'features' in geojson_data and len(geojson_data['features']) > 0:
                # Show completion message
                done_msg = html.Div("Done!", className="alert alert-success", role="alert")
                return [dl.GeoJSON(
                    data=geojson_data, 
                    style={'color': 'blue', 'weight': 3, 'opacity': 0.8}
                )], done_msg
            else:
                # Show completion message even if no streams found
                done_msg = html.Div("Done! (No streams found)", className="alert alert-warning", role="alert")
                return [], done_msg
        
        return [], html.Div("")

    # Callback 4: Handle "Get Watershed Info" button with working message
    @app.callback(
        [Output('watershed-layer', 'children'),
         Output('watershed-info-content', 'children'),
         Output('rain-info-content', 'children'),
         Output('status-message', 'children', allow_duplicate=True)],
        [Input('get-watershed-btn', 'n_clicks')],
        [State('selected-latitude', 'value'),
         State('selected-longitude', 'value')],
        prevent_initial_call=True
    )
    def get_watershed_info(n_clicks, lat, lon):
        if n_clicks and n_clicks > 0 and lat is not None and lon is not None:
            print(f"Getting watershed info for: {lat}, {lon}")
            
            # Show working message first
            working_msg = html.Div("Working on obtaining watershed info...", 
                                  className="alert alert-info", role="alert")
            
            # Get rain data
            df_rain = None
            monthly_rain = None
            rain_table = None
            monthly_rain_content = None
            try:
                df_rain = get_rain_data(lat, lon)
            except Exception as e:
                print(f"Error getting rain data: {e}")
            try:
                monthly_rain = get_monthly_rain(lat, lon)
            except Exception as e:
                print(f"Error getting monthly rain data: {e}")
                monthly_rain_content = html.P(f"Error getting monthly rain data: {str(e)}", className="text-danger")
            # Get watershed data for the map
            try:
                ws = streamstats.Watershed(lat=lat, lon=lon)
                watershed_geojson = ws.boundary
                print(f"Watershed parameters count: {len(ws.parameters)}")
                print(f"Watershed parameters: {ws.parameters}")
                
                df_data = []
                for par in ws.parameters:
                    name = par['name']
                    description = par['description']
                    code = par['code']
                    unit = par['unit'] 
                    value = par['value']
                    print(f"Parameter: {name} = {value} {unit}")
                    df_data.append([name, description, code, unit, value])
                
                # Create DataFrame
                df = pd.DataFrame(df_data, columns=['Name', 'Description', 'Code', 'Unit', 'Value'])
                print(f"DataFrame created with {len(df)} rows")
                print(f"DataFrame columns: {df.columns.tolist()}")
                print(f"DataFrame data: {df.to_dict('records')}")
                
                # Create watershed layer for the map
                watershed_layer = dl.GeoJSON(
                    data=watershed_geojson, 
                    style={'color': 'red', 'weight': 3, 'opacity': 0.8, 'fillOpacity': 0.2}
                )
                
                # Generate watershed table with error handling
                try:
                    if df.empty:
                        print("Watershed DataFrame is empty!")
                        watershed_table = html.P("No watershed parameters available.", className="text-warning")
                    else:
                        watershed_table = dash_table.DataTable(
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
                            page_size=len(df),  # Show all rows on one page
                            sort_action="native",
                            filter_action="native",
                            export_format="csv"
                        )
                except Exception as table_error:
                    print(f"Error creating watershed table: {table_error}")
                    watershed_table = html.P(f"Error creating table: {str(table_error)}", className="text-danger")
                
                # Generate monthly rain content (table and chart) with error handling
                if monthly_rain_content is None:
                    try:
                        if monthly_rain is None or monthly_rain.empty:
                            print("Monthly rain DataFrame is empty or None!")
                            monthly_rain_content = html.P("No monthly rain data available.", className="text-warning")
                        else:
                            # Create monthly rain table
                            monthly_rain_table = dash_table.DataTable(
                                data=monthly_rain.to_dict('records'),
                                columns=[{"name": i, "id": i} for i in monthly_rain.columns],
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
                                page_size=len(monthly_rain),
                                sort_action="native",
                                filter_action="native",
                                export_format="csv"
                            )
                            
                            # Create bar chart for monthly rain
                            fig = go.Figure(data=[
                                go.Bar(
                                    x=monthly_rain['Month'],
                                    y=monthly_rain['Rain (inches)'],
                                    marker_color='steelblue',
                                    text=monthly_rain['Rain (inches)'].round(2),
                                    textposition='outside'
                                )
                            ])
                            fig.update_layout(
                                title='Monthly Average Precipitation',
                                xaxis_title='Month',
                                yaxis_title='Rain (inches)',
                                xaxis={'tickangle': -45},
                                height=400,
                                margin=dict(l=50, r=50, t=50, b=100)
                            )
                            monthly_rain_chart = dcc.Graph(figure=fig)
                            
                            # Create card with table and chart side by side
                            monthly_rain_content = dbc.Card([
                                dbc.CardHeader("Monthly Average Precipitation", className="fw-bold bg-primary text-white"),
                                dbc.CardBody([
                                    dbc.Row([
                                        dbc.Col([monthly_rain_table], width=6),
                                        dbc.Col([monthly_rain_chart], width=6)
                                    ])
                                ])
                            ], className="mb-4")
                    except Exception as monthly_error:
                        print(f"Error creating monthly rain content: {monthly_error}")
                        monthly_rain_content = html.P(f"Error creating monthly rain content: {str(monthly_error)}", className="text-danger")
                
                # Generate precipitation frequency table (df_rain) with error handling
                try:
                    if df_rain is None or df_rain.empty:
                        print("Rain DataFrame is empty or None!")
                        df_rain_table = html.P("No precipitation frequency data available.", className="text-warning")
                    else:
                        df_rain_table = dash_table.DataTable(
                            data=df_rain.to_dict('records'),
                            columns=[{"name": i, "id": i} for i in df_rain.columns],
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
                            page_size=len(df_rain),  # Show all rows on one page
                            sort_action="native",
                            filter_action="native",
                            export_format="csv"
                        )
                except Exception as rain_table_error:
                    print(f"Error creating rain table: {rain_table_error}")
                    df_rain_table = html.P(f"Error creating rain table: {str(rain_table_error)}", className="text-danger")
                
                # Create card for precipitation frequency table
                df_rain_card = dbc.Card([
                    dbc.CardHeader("Precipitation Frequency Estimates (NOAA Atlas 14)", className="fw-bold bg-primary text-white"),
                    dbc.CardBody([
                        df_rain_table
                    ])
                ])
                
                # Combine monthly rain content and df_rain card
                rain_info_content = html.Div([
                    monthly_rain_content if monthly_rain_content else html.P("No monthly rain data available.", className="text-warning"),
                    df_rain_card
                ])
                
                print(f"Watershed table generated with {len(df)} rows")
                if df_rain is not None:
                    print(f"Rain table generated with {len(df_rain)} rows")
                if monthly_rain is not None:
                    print(f"Monthly rain table generated with {len(monthly_rain)} rows")
                
                # Show completion message
                done_msg = html.Div("Done!", className="alert alert-success", role="alert")
                return [watershed_layer], watershed_table, rain_info_content, done_msg
                
            except Exception as e:
                print(f"Error getting watershed data: {e}")
                error_msg = html.Div("Error getting watershed data", className="alert alert-danger", role="alert")
                # Create default rain info content
                default_rain_content = html.Div([
                    html.P("No data available.", className="text-warning")
                ])
                return [], html.P(f"Error getting watershed data: {str(e)}", className="text-danger"), default_rain_content, error_msg
        
        default_rain_content = html.Div([
            html.P("Click 'Get Watershed Info' to retrieve rain data.", className="text-muted")
        ])
        return [], html.Div("Click 'Get Watershed Info' to retrieve watershed data."), default_rain_content, html.Div("")

    # Callback for impervious curve number selection
    @app.callback(
        Output('selected-impervious-curve-number-display', 'children'),
        Input('impervious-curve-number-select', 'value')
    )
    def update_impervious_curve_number_display(selected_value):
        """Display the selected impervious curve number information."""
        if not selected_value:
            return html.Div("Please select a surface condition.", className="text-muted")
        
        # Map values to curve numbers
        curve_number_map = {
            "concrete_fresh": {"surface": "Concrete", "condition": "Fresh/Uncracked", "cn": 99},
            "concrete_weathered": {"surface": "Concrete", "condition": "Weathered/Cracked", "cn": 97},
            "asphalt_fresh": {"surface": "Asphalt", "condition": "Fresh/Uncracked", "cn": 99},
            "asphalt_weathered": {"surface": "Asphalt", "condition": "Weathered/Cracked", "cn": 97},
        }
        
        info = curve_number_map.get(selected_value)
        if info:
            return dbc.Alert([
                html.H5("Selected Surface Condition:", className="mb-2"),
                html.P([
                    html.Strong("Surface: "), info["surface"], html.Br(),
                    html.Strong("Condition: "), info["condition"], html.Br(),
                    html.Strong("Curve Number (CN): "), html.Span(str(info["cn"]), className="text-primary fw-bold fs-4")
                ], className="mb-0")
            ], color="info")
        
        return html.Div("Invalid selection.", className="text-danger")

    # Callback for curve number selection based on cover description and soil type
    @app.callback(
        Output('selected-curve-number-display', 'children'),
        [Input('cover-description-select', 'value'),
         Input('soil-type-select', 'value')]
    )
    def update_curve_number_display(cover_description, soil_type):
        """Display the selected curve number based on cover description and soil type."""
        if not cover_description or not soil_type:
            return html.Div("Please select both Cover Description and Hydrologic Soil Type.", className="text-muted")
        
        # Curve number lookup table
        # Structure: {cover_description: {soil_type: curve_number}}
        curve_number_table = {
            "open_space_poor": {
                "type_a": 56,
                "type_b": 70,
                "type_c": 79,
                "type_d": 84
            },
            "open_space_fair": {
                "type_a": 36,
                "type_b": 57,
                "type_c": 70,
                "type_d": 77
            },
            "open_space_good": {
                "type_a": 26,
                "type_b": 48,
                "type_c": 64,
                "type_d": 71
            },
            "natural_desert": {
                "type_a": 50,
                "type_b": 67,
                "type_c": 78,
                "type_d": 82
            },
            "developing_urban": {
                "type_a": 67,
                "type_b": 79,
                "type_c": 87,
                "type_d": 91
            }
        }
        
        # Cover description labels
        cover_labels = {
            "open_space_poor": "Open Space - Poor Condition",
            "open_space_fair": "Open Space - Fair Condition",
            "open_space_good": "Open Space - Good Condition",
            "natural_desert": "Natural Desert Landscaping (pervious areas only)",
            "developing_urban": "Developing Urban Areas - Newly Graded Areas"
        }
        
        # Soil type labels
        soil_labels = {
            "type_a": "Hydrologic Soil Type A",
            "type_b": "Hydrologic Soil Type B",
            "type_c": "Hydrologic Soil Type C",
            "type_d": "Hydrologic Soil Type D"
        }
        
        # Get curve number
        cn = curve_number_table.get(cover_description, {}).get(soil_type)
        
        if cn is not None:
            return dbc.Alert([
                html.H5("Selected Curve Number:", className="mb-2"),
                html.P([
                    html.Strong("Cover Description: "), cover_labels.get(cover_description, cover_description), html.Br(),
                    html.Strong("Soil Type: "), soil_labels.get(soil_type, soil_type), html.Br(),
                    html.Hr(className="my-2"),
                    html.Strong("Curve Number (CN): "), html.Span(str(cn), className="text-primary fw-bold fs-3")
                ], className="mb-0")
            ], color="info")
        
        return html.Div("Invalid selection combination.", className="text-danger")

    # Callback for composite CN table based on 1A/1B selection
    @app.callback(
        [Output('composite-cn-table', 'children'),
         Output('composite-cn-table-store', 'data')],
        [Input('impervious-outlet-option', 'value'),
         Input('impervious-curve-number-select', 'value'),
         Input('cover-description-select', 'value'),
         Input('soil-type-select', 'value')]
    )
    def update_composite_cn_table(selected_option, impervious_cn_selection, cover_description, soil_type):
        """Update the composite CN table based on 1A or 1B selection."""
        if not selected_option:
            return html.Div("Please select an option (1A or 1B).", className="text-muted"), None
        
        # Get CN impervious value from the impervious curve number selection
        cn_impervious_map = {
            "concrete_fresh": 99,
            "concrete_weathered": 97,
            "asphalt_fresh": 99,
            "asphalt_weathered": 97
        }
        cn_impervious = cn_impervious_map.get(impervious_cn_selection, 50)  # Default to 50 if not selected
        
        # Get CN pervious value from the cover description and soil type selection
        curve_number_table = {
            "open_space_poor": {
                "type_a": 56,
                "type_b": 70,
                "type_c": 79,
                "type_d": 84
            },
            "open_space_fair": {
                "type_a": 36,
                "type_b": 57,
                "type_c": 70,
                "type_d": 77
            },
            "open_space_good": {
                "type_a": 26,
                "type_b": 48,
                "type_c": 64,
                "type_d": 71
            },
            "natural_desert": {
                "type_a": 50,
                "type_b": 67,
                "type_c": 78,
                "type_d": 82
            },
            "developing_urban": {
                "type_a": 67,
                "type_b": 79,
                "type_c": 87,
                "type_d": 91
            }
        }
        cn_pervious = curve_number_table.get(cover_description, {}).get(soil_type, 50)  # Default to 50 if not selected
        
        if selected_option == "1A":
            # Table data for 1A
            table_data = [
                {"Parameter": "CN impervious", "Value": cn_impervious},
                {"Parameter": "CN pervious", "Value": cn_pervious},
                {"Parameter": "Connected Impervious Area %", "Value": 20},
                {"Parameter": "Composite CN", "Value": 50}
            ]
        elif selected_option == "1B":
            # Table data for 1B
            table_data = [
                {"Parameter": "CN impervious", "Value": cn_impervious},
                {"Parameter": "CN pervious", "Value": cn_pervious},
                {"Parameter": "Total Impervious Area %", "Value": 20},
                {"Parameter": "R %", "Value": 1},
                {"Parameter": "Composite CN", "Value": 0}
            ]
        else:
            return html.Div("Invalid option selected.", className="text-danger")
        
        if table_data:
            # Compute Composite CN based on the formula
            if selected_option == "1A":
                # Formula: ((M11*M13)+(M12*(100-M13)))/100
                # M11: CN impervious, M12: CN pervious, M13: Connected Impervious Area %
                try:
                    m11 = float(table_data[0]["Value"]) if table_data[0]["Value"] != "" else 0
                    m12 = float(table_data[1]["Value"]) if table_data[1]["Value"] != "" else 0
                    m13 = float(table_data[2]["Value"]) if table_data[2]["Value"] != "" else 0
                    composite_cn = ((m11 * m13) + (m12 * (100 - m13))) / 100
                    table_data[3]["Value"] = round(composite_cn, 2)
                except (ValueError, TypeError, IndexError):
                    table_data[3]["Value"] = 0
            elif selected_option == "1B":
                # Formula: (((P11*P13)+(P12*(100-P13)))/100)-(((P14/100)*P13*((((P11*P13)+(P12*(100-P13)))/100)-P12))/100)
                # P11: CN impervious, P12: CN pervious, P13: Total Impervious Area %, P14: R %
                try:
                    p11 = float(table_data[0]["Value"]) if table_data[0]["Value"] != "" else 0
                    p12 = float(table_data[1]["Value"]) if table_data[1]["Value"] != "" else 0
                    # Use default values of 20 and 1 if empty
                    p13 = float(table_data[2]["Value"]) if table_data[2]["Value"] != "" else 20
                    p14 = float(table_data[3]["Value"]) if table_data[3]["Value"] != "" else 1
                    # First part: ((P11*P13)+(P12*(100-P13)))/100
                    first_part = ((p11 * p13) + (p12 * (100 - p13))) / 100
                    # Second part: ((P14/100)*P13*((((P11*P13)+(P12*(100-P13)))/100)-P12))/100
                    second_part = ((p14 / 100) * p13 * (first_part - p12)) / 100
                    composite_cn = first_part - second_part
                    table_data[4]["Value"] = round(composite_cn, 2)
                except (ValueError, TypeError, IndexError):
                    table_data[4]["Value"] = 0
            
            # Create the DataTable to display in the div
            table = dash_table.DataTable(
                id="composite-cn-datatable",
                data=table_data,
                columns=[
                    {"name": "Parameter", "id": "Parameter", "editable": False},
                    {"name": "Value", "id": "Value", "editable": True, "type": "numeric"}
                ],
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
                    },
                    {
                        'if': {'row_index': 3 if selected_option == "1A" else 4},
                        'backgroundColor': '#e3f2fd',
                        'fontWeight': 'bold'
                    }
                ]
            )
            return table, table_data
        
        return html.Div("No data available for this option.", className="text-warning"), None

    # Callback to recompute Composite CN when table values are edited
    @app.callback(
        [Output('composite-cn-table', 'children', allow_duplicate=True),
         Output('composite-cn-table-store', 'data', allow_duplicate=True)],
        [Input('composite-cn-datatable', 'data'),
         Input('impervious-outlet-option', 'value')],
        prevent_initial_call=True
    )
    def recompute_composite_cn_from_table(table_data, selected_option):
        """Recompute Composite CN when any table value is edited."""
        if not table_data or not selected_option:
            return dash.no_update, dash.no_update
        
        # Make a copy to avoid modifying the original
        updated_data = [row.copy() for row in table_data]
        
        # Compute Composite CN based on the formula
        if selected_option == "1A":
            # Formula: ((M11*M13)+(M12*(100-M13)))/100
            try:
                m11 = float(updated_data[0]["Value"]) if updated_data[0]["Value"] != "" else 0
                m12 = float(updated_data[1]["Value"]) if updated_data[1]["Value"] != "" else 0
                m13 = float(updated_data[2]["Value"]) if updated_data[2]["Value"] != "" else 0
                composite_cn = ((m11 * m13) + (m12 * (100 - m13))) / 100
                updated_data[3]["Value"] = round(composite_cn, 2)
            except (ValueError, TypeError, IndexError):
                updated_data[3]["Value"] = 0
        elif selected_option == "1B":
            # Formula: (((P11*P13)+(P12*(100-P13)))/100)-(((P14/100)*P13*((((P11*P13)+(P12*(100-P13)))/100)-P12))/100)
            try:
                p11 = float(updated_data[0]["Value"]) if updated_data[0]["Value"] != "" else 0
                p12 = float(updated_data[1]["Value"]) if updated_data[1]["Value"] != "" else 0
                p13 = float(updated_data[2]["Value"]) if updated_data[2]["Value"] != "" else 20
                p14 = float(updated_data[3]["Value"]) if updated_data[3]["Value"] != "" else 1
                first_part = ((p11 * p13) + (p12 * (100 - p13))) / 100
                second_part = ((p14 / 100) * p13 * (first_part - p12)) / 100
                composite_cn = first_part - second_part
                updated_data[4]["Value"] = round(composite_cn, 2)
            except (ValueError, TypeError, IndexError):
                updated_data[4]["Value"] = 0
        
        # Update the table display
        table = dash_table.DataTable(
            id="composite-cn-datatable",
            data=updated_data,
            columns=[
                {"name": "Parameter", "id": "Parameter", "editable": False},
                {"name": "Value", "id": "Value", "editable": True, "type": "numeric"}
            ],
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
                },
                {
                    'if': {'row_index': 3 if selected_option == "1A" else 4},
                    'backgroundColor': '#e3f2fd',
                    'fontWeight': 'bold'
                }
            ]
        )
        
        return table, updated_data
    
    # Callback to sync Composite CN to runoff calculations table
    @app.callback(
        Output('runoff-calculations-table', 'data'),
        [Input('composite-cn-table-store', 'data'),
         Input('runoff-calculations-table', 'data')],
        [State('runoff-calculations-table', 'data')],
        prevent_initial_call=False
    )
    def sync_composite_cn_to_runoff_table(cn_store_data, table_data_trigger, current_table_data):
        """Sync Composite CN value to runoff calculations table."""
        ctx = dash.callback_context
        if not ctx.triggered:
            # Initial load - use default data
            return current_table_data if current_table_data else [
                {"Parameter": "Area (acres)", "Value": 10},
                {"Parameter": "Composite Curve Number", "Value": 50},
                {"Parameter": "24-hour Rainfall (inches)", "Value": 5},
                {"Parameter": "Maximum Potential Storage (inches)", "Value": 10},
                {"Parameter": "Initial Abstraction", "Value": 0.05},
                {"Parameter": "Runoff Depth (inches)", "Value": 1},
                {"Parameter": "Runoff/Precipitation Ratio", "Value": 0.2},
                {"Parameter": "Runoff Volume (ft3)", "Value": 10000}
            ]
        
        trigger_id = ctx.triggered[0]["prop_id"].split(".")[0]
        
        # If Composite CN store was updated, update the runoff table
        if trigger_id == "composite-cn-table-store" and cn_store_data:
            # Find Composite CN value
            composite_cn = None
            for row in cn_store_data:
                if row.get("Parameter") == "Composite CN":
                    try:
                        composite_cn = float(row.get("Value", 0))
                    except (ValueError, TypeError):
                        pass
                    break
            
            if composite_cn is not None:
                # Calculate Maximum Potential Storage: (1000/D6) - 10 where D6 is Composite Curve Number
                max_potential_storage = (1000 / composite_cn) - 10 if composite_cn > 0 else 0
                
                # Get current table data or use defaults
                if current_table_data:
                    updated_data = [row.copy() for row in current_table_data]
                else:
                    updated_data = [
                        {"Parameter": "Area (acres)", "Value": 10},
                        {"Parameter": "Composite Curve Number", "Value": composite_cn},
                        {"Parameter": "24-hour Rainfall (inches)", "Value": 5},
                        {"Parameter": "Maximum Potential Storage (inches)", "Value": max_potential_storage},
                        {"Parameter": "Initial Abstraction", "Value": 0.05},
                        {"Parameter": "Runoff Depth (inches)", "Value": 1},
                        {"Parameter": "Runoff/Precipitation Ratio", "Value": 0.2},
                        {"Parameter": "Runoff Volume (ft3)", "Value": 10000}
                    ]
                
                # Get current values for Runoff Depth calculation
                rainfall = 5  # default
                initial_abstraction = 0.05  # default
                for row in updated_data:
                    if row.get("Parameter") == "24-hour Rainfall (inches)":
                        try:
                            rainfall = float(row.get("Value", 5))
                        except (ValueError, TypeError):
                            rainfall = 5
                    elif row.get("Parameter") == "Initial Abstraction":
                        try:
                            initial_abstraction = float(row.get("Value", 0.05))
                        except (ValueError, TypeError):
                            initial_abstraction = 0.05
                
                # Calculate Runoff Depth: ((D7 - (D19 * D18))^2) / (D7 + ((1 - D19) * D18))
                # D7: 24-hour Rainfall, D19: Initial Abstraction, D18: Maximum Potential Storage
                numerator = (rainfall - (initial_abstraction * max_potential_storage)) ** 2
                denominator = rainfall + ((1 - initial_abstraction) * max_potential_storage)
                runoff_depth = numerator / denominator if denominator > 0 else 0
                
                # Calculate Runoff/Precipitation Ratio: D20 / D7
                # D20: Runoff Depth, D7: 24-hour Rainfall
                runoff_precip_ratio = runoff_depth / rainfall if rainfall > 0 else 0
                
                # Get Area value for Runoff Volume calculation
                area = 10  # default
                for row in updated_data:
                    if row.get("Parameter") == "Area (acres)":
                        try:
                            area = float(row.get("Value", 10))
                        except (ValueError, TypeError):
                            area = 10
                        break
                
                # Calculate Runoff Volume: D20 * (D5 * 43560 / 12)
                # D5: Area (acres), D20: Runoff Depth (inches)
                runoff_volume = runoff_depth * (area * 43560 / 12)
                
                # Update the Composite Curve Number, Maximum Potential Storage, Runoff Depth, Runoff/Precipitation Ratio, and Runoff Volume values
                for row in updated_data:
                    if row.get("Parameter") == "Composite Curve Number":
                        row["Value"] = composite_cn
                    elif row.get("Parameter") == "Maximum Potential Storage (inches)":
                        row["Value"] = round(max_potential_storage, 2)
                    elif row.get("Parameter") == "Runoff Depth (inches)":
                        row["Value"] = round(runoff_depth, 2)
                    elif row.get("Parameter") == "Runoff/Precipitation Ratio":
                        row["Value"] = round(runoff_precip_ratio, 2)
                    elif row.get("Parameter") == "Runoff Volume (ft3)":
                        row["Value"] = round(runoff_volume, 2)
                return updated_data
        
        # If table data was edited, check for changes and recalculate dependent values
        if trigger_id == "runoff-calculations-table" and current_table_data:
            updated_data = [row.copy() for row in current_table_data]
            
            # Extract current values from the table
            composite_cn = None
            rainfall = None
            max_potential_storage = None
            initial_abstraction = None
            runoff_depth = None
            area = None
            
            for row in updated_data:
                param = row.get("Parameter")
                try:
                    value = float(row.get("Value", 0))
                    if param == "Composite Curve Number":
                        composite_cn = value
                    elif param == "24-hour Rainfall (inches)":
                        rainfall = value
                    elif param == "Maximum Potential Storage (inches)":
                        max_potential_storage = value
                    elif param == "Initial Abstraction":
                        initial_abstraction = value
                    elif param == "Runoff Depth (inches)":
                        runoff_depth = value
                    elif param == "Area (acres)":
                        area = value
                except (ValueError, TypeError):
                    pass
            
            # If Composite Curve Number was edited, recalculate Maximum Potential Storage
            if composite_cn is not None and composite_cn > 0:
                new_max_storage = (1000 / composite_cn) - 10
                for row in updated_data:
                    if row.get("Parameter") == "Maximum Potential Storage (inches)":
                        row["Value"] = round(new_max_storage, 2)
                        max_potential_storage = new_max_storage
                        break
            
            # Recalculate Runoff Depth if any of the required values are available
            # Formula: ((D7 - (D19 * D18))^2) / (D7 + ((1 - D19) * D18))
            # D7: 24-hour Rainfall, D19: Initial Abstraction, D18: Maximum Potential Storage
            if rainfall is not None and initial_abstraction is not None and max_potential_storage is not None:
                numerator = (rainfall - (initial_abstraction * max_potential_storage)) ** 2
                denominator = rainfall + ((1 - initial_abstraction) * max_potential_storage)
                runoff_depth = numerator / denominator if denominator > 0 else 0
                
                # Update Runoff Depth in the table
                for row in updated_data:
                    if row.get("Parameter") == "Runoff Depth (inches)":
                        row["Value"] = round(runoff_depth, 2)
                        break
            
            # Recalculate Runoff/Precipitation Ratio: D20 / D7
            # D20: Runoff Depth, D7: 24-hour Rainfall
            if runoff_depth is not None and rainfall is not None and rainfall > 0:
                runoff_precip_ratio = runoff_depth / rainfall
                
                # Update Runoff/Precipitation Ratio in the table
                for row in updated_data:
                    if row.get("Parameter") == "Runoff/Precipitation Ratio":
                        row["Value"] = round(runoff_precip_ratio, 2)
                        break
            
            # Recalculate Runoff Volume: D20 * (D5 * 43560 / 12)
            # D5: Area (acres), D20: Runoff Depth (inches)
            if runoff_depth is not None and area is not None:
                runoff_volume = runoff_depth * (area * 43560 / 12)
                
                # Update Runoff Volume in the table
                for row in updated_data:
                    if row.get("Parameter") == "Runoff Volume (ft3)":
                        row["Value"] = round(runoff_volume, 2)
                        break
            
            return updated_data
        
        return current_table_data if current_table_data else dash.no_update

    # Callback for "Download Rain Statistics" button in Runoff for Single Storm card
    @app.callback(
        Output('rain-statistics-table-placeholder', 'children'),
        Input('download-rain-statistics-btn', 'n_clicks'),
        [State('runoff-single-storm-latitude', 'value'),
         State('runoff-single-storm-longitude', 'value')],
        prevent_initial_call=True
    )
    def download_rain_statistics(n_clicks, lat, lon):
        """Download rain statistics and display as table side by side with runoff calculations table."""
        if n_clicks and n_clicks > 0 and lat is not None and lon is not None:
            try:
                # Get rain data
                df_rain = get_rain_data(lat, lon)
                
                if df_rain is None or df_rain.empty:
                    return html.P("No rain statistics data available.", className="text-warning")
                
                # Create rain statistics table
                rain_statistics_table = dash_table.DataTable(
                    data=df_rain.to_dict('records'),
                    columns=[{"name": i, "id": i} for i in df_rain.columns],
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
                    page_size=len(df_rain),
                    sort_action="native",
                    filter_action="native",
                    export_format="csv"
                )
                
                # Return table with heading
                return html.Div([
                    html.H6("Precipitation Frequency Estimates (NOAA Atlas 14)", className="fw-bold mb-2"),
                    rain_statistics_table
                ])
                
            except Exception as e:
                print(f"Error downloading rain statistics: {e}")
                return html.P(f"Error downloading rain statistics: {str(e)}", className="text-danger")
        
        return html.Div()

    # Callback for "Get Monthly Rainfall and Runoff" button in Monthly Runoff Estimation card
    @app.callback(
        Output('monthly-runoff-estimation-content', 'children'),
        Input('get-monthly-rain-btn', 'n_clicks'),
        [State('runoff-single-storm-latitude', 'value'),
         State('runoff-single-storm-longitude', 'value'),
         State('runoff-calculations-table', 'data')],
        prevent_initial_call=True
    )
    def get_monthly_rain_for_runoff(n_clicks, lat, lon, runoff_table_data):
        """Get monthly rain data and display as table and chart side by side."""
        if n_clicks and n_clicks > 0 and lat is not None and lon is not None:
            try:
                # Get monthly rain data
                monthly_rain = get_monthly_rain(lat, lon)
                #rain_stat = get_rain_data(lat, lon)
                ### 
                # Get Composite Curve Number and Area from the runoff calculations table
                cn = 50  # default value
                area = 0  # default value
                if runoff_table_data:
                    for row in runoff_table_data:
                        if row.get("Parameter") == "Composite Curve Number":
                            try:
                                cn = float(row.get("Value", 50))
                            except (ValueError, TypeError):
                                cn = 50
                        elif row.get("Parameter") == "Area (acres)":
                            try:
                                area = float(row.get("Value", 0))
                            except (ValueError, TypeError):
                                area = 0

                
                runoff_volume = []
                runoff_depth = []
                for p in monthly_rain['Rain (inches)']:
                    if p > 0:
                        s = (1000.0 / cn) - 10
                        alpha_s = p - s
                        lambda005 = 0.05
                        exp_lambda005 = np.exp(-1.0 * lambda005 * (s/p))
                        term1 = alpha_s * exp_lambda005

                        tm1 = s*s/p
                        tm2 = np.exp(((1-lambda005)*s)/p)
                        tm3 = exp1(s/p)
                        term2 = tm1 * tm2 * tm3
                        vol = 30.25*area * 43560 / 12 * (term1 + term2)
                        runoff_depth.append(term1 + term2)
                        runoff_volume.append(vol)
                       
                    else:
                        runoff_volume.append(0)
                        runoff_depth.append(0)
                    

                ###
                
                if monthly_rain is None or monthly_rain.empty:
                    return html.P("No monthly rain data available.", className="text-warning")
                if len(runoff_volume)>0:
                    monthly_rain['Runoff depth (in/day)'] = runoff_depth
                    monthly_rain['Runoff Volume (ft3)'] = runoff_volume
                # Create monthly rain table with different colors for each column
                # Define colors for each column
                column_colors = {
                    'Month': {'header': '#2c5aa0', 'data': '#e8f4f8'},
                    'Rain (inches)': {'header': '#28a745', 'data': '#d4edda'},
                    'Runoff depth (in/day)': {'header': '#ff6b35', 'data': '#ffe5d9'},
                    'Runoff Volume (ft3)': {'header': '#6f42c1', 'data': '#e9d5ff'}
                }
                
                # Build conditional styling for columns
                style_data_conditional = []
                style_header_conditional = []
                
                for col in monthly_rain.columns:
                    if col in column_colors:
                        style_data_conditional.append({
                            'if': {'column_id': col},
                            'backgroundColor': column_colors[col]['data']
                        })
                        style_header_conditional.append({
                            'if': {'column_id': col},
                            'backgroundColor': column_colors[col]['header'],
                            'color': 'white'
                        })
                
                monthly_rain_table = dash_table.DataTable(
                    data=monthly_rain.to_dict('records'),
                    columns=[{"name": i, "id": i} for i in monthly_rain.columns],
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
                        'border': '1px solid #ddd',
                        'color': 'black'
                    },
                    style_data={
                        'backgroundColor': 'white',
                        'border': '1px solid #ddd'
                    },
                    style_data_conditional=style_data_conditional,
                    style_header_conditional=style_header_conditional,
                    page_size=len(monthly_rain),
                    sort_action="native",
                    filter_action="native",
                    export_format="csv"
                )
                
                # Create grouped bar chart for monthly rain and runoff depth
                fig = go.Figure(data=[
                    go.Bar(
                        name='Rainfall',
                        x=monthly_rain['Month'],
                        y=monthly_rain['Rain (inches)'],
                        marker_color='steelblue',
                        text=monthly_rain['Rain (inches)'].round(2),
                        textposition='outside'
                    ),
                    go.Bar(
                        name='Runoff depth (in/day)',
                        x=monthly_rain['Month'],
                        y=monthly_rain['Runoff depth (in/day)'],
                        marker_color='orange',
                        text=monthly_rain['Runoff depth (in/day)'].round(2),
                        textposition='outside'
                    )
                ])
                fig.update_layout(
                    title='Monthly Average Precipitation and Runoff Depth',
                    xaxis_title='Month',
                    yaxis_title='Depth (inches)',
                    xaxis={'tickangle': -45},
                    barmode='group',  # Group bars side by side
                    height=400,
                    margin=dict(l=50, r=50, t=50, b=100),
                    legend=dict(
                        orientation="h",
                        yanchor="bottom",
                        y=1.02,
                        xanchor="right",
                        x=1
                    )
                )
                monthly_rain_chart = dcc.Graph(figure=fig)
                
                # Return table and chart side by side
                return dbc.Row([
                    dbc.Col([monthly_rain_table], width=6),
                    dbc.Col([monthly_rain_chart], width=6)
                ])
                
            except Exception as e:
                print(f"Error getting monthly rain data: {e}")
                return html.P(f"Error getting monthly rain data: {str(e)}", className="text-danger")
        
        return html.Div("Click 'Get Monthly Rainfall and Runoff' to retrieve monthly precipitation data.", className="text-muted")



