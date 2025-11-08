"""
Callbacks for the Runoff Calculator tab.
"""
import os
import dash
from dash import Input, Output, html, no_update, State
import dash_bootstrap_components as dbc
import dash_leaflet as dl
import pandas as pd
import osmnx as ox
import geopandas as gpd
import streamstats
import json
from dash import dash_table
from mar_dss.pfdf.data.noaa.atlas14 import download



try:
    from mar_dss.app.components.runoff_calculator_tab import create_runoff_map
except ImportError:
    from ..components.runoff_calculator_tab import create_runoff_map
df = pd.DataFrame()

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
            rain_table = None
            try:
                df_rain = get_rain_data(lat, lon)
            except Exception as e:
                print(f"Error getting rain data: {e}")
                rain_table = html.P(f"Error getting rain data: {str(e)}", className="text-danger")
            
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
                
                # Generate rain table with error handling (only if not already set from error above)
                if rain_table is None:
                    try:
                        if df_rain is None or df_rain.empty:
                            print("Rain DataFrame is empty or None!")
                            rain_table = html.P("No rain data available.", className="text-warning")
                        else:
                            rain_table = dash_table.DataTable(
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
                        rain_table = html.P(f"Error creating rain table: {str(rain_table_error)}", className="text-danger")
                
                print(f"Watershed table generated with {len(df)} rows")
                if df_rain is not None:
                    print(f"Rain table generated with {len(df_rain)} rows")
                
                # Show completion message
                done_msg = html.Div("Done!", className="alert alert-success", role="alert")
                return [watershed_layer], watershed_table, rain_table, done_msg
                
            except Exception as e:
                print(f"Error getting watershed data: {e}")
                error_msg = html.Div("Error getting watershed data", className="alert alert-danger", role="alert")
                # Use rain_table if it was set, otherwise show default message
                if rain_table is None:
                    rain_table = html.P("No data available.", className="text-warning")
                return [], html.P(f"Error getting watershed data: {str(e)}", className="text-danger"), rain_table, error_msg
        
        return [], html.Div("Click 'Get Watershed Info' to retrieve watershed data."), html.Div("Click 'Get Watershed Info' to retrieve rain data."), html.Div("")

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
                {"Parameter": "Total Impervious Area %", "Value": ""},
                {"Parameter": "R %", "Value": ""},
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
                    p13 = float(table_data[2]["Value"]) if table_data[2]["Value"] != "" else 0
                    p14 = float(table_data[3]["Value"]) if table_data[3]["Value"] != "" else 0
                    # First part: ((P11*P13)+(P12*(100-P13)))/100
                    first_part = ((p11 * p13) + (p12 * (100 - p13))) / 100
                    # Second part: ((P14/100)*P13*((((P11*P13)+(P12*(100-P13)))/100)-P12))/100
                    second_part = ((p14 / 100) * p13 * (first_part - p12)) / 100
                    composite_cn = first_part - second_part
                    table_data[4]["Value"] = round(composite_cn, 2)
                except (ValueError, TypeError, IndexError):
                    table_data[4]["Value"] = 0
            
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



