"""
Hydrogeology tab callbacks for MAR DSS dashboard.
"""

import dash
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.graph_objects as go
from dash import Input, Output, dcc, html, State, callback_context
import mar_dss.app.utils.data_storage as dash_storage


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
    
    # Callback to show/hide maximum allowed head input for confined aquifers
    @app.callback(
        Output("confined-head-input-container", "style"),
        [Input("aquifer-type-radio", "value")],
        prevent_initial_call=False
    )
    def toggle_confined_head_input(aquifer_type):
        """Show maximum allowed head input only when confined aquifer is selected."""
        if aquifer_type == "confined":
            return {"display": "block"}
        else:
            return {"display": "none"}
    
    # Callback to synchronize geometry tabs with view tabs
    @app.callback(
        Output("view-tabs", "active_tab"),
        [Input("geometry-tabs", "active_tab")],
        prevent_initial_call=False
    )
    def sync_view_tabs_with_geometry_tabs(active_geometry_tab):
        """Synchronize view tabs based on geometry tab selection."""
        # Map geometry tabs to view tabs
        tab_mapping = {
            "stratigraphy-tab": "stratigraphy-cross-section",
            "groundwater-level-tab": "available-mar-storage",
            "horizontal-extension-tab": "xy-view"
        }
        
        # Return the corresponding view tab, or default to stratigraphy-cross-section
        return tab_mapping.get(active_geometry_tab, "stratigraphy-cross-section")
    
    # Callback to save aquifer type to data storage
    @app.callback(
        Output("aquifer-type-radio", "value"),
        [
            Input("aquifer-type-radio", "value"),
            Input("aquifer-type-radio", "id")
        ],
        prevent_initial_call=False
    )
    def handle_aquifer_type_selection(value, component_id):
        """Handle aquifer type selection and save to data storage."""
        ctx = dash.callback_context
        
        if not ctx.triggered:
            # Initial load - get saved aquifer type or use default, and save it
            aquifer_type = dash_storage.get_data("aq_type") or "unconfined"
            dash_storage.set_data("aq_type", aquifer_type)
            return aquifer_type
        
        # Get the current selection
        current_selection = value if value else "unconfined"
        
        # Save aquifer type to data storage
        dash_storage.set_data("aq_type", current_selection)
        
        return current_selection
    
    def _set_confined_stratigraphy():
        """Set stratigraphy to 4 layers for confined aquifer."""
        confined_stratigraphy = [
            {"layer": "Sand", "thickness": 100.0, "conductivity": SOIL_PROPERTIES["Sand"]["conductivity"], 
             "storage": SOIL_PROPERTIES["Sand"]["storage"], "yield": SOIL_PROPERTIES["Sand"]["yield"], "selected": False},
            {"layer": "Clay", "thickness": 10.0, "conductivity": SOIL_PROPERTIES["Clay"]["conductivity"], 
             "storage": SOIL_PROPERTIES["Clay"]["storage"], "yield": SOIL_PROPERTIES["Clay"]["yield"], "selected": False},
            {"layer": "Sand", "thickness": 50.0, "conductivity": SOIL_PROPERTIES["Sand"]["conductivity"], 
             "storage": SOIL_PROPERTIES["Sand"]["storage"], "yield": SOIL_PROPERTIES["Sand"]["yield"], "selected": False},
            {"layer": "Clay", "thickness": 10.0, "conductivity": SOIL_PROPERTIES["Clay"]["conductivity"], 
             "storage": SOIL_PROPERTIES["Clay"]["storage"], "yield": SOIL_PROPERTIES["Clay"]["yield"], "selected": False},
        ]
        dash_storage.set_data("stratigraphy_data", confined_stratigraphy)
    
    # Callback to save max allowed head to data storage
    @app.callback(
        Output("max-allowed-head-input", "value"),
        [
            Input("max-allowed-head-input", "value"),
            Input("max-allowed-head-input", "n_blur"),
            Input("max-allowed-head-input", "n_submit"),
            Input("max-allowed-head-input", "id")
        ],
        prevent_initial_call=False
    )
    def handle_max_allowed_head_input(value, n_blur, n_submit, component_id):
        """Handle max allowed head input and save to data storage."""
        ctx = dash.callback_context
        
        if not ctx.triggered:
            # Initial load - get saved value and ensure it's a float, then save it
            max_head = dash_storage.get_data("max_allowed_head")
            if max_head is not None:
                try:
                    max_head = float(max_head)
                except (ValueError, TypeError):
                    max_head = 1.0
            else:
                max_head = 1.0
            dash_storage.set_data("max_allowed_head", max_head)
            return max_head
        
        # Get the current value and convert to float
        if value is not None:
            try:
                current_value = float(value)
            except (ValueError, TypeError):
                current_value = 1.0
        else:
            current_value = 1.0
        
        # Determine which trigger caused the callback
        trigger_prop = ctx.triggered[0]["prop_id"].split(".")[1] if ctx.triggered else ""
        
        # Save for all triggers except initial load (ensure it's saved as float)
        if trigger_prop != "id":
            dash_storage.set_data("max_allowed_head", current_value)
        
        return current_value
    
    # Callback to save stratigraphy data to dash_storage when store updates
    @app.callback(
        Output("stratigraphy-data-store", "data", allow_duplicate=True),
        [Input("stratigraphy-data-store", "data")],
        prevent_initial_call=True
    )
    def save_stratigraphy_to_storage(data):
        """Save stratigraphy data to dash_storage when store updates."""
        if data:
            dash_storage.set_data("stratigraphy_data", data)
        return dash.no_update
    
    # Callback to save groundwater data to dash_storage when store updates
    @app.callback(
        Output("groundwater-data-store", "data", allow_duplicate=True),
        [Input("groundwater-data-store", "data")],
        prevent_initial_call=True
    )
    def save_groundwater_to_storage(data):
        """Save groundwater data to dash_storage when store updates."""
        if data:
            dash_storage.set_data("groundwater_data", data)
        return dash.no_update
    
    # Callback to save ground surface elevation to data storage
    @app.callback(
        Output("ground-surface-elevation", "value"),
        [
            Input("ground-surface-elevation", "value"),
            Input("ground-surface-elevation", "n_blur"),
            Input("ground-surface-elevation", "n_submit"),
            Input("ground-surface-elevation", "id")
        ],
        prevent_initial_call=False
    )
    def handle_ground_surface_elevation_input(value, n_blur, n_submit, component_id):
        """Handle ground surface elevation input and save to data storage."""
        ctx = dash.callback_context
        
        if not ctx.triggered:
            # Initial load - get saved value and ensure it's a float, then save it
            elevation = dash_storage.get_data("ground_surface_elevation")
            if elevation is not None:
                try:
                    elevation = float(elevation)
                except (ValueError, TypeError):
                    elevation = 120.0
            else:
                elevation = 120.0
            dash_storage.set_data("ground_surface_elevation", elevation)
            return elevation
        
        # Get the current value and convert to float
        if value is not None:
            try:
                current_value = float(value)
            except (ValueError, TypeError):
                current_value = 120.0
        else:
            current_value = 120.0
        
        # Determine which trigger caused the callback
        trigger_prop = ctx.triggered[0]["prop_id"].split(".")[1] if ctx.triggered else ""
        
        # Save for all triggers except initial load (ensure it's saved as float)
        if trigger_prop != "id":
            dash_storage.set_data("ground_surface_elevation", current_value)
        
        return current_value
    
    # Callback to save max MAR storage depth to data storage
    @app.callback(
        Output("max-mar-storage-depth", "value"),
        [
            Input("max-mar-storage-depth", "value"),
            Input("max-mar-storage-depth", "n_blur"),
            Input("max-mar-storage-depth", "n_submit"),
            Input("max-mar-storage-depth", "id")
        ],
        prevent_initial_call=False
    )
    def handle_max_mar_storage_depth_input(value, n_blur, n_submit, component_id):
        """Handle max MAR storage depth input and save to data storage."""
        ctx = dash.callback_context
        
        if not ctx.triggered:
            # Initial load - get saved value and ensure it's a float, then save it
            depth = dash_storage.get_data("max_mar_storage_depth")
            if depth is not None:
                try:
                    depth = float(depth)
                except (ValueError, TypeError):
                    depth = 20.0
            else:
                depth = 20.0
            dash_storage.set_data("max_mar_storage_depth", depth)
            return depth
        
        # Get the current value and convert to float
        if value is not None:
            try:
                current_value = float(value)
            except (ValueError, TypeError):
                current_value = 20.0
        else:
            current_value = 20.0
        
        # Determine which trigger caused the callback
        trigger_prop = ctx.triggered[0]["prop_id"].split(".")[1] if ctx.triggered else ""
        
        # Save for all triggers except initial load (ensure it's saved as float)
        if trigger_prop != "id":
            dash_storage.set_data("max_mar_storage_depth", current_value)
        
        return current_value
    
    # Callback to save extension length to data storage
    @app.callback(
        Output("extension-length", "value"),
        [
            Input("extension-length", "value"),
            Input("extension-length", "n_blur"),
            Input("extension-length", "n_submit"),
            Input("extension-length", "id")
        ],
        prevent_initial_call=False
    )
    def handle_extension_length_input(value, n_blur, n_submit, component_id):
        """Handle extension length input and save to data storage."""
        ctx = dash.callback_context
        
        if not ctx.triggered:
            # Initial load - get saved value or use default, and save it
            length = dash_storage.get_data("extension_length") or 100.0
            dash_storage.set_data("extension_length", length)
            return length
        
        current_value = value if value is not None else 100.0
        trigger_prop = ctx.triggered[0]["prop_id"].split(".")[1] if ctx.triggered else ""
        
        if trigger_prop != "id":
            dash_storage.set_data("extension_length", current_value)
        
        return current_value
    
    # Callback to save extension width to data storage
    @app.callback(
        Output("extension-width", "value"),
        [
            Input("extension-width", "value"),
            Input("extension-width", "n_blur"),
            Input("extension-width", "n_submit"),
            Input("extension-width", "id")
        ],
        prevent_initial_call=False
    )
    def handle_extension_width_input(value, n_blur, n_submit, component_id):
        """Handle extension width input and save to data storage."""
        ctx = dash.callback_context
        
        if not ctx.triggered:
            # Initial load - get saved value or use default, and save it
            width = dash_storage.get_data("extension_width") or 50.0
            dash_storage.set_data("extension_width", width)
            return width
        
        current_value = value if value is not None else 50.0
        trigger_prop = ctx.triggered[0]["prop_id"].split(".")[1] if ctx.triggered else ""
        
        if trigger_prop != "id":
            dash_storage.set_data("extension_width", current_value)
        
        return current_value
    
    # Callback to save extension rotation to data storage
    @app.callback(
        Output("extension-rotation", "value"),
        [
            Input("extension-rotation", "value"),
            Input("extension-rotation", "n_blur"),
            Input("extension-rotation", "n_submit"),
            Input("extension-rotation", "id")
        ],
        prevent_initial_call=False
    )
    def handle_extension_rotation_input(value, n_blur, n_submit, component_id):
        """Handle extension rotation input and save to data storage."""
        ctx = dash.callback_context
        
        if not ctx.triggered:
            # Initial load - get saved value or use default, and save it
            rotation = dash_storage.get_data("extension_rotation") or 0.0
            dash_storage.set_data("extension_rotation", rotation)
            return rotation
        
        current_value = value if value is not None else 0.0
        trigger_prop = ctx.triggered[0]["prop_id"].split(".")[1] if ctx.triggered else ""
        
        if trigger_prop != "id":
            dash_storage.set_data("extension_rotation", current_value)
        
        return current_value
    
    # Callback to save upstream head to data storage
    @app.callback(
        Output("upstream-head", "value"),
        [
            Input("upstream-head", "value"),
            Input("upstream-head", "n_blur"),
            Input("upstream-head", "n_submit"),
            Input("upstream-head", "id")
        ],
        prevent_initial_call=False
    )
    def handle_upstream_head_input(value, n_blur, n_submit, component_id):
        """Handle upstream head input and save to data storage."""
        ctx = dash.callback_context
        
        if not ctx.triggered:
            # Initial load - get saved value or use default, and save it
            head = dash_storage.get_data("upstream_head") or 10.0
            dash_storage.set_data("upstream_head", head)
            return head
        
        current_value = value if value is not None else 10.0
        trigger_prop = ctx.triggered[0]["prop_id"].split(".")[1] if ctx.triggered else ""
        
        if trigger_prop != "id":
            dash_storage.set_data("upstream_head", current_value)
        
        return current_value
    
    # Callback to save downstream head to data storage
    @app.callback(
        Output("downstream-head", "value"),
        [
            Input("downstream-head", "value"),
            Input("downstream-head", "n_blur"),
            Input("downstream-head", "n_submit"),
            Input("downstream-head", "id")
        ],
        prevent_initial_call=False
    )
    def handle_downstream_head_input(value, n_blur, n_submit, component_id):
        """Handle downstream head input and save to data storage."""
        ctx = dash.callback_context
        
        if not ctx.triggered:
            # Initial load - get saved value or use default, and save it
            head = dash_storage.get_data("downstream_head") or 5.0
            dash_storage.set_data("downstream_head", head)
            return head
        
        current_value = value if value is not None else 5.0
        trigger_prop = ctx.triggered[0]["prop_id"].split(".")[1] if ctx.triggered else ""
        
        if trigger_prop != "id":
            dash_storage.set_data("downstream_head", current_value)
        
        return current_value
    
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
        
        # Check if confined aquifer is selected
        aquifer_type = dash_storage.get_data("aq_type") or "unconfined"
        current_data = data or []
        
        button_id = ctx.triggered[0]["prop_id"].split(".")[0]
        
        # For confined aquifers, prevent adding or deleting layers
        if aquifer_type == "confined":
            if button_id == "add-layer-btn":
                # Don't add layer, return current data unchanged
                # Error message will be shown by another callback
                return dash.no_update
            elif button_id == "delete-layer-btn":
                # Don't delete layers, return current data unchanged
                # Error message will be shown by another callback
                return dash.no_update
        
        # For non-confined or move operations, proceed normally
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
        
        # Check if confined aquifer is selected
        aquifer_type = dash_storage.get_data("aq_type") or "unconfined"
        
        # For confined aquifers, ensure exactly 4 layers
        if aquifer_type == "confined" and len(data) != 4:
            # Don't update if layer count is wrong - error will be shown
            return dash.no_update
        
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
    
    # Callback to update stratigraphy store when aquifer type changes to confined
    @app.callback(
        Output("stratigraphy-data-store", "data", allow_duplicate=True),
        [Input("aquifer-type-radio", "value")],
        prevent_initial_call=True
    )
    def update_stratigraphy_for_aquifer_type(aquifer_type):
        """Update stratigraphy when aquifer type changes."""
        if aquifer_type == "confined":
            confined_stratigraphy = [
                {"layer": "Sand", "thickness": 100.0, "conductivity": SOIL_PROPERTIES["Sand"]["conductivity"], 
                 "storage": SOIL_PROPERTIES["Sand"]["storage"], "yield": SOIL_PROPERTIES["Sand"]["yield"], "selected": False},
                {"layer": "Clay", "thickness": 10.0, "conductivity": SOIL_PROPERTIES["Clay"]["conductivity"], 
                 "storage": SOIL_PROPERTIES["Clay"]["storage"], "yield": SOIL_PROPERTIES["Clay"]["yield"], "selected": False},
                {"layer": "Sand", "thickness": 50.0, "conductivity": SOIL_PROPERTIES["Sand"]["conductivity"], 
                 "storage": SOIL_PROPERTIES["Sand"]["storage"], "yield": SOIL_PROPERTIES["Sand"]["yield"], "selected": False},
                {"layer": "Clay", "thickness": 10.0, "conductivity": SOIL_PROPERTIES["Clay"]["conductivity"], 
                 "storage": SOIL_PROPERTIES["Clay"]["storage"], "yield": SOIL_PROPERTIES["Clay"]["yield"], "selected": False},
            ]
            dash_storage.set_data("stratigraphy_data", confined_stratigraphy)
            return confined_stratigraphy
        return dash.no_update
    
    # Callback to show error message for confined aquifer layer restrictions
    @app.callback(
        Output("stratigraphy-error-message", "children"),
        [
            Input("aquifer-type-radio", "value"),
            Input("stratigraphy-data-store", "data"),
            Input("add-layer-btn", "n_clicks"),
            Input("delete-layer-btn", "n_clicks"),
        ],
        prevent_initial_call=False
    )
    def show_stratigraphy_error_message(aquifer_type, stratigraphy_data, add_clicks, delete_clicks):
        """Show error message if user tries to change layer count for confined aquifer."""
        if aquifer_type == "confined":
            num_layers = len(stratigraphy_data) if stratigraphy_data else 0
            if num_layers != 4:
                return dbc.Alert(
                    "Error: Confined aquifer must have exactly 4 layers. The stratigraphy has been reset to the required configuration.",
                    color="danger",
                    className="mb-2"
                )
            else:
                return dbc.Alert(
                    "Note: Confined aquifer requires exactly 4 layers. Adding or deleting layers is not allowed.",
                    color="info",
                    className="mb-2"
                )
        return html.Div()  # No message for non-confined aquifers
    
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
        
        # Convert input values to float in case they're strings (from CSV storage)
        ground_elevation_float = None
        max_storage_depth_float = None
        
        if ground_elevation is not None:
            try:
                ground_elevation_float = float(ground_elevation)
            except (ValueError, TypeError):
                ground_elevation_float = None
        
        if max_storage_depth is not None:
            try:
                max_storage_depth_float = float(max_storage_depth)
            except (ValueError, TypeError):
                max_storage_depth_float = None
        
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
        
        # Add filled area between MAR storage and groundwater if both values are provided
        if max_storage_depth_float is not None and ground_elevation_float is not None:
            mar_storage_line = ground_elevation - max_storage_depth
            
            # Create filled area between MAR storage line and groundwater elevation
            # We need to create a polygon that fills the area between the two lines
            months = df['month'].tolist()
            groundwater_elevations = df['elevation'].tolist()
            mar_storage_elevations = [mar_storage_line] * len(months)
            
            # Create the filled area by combining the lines
            fig.add_trace(go.Scatter(
                x=months + months[::-1],  # Forward then reverse for closed polygon
                y=groundwater_elevations + mar_storage_elevations[::-1],  # Combine both lines
                fill='toself',
                fillcolor='rgba(255, 165, 0, 0.3)',  # Orange with transparency
                line=dict(color='rgba(255,255,255,0)'),  # Transparent line
                name='Available MAR Storage',
                hovertemplate='<b>Available MAR Storage Area</b><extra></extra>',
                showlegend=True
            ))
            
            # Add the MAR storage line as a reference
            fig.add_trace(go.Scatter(
                x=months,
                y=mar_storage_elevations,
                mode='lines',
                line=dict(color='red', width=2, dash='dot'),
                name='MAR Storage Limit',
                hovertemplate='<b>%{x}</b><br>MAR Storage Limit: %{y:.1f} ft<extra></extra>',
                showlegend=True
            ))
        
        # Add horizontal lines if values are provided
        if ground_elevation_float is not None:
            # Ground surface elevation line
            fig.add_hline(
                y=ground_elevation_float,
                line_dash="dash",
                line_color="green",
                line_width=2,
                annotation_text=f"Ground Surface: {ground_elevation_float:.1f} ft",
                annotation_position="top right"
            )
        
        if max_storage_depth_float is not None and ground_elevation_float is not None:
            # Maximum MAR storage depth line (from ground surface)
            mar_storage_line = ground_elevation_float - max_storage_depth_float
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
            height=600,
            margin=dict(l=50, r=50, t=60, b=100),
            showlegend=True,
            legend=dict(
                orientation="h",
                yanchor="top",
                y=-0.15,
                xanchor="center",
                x=0.5
            )
        )
        
        # Add grid
        fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='lightgray')
        fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='lightgray')
        
        return fig
    
    # Stratigraphy Cross Section Plot Callback
    @app.callback(
        Output("stratigraphy-cross-section-plot", "figure"),
        [Input("stratigraphy-data-store", "data")],
        prevent_initial_call=False
    )
    def update_stratigraphy_cross_section(data):
        """Update the stratigraphy cross-section plot based on table data."""
        if not data:
            return go.Figure()
        
        # Define colors for different layer types
        layer_colors = {
            "Gravel": "#8B4513",      # Brown
            "Sand": "#F4A460",        # Sandy brown
            "Silt": "#D2B48C",        # Tan
            "Loam": "#DEB887",        # Burlywood
            "Clay": "#A0522D"         # Sienna
        }
        
        # Create the plot
        fig = go.Figure()
        
        # Calculate cumulative depths for layering
        cumulative_depth = 0
        layer_names = []
        layer_depths = []
        layer_colors_list = []
        
        for i, row in enumerate(data):
            layer_name = row["layer"]
            thickness = row["thickness"]
            
            # Add layer rectangle
            fig.add_trace(go.Scatter(
                x=[0, 1, 1, 0, 0],  # Rectangle coordinates
                y=[cumulative_depth, cumulative_depth, cumulative_depth + thickness, cumulative_depth + thickness, cumulative_depth],
                fill='toself',
                fillcolor=layer_colors.get(layer_name, "#808080"),  # Default gray if layer not found
                line=dict(color='black', width=1),
                name=layer_name,
                hovertemplate=f'<b>{layer_name}</b><br>Thickness: {thickness:.1f} ft<br>Depth: {cumulative_depth:.1f} - {cumulative_depth + thickness:.1f} ft<extra></extra>',
                showlegend=True
            ))
            
            # Add layer label in the middle of the layer
            fig.add_annotation(
                x=0.5,
                y=cumulative_depth + thickness/2,
                text=layer_name,
                showarrow=False,
                font=dict(size=12, color="black")
            )
            
            cumulative_depth += thickness
        
        # Update layout
        fig.update_layout(
            title={
                'text': 'Stratigraphy Cross Section',
                'x': 0.5,
                'xanchor': 'center',
                'font': {'size': 16}
            },
            xaxis_title="",
            yaxis_title="Depth (ft)",
            yaxis=dict(autorange="reversed"),  # Reverse y-axis so surface is at top
            template="plotly_white",
            height=500,
            margin=dict(l=50, r=50, t=60, b=50),
            showlegend=True,
            legend=dict(
                orientation="h",
                yanchor="top",
                y=-0.1,
                xanchor="center",
                x=0.5
            ),
            xaxis=dict(
                showgrid=False,
                showticklabels=False,
                range=[-0.1, 1.1]
            )
        )
        
        # Add grid
        fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='lightgray')
        
        return fig
    
    # XY View Plot Callback
    @app.callback(
        Output("xy-view-plot", "figure"),
        [Input("extension-length", "value"),
         Input("extension-width", "value"),
         Input("extension-rotation", "value"),
         Input("upstream-head", "value"),
         Input("downstream-head", "value")],
        prevent_initial_call=False
    )
    def update_xy_view_plot(length, width, rotation, upstream_head, downstream_head):
        """Update the XY view plot with rectangle and contour lines."""
        import numpy as np
        
        # Default values if inputs are None, and convert to float
        if length is None:
            length = 100.0
        else:
            try:
                length = float(length)
            except (ValueError, TypeError):
                length = 100.0
        
        if width is None:
            width = 50.0
        else:
            try:
                width = float(width)
            except (ValueError, TypeError):
                width = 50.0
        
        if rotation is None:
            rotation = 0.0
        else:
            try:
                rotation = float(rotation)
            except (ValueError, TypeError):
                rotation = 0.0
        
        if upstream_head is None:
            upstream_head = 10.0
        else:
            try:
                upstream_head = float(upstream_head)
            except (ValueError, TypeError):
                upstream_head = 10.0
        
        if downstream_head is None:
            downstream_head = 5.0
        else:
            try:
                downstream_head = float(downstream_head)
            except (ValueError, TypeError):
                downstream_head = 5.0
        
        # Create the plot
        fig = go.Figure()
        
        # Convert rotation to radians
        rotation_rad = np.radians(rotation)
        
        # Define rectangle corners (centered at origin, then rotated)
        half_length = length / 2
        half_width = width / 2
        
        # Original rectangle corners (before rotation)
        corners = np.array([
            [-half_length, -half_width],
            [half_length, -half_width],
            [half_length, half_width],
            [-half_length, half_width],
            [-half_length, -half_width]  # Close the rectangle
        ])
        
        # Rotation matrix
        cos_rot = np.cos(rotation_rad)
        sin_rot = np.sin(rotation_rad)
        rotation_matrix = np.array([[cos_rot, -sin_rot], [sin_rot, cos_rot]])
        
        # Rotate the rectangle
        rotated_corners = corners @ rotation_matrix.T
        
        # Add rectangle outline
        fig.add_trace(go.Scatter(
            x=rotated_corners[:, 0],
            y=rotated_corners[:, 1],
            mode='lines',
            line=dict(color='black', width=3),
            name='MAR Project Area',
            hovertemplate='<b>MAR Project Area</b><br>Length: %{x:.1f} ft<br>Width: %{y:.1f} ft<extra></extra>',
            showlegend=True
        ))
        
        # Add filled rectangle
        fig.add_trace(go.Scatter(
            x=rotated_corners[:, 0],
            y=rotated_corners[:, 1],
            fill='toself',
            fillcolor='rgba(0, 123, 255, 0.3)',
            line=dict(color='rgba(255,255,255,0)'),
            name='Project Area',
            showlegend=False,
            hoverinfo='skip'
        ))
        
        # Create contour lines (10 lines parallel to width, from upstream to downstream)
        n_contours = 10
        head_values = np.linspace(upstream_head, downstream_head, n_contours)
        
        # Define color scale from blue (high head) to red (low head)
        colors = ['#0000FF', '#0080FF', '#00FFFF', '#00FF80', '#00FF00', 
                 '#80FF00', '#FFFF00', '#FF8000', '#FF4000', '#FF0000']
        
        for i, head in enumerate(head_values):
            # Create contour line parallel to the width (perpendicular to length)
            # The contour lines run from one width side to the other
            t = np.linspace(-half_width, half_width, 50)
            
            # Create points along the width at different positions along the length
            # Position varies from -half_length to +half_length
            length_position = (i / (n_contours - 1) - 0.5) * 2 * half_length
            
            # Create points along the width
            contour_x = np.full_like(t, length_position)
            contour_y = t
            
            # Rotate the contour line
            contour_points = np.column_stack([contour_x, contour_y])
            rotated_contour = contour_points @ rotation_matrix.T
            
            # Add contour line with color based on head value
            fig.add_trace(go.Scatter(
                x=rotated_contour[:, 0],
                y=rotated_contour[:, 1],
                mode='lines',
                line=dict(color=colors[i], width=2, dash='dash'),
                name=f'Head: {head:.1f} ft',
                hovertemplate=f'<b>Head: {head:.1f} ft</b><extra></extra>',
                showlegend=False
            ))
            
            # Add label for contour line (at the middle of the line)
            label_position = np.array([length_position, 0]) @ rotation_matrix.T
            fig.add_annotation(
                x=label_position[0],
                y=label_position[1],
                text=f'{head:.1f}',
                showarrow=False,
                font=dict(size=10, color='black', family="Arial Black"),
                bgcolor="rgba(255,255,255,0.8)",
                bordercolor="black",
                borderwidth=1
            )
        
        # Add upstream and downstream labels
        # Upstream (higher head)
        upstream_center = np.array([-half_length, 0]) @ rotation_matrix.T
        fig.add_annotation(
            x=upstream_center[0],
            y=upstream_center[1],
            text=f"Upstream<br>{upstream_head:.1f} ft",
            showarrow=True,
            arrowhead=2,
            arrowcolor="green",
            font=dict(size=10, color="green"),
            bgcolor="rgba(255,255,255,0.8)",
            bordercolor="green"
        )
        
        # Downstream (lower head)
        downstream_center = np.array([half_length, 0]) @ rotation_matrix.T
        fig.add_annotation(
            x=downstream_center[0],
            y=downstream_center[1],
            text=f"Downstream<br>{downstream_head:.1f} ft",
            showarrow=True,
            arrowhead=2,
            arrowcolor="red",
            font=dict(size=10, color="red"),
            bgcolor="rgba(255,255,255,0.8)",
            bordercolor="red"
        )
        
        # Update layout
        fig.update_layout(
            title={
                'text': 'XY View - MAR Project Area with Head Contours',
                'x': 0.5,
                'xanchor': 'center',
                'font': {'size': 16}
            },
            xaxis_title="Distance (ft)",
            yaxis_title="Distance (ft)",
            template="plotly_white",
            height=500,
            margin=dict(l=50, r=50, t=60, b=50),
            showlegend=True,
            legend=dict(
                orientation="h",
                yanchor="top",
                y=-0.1,
                xanchor="center",
                x=0.5
            ),
            xaxis=dict(scaleanchor="y", scaleratio=1),  # Equal aspect ratio
            yaxis=dict(scaleanchor="x", scaleratio=1)
        )
        
        # No grid lines for cleaner appearance
        
        return fig
    
    # Callback to update Hydrogeologic Feasibility content
    @app.callback(
        Output("hydrogeologic-feasibility-content", "children"),
        [
            Input("stratigraphy-data-store", "data"),
            Input("groundwater-data-store", "data"),
            Input("aquifer-type-radio", "value"),
            Input("hydrogeology-subtabs", "active_tab"),
        ],
        prevent_initial_call=False
    )
    def update_hydrogeologic_feasibility_content(strat_data, gw_data, aquifer_type, active_tab):
        """Update the Hydrogeologic Feasibility tab content when data changes."""
        from mar_dss.app.components.hydrogeologic_feasibility_content import (
            create_hydrogeologic_feasibility_content_dynamic,
            create_loading_content
        )
        
        # Only update if we're on the feasibility tab
        if active_tab != "hydrogeologic-feasibility-tab":
            return dash.no_update
        
        try:
            # Store aquifer type
            if aquifer_type:
                dash_storage.set_data("aq_type", aquifer_type)
            
            # Generate dynamic content
            content = create_hydrogeologic_feasibility_content_dynamic()
            return content
        except Exception as e:
            import traceback
            traceback.print_exc()
            return create_loading_content(f"Error: {str(e)}")