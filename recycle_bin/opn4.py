import dash
from dash import dcc, html, Input, Output, callback
import plotly.express as px
import pandas as pd

# Initialize the Dash app
app = dash.Dash(__name__)

# Create the initial map - use a proper base map without data points
fig = px.scatter_mapbox(
    lat=[38.58],  # Sacramento as default center
    lon=[-121.49],
    zoom=8,
    height=600,
    mapbox_style="open-street-map"
)
fig.update_layout(
    mapbox_style="open-street-map",
    margin={"r":0,"t":0,"l":0,"b":0},
    clickmode='event+select',
    showlegend=False
)
# Make the scatter points invisible so the map is fully clickable
fig.update_traces(
    marker=dict(size=0, opacity=0),
    selector=dict(type='scattermapbox')
)

# App layout
app.layout = html.Div([
    html.H1("🌍 Interactive Map Dashboard - Click Anywhere for Coordinates", 
            style={'textAlign': 'center', 'marginBottom': 30}),
    
    html.Div([
        dcc.Graph(
            id='world-map',
            figure=fig,
            config={'displayModeBar': True}
        )
    ], style={'width': '100%', 'height': '600px'}),
    
    html.Div([
        html.Div([
            html.H3("📍 Clicked Coordinates", style={'color': '#2E86AB'}),
            html.Div(id='coordinates-display', 
                    style={
                        'backgroundColor': '#f8f9fa',
                        'padding': '20px',
                        'borderRadius': '10px',
                        'border': '2px solid #dee2e6',
                        'marginTop': '20px'
                    })
        ], style={'width': '48%', 'display': 'inline-block', 'verticalAlign': 'top', 'padding': '10px'}),
        
        html.Div([
            html.H3("📋 Click History", style={'color': '#A23B72'}),
            html.Div(id='click-history',
                    style={
                        'backgroundColor': '#f8f9fa',
                        'padding': '20px',
                        'borderRadius': '10px',
                        'border': '2px solid #dee2e6',
                        'marginTop': '20px',
                        'maxHeight': '300px',
                        'overflowY': 'auto'
                    })
        ], style={'width': '48%', 'display': 'inline-block', 'verticalAlign': 'top', 'padding': '10px'})
    ], style={'marginTop': '30px'}),
    
    # Store component for click history
    dcc.Store(id='click-store', data=[])
])

# Callback to handle map clicks and update coordinates
@callback(
    [Output('coordinates-display', 'children'),
     Output('click-history', 'children'),
     Output('click-store', 'data')],
    [Input('world-map', 'clickData')],
    [dash.dependencies.State('click-store', 'data')]
)
def display_click_data(clickData, history):
    if clickData is None or 'points' not in clickData or len(clickData['points']) == 0:
        # Default message when no clicks yet
        coords_display = html.Div([
            html.P("Click anywhere on the map to see coordinates here!", 
                  style={'color': '#6c757d', 'fontStyle': 'italic'})
        ])
        history_display = html.P("No clicks recorded yet.", 
                               style={'color': '#6c757d', 'fontStyle': 'italic'})
        return coords_display, history_display, history
    
    # Extract coordinates from click data
    lat = clickData['points'][0]['lat']
    lon = clickData['points'][0]['lon']
    
    # Create coordinates display
    coords_display = html.Div([
        html.H4("Selected Location", style={'color': '#2E86AB', 'marginBottom': '15px'}),
        html.Table([
            html.Tr([html.Td(html.Strong("Latitude:")), html.Td(f"{lat:.6f}°")]),
            html.Tr([html.Td(html.Strong("Longitude:")), html.Td(f"{lon:.6f}°")]),
            html.Tr([html.Td(html.Strong("DMS:")), html.Td(convert_to_dms(lat, lon))])
        ], style={'width': '100%', 'fontSize': '16px'})
    ])
    
    # Add to history
    new_entry = {
        'lat': f"{lat:.6f}",
        'lon': f"{lon:.6f}",
        'timestamp': pd.Timestamp.now().strftime('%H:%M:%S')
    }
    
    # Keep only last 10 entries
    updated_history = history[-9:] + [new_entry] if len(history) > 0 else [new_entry]
    
    # Create history display
    history_items = []
    for i, entry in enumerate(reversed(updated_history)):
        history_items.append(
            html.Div([
                html.Strong(f"Click {len(updated_history)-i}:"),
                html.Br(),
                f"Lat: {entry['lat']}, Lon: {entry['lon']}",
                html.Br(),
                html.Small(f"Time: {entry['timestamp']}", style={'color': '#6c757d'})
            ], style={
                'padding': '8px',
                'marginBottom': '8px',
                'backgroundColor': 'white',
                'borderRadius': '5px',
                'border': '1px solid #dee2e6'
            })
        )
    
    history_display = html.Div(history_items)
    
    return coords_display, history_display, updated_history

def convert_to_dms(lat, lon):
    """Convert decimal degrees to Degrees Minutes Seconds format"""
    def to_dms(coord, is_lat):
        direction = 'N' if is_lat and coord >= 0 else 'S' if is_lat else 'E' if coord >= 0 else 'W'
        coord = abs(coord)
        degrees = int(coord)
        minutes = int((coord - degrees) * 60)
        seconds = (coord - degrees - minutes/60) * 3600
        return f"{degrees}°{minutes}'{seconds:.2f}\" {direction}"
    
    lat_dms = to_dms(lat, True)
    lon_dms = to_dms(lon, False)
    return f"{lat_dms}, {lon_dms}"

if __name__ == '__main__':
    app.run(debug=True)