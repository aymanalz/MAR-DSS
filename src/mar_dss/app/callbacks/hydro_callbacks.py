"""
Hydrogeology tab callbacks for MAR DSS dashboard.
"""

import dash
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.graph_objects as go
from dash import Input, Output, dcc, html, State, callback_context


def setup_hydro_callbacks(app):
    """Set up all hydrogeology-related callbacks."""
    
    # Typical values for different soil types
    SOIL_PROPERTIES = {
        "Gravel": {"conductivity": 100.0, "storage": 0.0001, "yield": 0.30},
        "Sand": {"conductivity": 10.0, "storage": 0.0001, "yield": 0.25},
        "Silt": {"conductivity": 0.01, "storage": 0.0001, "yield": 0.10},
        "Loam": {"conductivity": 0.001, "storage": 0.0001, "yield": 0.05},
        "Clay": {"conductivity": 0.0001, "storage": 0.0001, "yield": 0.01}
    }
    
    @app.callback(
        Output("stratigraphy-table-body", "children"),
        [Input("stratigraphy-data-store", "data")],
        prevent_initial_call=False
    )
    def update_stratigraphy_table(data):
        """Update the stratigraphy table based on stored data."""
        if not data:
            return []
        
        rows = []
        for i, row in enumerate(data):
            # Create checkbox for selection
            checkbox = dbc.Checkbox(
                id={"type": "layer-checkbox", "index": i},
                value=row.get("selected", False),
                className="form-check-input"
            )
            
            # Create layer dropdown
            layer_dropdown = dbc.Select(
                id={"type": "layer-select", "index": i},
                value=row["layer"],
                options=[{"label": lith, "value": lith} for lith in SOIL_PROPERTIES.keys()],
                size="sm"
            )
            
            # Create thickness input
            thickness_input = dbc.Input(
                id={"type": "thickness-input", "index": i},
                value=row["thickness"],
                type="number",
                step="0.1",
                size="sm"
            )
            
            # Create input fields
            conductivity_input = dbc.Input(
                id={"type": "conductivity-input", "index": i},
                value=row["conductivity"],
                type="number",
                step="0.001",
                size="sm"
            )
            
            storage_input = dbc.Input(
                id={"type": "storage-input", "index": i},
                value=row["storage"],
                type="number",
                step="0.000001",
                size="sm"
            )
            
            yield_input = dbc.Input(
                id={"type": "yield-input", "index": i},
                value=row["yield"],
                type="number",
                step="0.01",
                size="sm"
            )
            
            rows.append(html.Tr([
                html.Td(checkbox),
                html.Td(layer_dropdown),
                html.Td(thickness_input),
                html.Td(conductivity_input),
                html.Td(storage_input),
                html.Td(yield_input)
            ]))
        
        return rows
    
    @app.callback(
        Output("stratigraphy-data-store", "data"),
        [Input("add-layer-btn", "n_clicks"),
         Input("delete-layer-btn", "n_clicks"),
         Input("move-up-btn", "n_clicks"),
         Input("move-down-btn", "n_clicks")],
        [State("stratigraphy-data-store", "data")],
        prevent_initial_call=True
    )
    def handle_table_actions(add_clicks, delete_clicks, move_up_clicks, move_down_clicks, data):
        """Handle table actions (add, delete, move)."""
        ctx = callback_context
        if not ctx.triggered:
            return data
        
        button_id = ctx.triggered[0]["prop_id"].split(".")[0]
        current_data = data or []
        
        if button_id == "add-layer-btn":
            # Add new layer (default to Sand)
            new_layer = {
                "layer": "Sand",
                "thickness": 60.0,
                "conductivity": SOIL_PROPERTIES["Sand"]["conductivity"],
                "storage": SOIL_PROPERTIES["Sand"]["storage"],
                "yield": SOIL_PROPERTIES["Sand"]["yield"],
                "selected": False
            }
            current_data.append(new_layer)
            
        elif button_id == "delete-layer-btn":
            # Delete selected layers
            current_data = [row for row in current_data if not row.get("selected", False)]
            
        elif button_id == "move-up-btn":
            # Move selected layers up
            for i in range(1, len(current_data)):
                if current_data[i].get("selected", False) and not current_data[i-1].get("selected", False):
                    current_data[i], current_data[i-1] = current_data[i-1], current_data[i]
                    
        elif button_id == "move-down-btn":
            # Move selected layers down
            for i in range(len(current_data)-2, -1, -1):
                if current_data[i].get("selected", False) and not current_data[i+1].get("selected", False):
                    current_data[i], current_data[i+1] = current_data[i+1], current_data[i]
        
        return current_data
    
    @app.callback(
        Output("stratigraphy-data-store", "data", allow_duplicate=True),
        [Input({"type": "layer-checkbox", "index": dash.dependencies.ALL}, "value"),
         Input({"type": "layer-select", "index": dash.dependencies.ALL}, "value"),
         Input({"type": "thickness-input", "index": dash.dependencies.ALL}, "value"),
         Input({"type": "conductivity-input", "index": dash.dependencies.ALL}, "value"),
         Input({"type": "storage-input", "index": dash.dependencies.ALL}, "value"),
         Input({"type": "yield-input", "index": dash.dependencies.ALL}, "value")],
        [State("stratigraphy-data-store", "data")],
        prevent_initial_call=True
    )
    def update_table_data(checkbox_values, layer_values, thickness_values, conductivity_values, storage_values, yield_values, data):
        """Update table data when inputs change."""
        if not data:
            return data
        
        # Update data with new values
        for i, row in enumerate(data):
            if i < len(checkbox_values):
                row["selected"] = checkbox_values[i] or False
            if i < len(layer_values):
                row["layer"] = layer_values[i]
                # Update properties based on selected layer
                if layer_values[i] in SOIL_PROPERTIES:
                    props = SOIL_PROPERTIES[layer_values[i]]
                    row["conductivity"] = props["conductivity"]
                    row["storage"] = props["storage"]
                    row["yield"] = props["yield"]
            if i < len(thickness_values) and thickness_values[i] is not None:
                row["thickness"] = float(thickness_values[i])
            if i < len(conductivity_values) and conductivity_values[i] is not None:
                row["conductivity"] = float(conductivity_values[i])
            if i < len(storage_values) and storage_values[i] is not None:
                row["storage"] = float(storage_values[i])
            if i < len(yield_values) and yield_values[i] is not None:
                row["yield"] = float(yield_values[i])
        
        return data
    
    # Groundwater Level Table Callbacks
    @app.callback(
        Output("groundwater-table-body", "children"),
        [Input("groundwater-data-store", "data")],
        prevent_initial_call=False
    )
    def update_groundwater_table(data):
        """Update the groundwater level table based on stored data."""
        if not data:
            return []
        
        rows = []
        for i, row in enumerate(data):
            # Create checkbox for selection
            checkbox = dbc.Checkbox(
                id={"type": "gw-checkbox", "index": i},
                value=row.get("selected", False),
                className="form-check-input"
            )
            
            # Create month dropdown
            month_dropdown = dbc.Select(
                id={"type": "month-select", "index": i},
                value=row["month"],
                options=[
                    {"label": "January", "value": "January"},
                    {"label": "February", "value": "February"},
                    {"label": "March", "value": "March"},
                    {"label": "April", "value": "April"},
                    {"label": "May", "value": "May"},
                    {"label": "June", "value": "June"},
                    {"label": "July", "value": "July"},
                    {"label": "August", "value": "August"},
                    {"label": "September", "value": "September"},
                    {"label": "October", "value": "October"},
                    {"label": "November", "value": "November"},
                    {"label": "December", "value": "December"}
                ],
                size="sm"
            )
            
            # Create elevation input
            elevation_input = dbc.Input(
                id={"type": "elevation-input", "index": i},
                value=row["elevation"],
                type="number",
                step="0.1",
                size="sm"
            )
            
            rows.append(html.Tr([
                html.Td(checkbox),
                html.Td(month_dropdown),
                html.Td(elevation_input)
            ]))
        
        return rows
    
    @app.callback(
        Output("groundwater-data-store", "data"),
        [Input("add-month-btn", "n_clicks"),
         Input("delete-month-btn", "n_clicks"),
         Input("reset-gw-btn", "n_clicks")],
        [State("groundwater-data-store", "data")],
        prevent_initial_call=True
    )
    def handle_groundwater_actions(add_clicks, delete_clicks, reset_clicks, data):
        """Handle groundwater table actions."""
        ctx = callback_context
        if not ctx.triggered:
            return data
        
        button_id = ctx.triggered[0]["prop_id"].split(".")[0]
        current_data = data or []
        
        if button_id == "add-month-btn":
            # Add new month (default to January)
            new_month = {
                "month": "January",
                "elevation": 75.0,
                "selected": False
            }
            current_data.append(new_month)
            
        elif button_id == "delete-month-btn":
            # Delete selected months
            current_data = [row for row in current_data if not row.get("selected", False)]
            
        elif button_id == "reset-gw-btn":
            # Reset to default values
            current_data = [
                {"month": "January", "elevation": 75.0, "selected": False},
                {"month": "February", "elevation": 72.0, "selected": False},
                {"month": "March", "elevation": 78.0, "selected": False},
                {"month": "April", "elevation": 82.0, "selected": False},
                {"month": "May", "elevation": 85.0, "selected": False},
                {"month": "June", "elevation": 88.0, "selected": False},
                {"month": "July", "elevation": 90.0, "selected": False},
                {"month": "August", "elevation": 89.0, "selected": False},
                {"month": "September", "elevation": 86.0, "selected": False},
                {"month": "October", "elevation": 83.0, "selected": False},
                {"month": "November", "elevation": 79.0, "selected": False},
                {"month": "December", "elevation": 76.0, "selected": False}
            ]
        
        return current_data
    
    @app.callback(
        Output("groundwater-data-store", "data", allow_duplicate=True),
        [Input({"type": "gw-checkbox", "index": dash.dependencies.ALL}, "value"),
         Input({"type": "month-select", "index": dash.dependencies.ALL}, "value"),
         Input({"type": "elevation-input", "index": dash.dependencies.ALL}, "value")],
        [State("groundwater-data-store", "data")],
        prevent_initial_call=True
    )
    def update_groundwater_data(checkbox_values, month_values, elevation_values, data):
        """Update groundwater data when inputs change."""
        if not data:
            return data
        
        # Update data with new values
        for i, row in enumerate(data):
            if i < len(checkbox_values):
                row["selected"] = checkbox_values[i] or False
            if i < len(month_values):
                row["month"] = month_values[i]
            if i < len(elevation_values) and elevation_values[i] is not None:
                row["elevation"] = float(elevation_values[i])
        
        return data
    
    # Groundwater Level Plot Callback
    @app.callback(
        Output("groundwater-plot", "figure"),
        [Input("groundwater-data-store", "data"),
         Input("ground-surface-elevation", "value"),
         Input("max-mar-storage-depth", "value")],
        prevent_initial_call=False
    )
    def update_groundwater_plot(data, ground_elevation, max_storage_depth):
        """Update the groundwater level plot based on table data."""
        if not data:
            return go.Figure()
        
        # Convert data to DataFrame for easier handling
        df = pd.DataFrame(data)
        
        # Sort by month order
        month_order = ['January', 'February', 'March', 'April', 'May', 'June',
                      'July', 'August', 'September', 'October', 'November', 'December']
        df['month_num'] = df['month'].map({month: i for i, month in enumerate(month_order)})
        df = df.sort_values('month_num')
        
        # Create the plot
        fig = go.Figure()
        
        # Add groundwater elevation line plot
        fig.add_trace(go.Scatter(
            x=df['month'],
            y=df['elevation'],
            mode='lines+markers',
            name='Groundwater Elevation',
            line=dict(color='#1f77b4', width=3),
            marker=dict(size=8, color='#1f77b4'),
            hovertemplate='<b>%{x}</b><br>Elevation: %{y:.1f} ft<extra></extra>'
        ))
        
        # Add horizontal lines if values are provided
        if ground_elevation is not None:
            # Ground surface elevation line
            fig.add_hline(
                y=ground_elevation,
                line_dash="dash",
                line_color="green",
                line_width=2,
                annotation_text=f"Ground Surface: {ground_elevation:.1f} ft",
                annotation_position="top right"
            )
        
        if max_storage_depth is not None and ground_elevation is not None:
            # Maximum MAR storage depth line (from ground surface)
            mar_storage_line = ground_elevation - max_storage_depth
            fig.add_hline(
                y=mar_storage_line,
                line_dash="dot",
                line_color="red",
                line_width=2,
                annotation_text=f"Max MAR Storage: {mar_storage_line:.1f} ft",
                annotation_position="bottom right"
            )
        
        # Update layout
        fig.update_layout(
            title={
                'text': 'Groundwater Elevation Variation by Month',
                'x': 0.5,
                'xanchor': 'center',
                'font': {'size': 16}
            },
            xaxis_title="Month",
            yaxis_title="Elevation (ft)",
            template="plotly_white",
            height=400,
            margin=dict(l=50, r=50, t=60, b=50),
            showlegend=False
        )
        
        # Add grid
        fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='lightgray')
        fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='lightgray')
        
        return fig