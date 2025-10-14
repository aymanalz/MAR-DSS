"""
Hydrogeology tab callbacks for MAR DSS dashboard.
"""

import dash
import dash_bootstrap_components as dbc
import pandas as pd
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
         Input({"type": "conductivity-input", "index": dash.dependencies.ALL}, "value"),
         Input({"type": "storage-input", "index": dash.dependencies.ALL}, "value"),
         Input({"type": "yield-input", "index": dash.dependencies.ALL}, "value")],
        [State("stratigraphy-data-store", "data")],
        prevent_initial_call=True
    )
    def update_table_data(checkbox_values, layer_values, conductivity_values, storage_values, yield_values, data):
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
            if i < len(conductivity_values) and conductivity_values[i] is not None:
                row["conductivity"] = float(conductivity_values[i])
            if i < len(storage_values) and storage_values[i] is not None:
                row["storage"] = float(storage_values[i])
            if i < len(yield_values) and yield_values[i] is not None:
                row["yield"] = float(yield_values[i])
        
        return data