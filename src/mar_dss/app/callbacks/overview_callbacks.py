"""
Overview tab callbacks for MAR DSS dashboard.
"""

import dash
import dash_bootstrap_components as dbc
from dash import Input, Output, html, dependencies
import mar_dss.app.utils.data_storage as dash_storage
import os
import pandas as pd

# Import the overview content creation function
try:
    from mar_dss.app.components.overview_tab import create_overview_content
except ImportError:
    from ..components.overview_tab import create_overview_content


def setup_overview_callbacks(app):
    """Set up all overview-related callbacks."""
    
    # Combined callback for project name input - handles all triggers
    @app.callback(
        Output("project-name-input", "value"),
        [
            Input("project-name-input", "value"),
            Input("project-name-input", "n_blur"),
            Input("project-name-input", "n_submit"),
            Input("project-name-input", "id")
        ],
        prevent_initial_call=False
    )
    def handle_project_name(value, n_blur, n_submit, component_id):
        """Handle project name input for all triggers: value change, blur, submit, and load."""
        ctx = dash.callback_context
        
        if not ctx.triggered:
            # Initial load - get saved project name
            project_name = dash_storage.get_data("project_name") or ""
            return project_name
        
        # Get the current value from the input
        current_value = value if value else ""
        
        # Determine which trigger caused the callback
        trigger_id = ctx.triggered[0]["prop_id"].split(".")[0]
        trigger_prop = ctx.triggered[0]["prop_id"].split(".")[1]
        
        # Save project name for all triggers except initial load
        if trigger_prop != "id" and current_value:
            dash_storage.set_data("project_name", current_value)
        
        return current_value

    # Combined callback for analysis date input - handles all triggers
    @app.callback(
        Output("analysis-date-input", "value"),
        [
            Input("analysis-date-input", "value"),
            Input("analysis-date-input", "n_blur"),
            Input("analysis-date-input", "n_submit"),
            Input("analysis-date-input", "id")
        ],
        prevent_initial_call=False
    )
    def handle_analysis_date(value, n_blur, n_submit, component_id):
        """Handle analysis date input for all triggers: value change, blur, submit, and load."""
        ctx = dash.callback_context
        
        if not ctx.triggered:
            # Initial load - get saved analysis date
            analysis_date = dash_storage.get_data("analysis_date") or ""
            return analysis_date
        
        # Get the current value from the input
        current_value = value if value else ""
        
        # Determine which trigger caused the callback
        trigger_id = ctx.triggered[0]["prop_id"].split(".")[0]
        trigger_prop = ctx.triggered[0]["prop_id"].split(".")[1]
        
        # Save analysis date for all triggers except initial load
        if trigger_prop != "id" and current_value:
            dash_storage.set_data("analysis_date", current_value)
        
        return current_value

    # Callback for MAR purpose checklist - saves selections to data storage
    @app.callback(
        Output("mar-purpose-checklist", "value"),
        [
            Input("mar-purpose-checklist", "value"),
            Input("mar-purpose-checklist", "id")
        ],
        prevent_initial_call=False
    )
    def handle_mar_purpose_selections(value, component_id):
        """Handle MAR purpose checklist selections and save to data storage."""
        ctx = dash.callback_context
        
        if not ctx.triggered:
            # Initial load - get saved MAR purpose selections
            mar_purpose = dash_storage.get_data("mar_purpose") or ["secure_water_supply"]
            return mar_purpose
        
        # Get the current selections
        current_selections = value if value else []
        
        # Save MAR purpose selections to data storage
        if current_selections:
            dash_storage.set_data("mar_purpose", current_selections)
        
        return current_selections

    # Add callback for map interactions to update location title
    @app.callback(
        Output("location-card-header", "children"),
        [Input("location-map", "relayoutData")],
    )
    def update_location_title(relayout_data):
        """Update the location card title based on map interactions."""
        if relayout_data and "mapbox.center" in relayout_data:
            center = relayout_data["mapbox.center"]
            lat = center["lat"]
            lon = center["lon"]

            # Import the function from components.water_source_tab
            try:
                from mar_dss.app.components.water_source_tab import (
                    get_location_details,
                )
            except ImportError:
                from ..components.water_source_tab import get_location_details

            location_name = get_location_details(lat, lon)
            return f"Project Location - {location_name}"

        # Default fallback
        return "Project Location - Sacramento, California, United States"

    # Callback for workspace input - saves to data storage
    @app.callback(
        Output("workspace-input", "value"),
        [
            Input("workspace-input", "value"),
            Input("workspace-input", "n_blur"),
            Input("workspace-input", "n_submit"),
            Input("workspace-input", "id")
        ],
        prevent_initial_call=False
    )
    def handle_workspace_input(value, n_blur, n_submit, component_id):
        """Handle workspace input for all triggers: value change, blur, submit, and load."""
        ctx = dash.callback_context
        
        if not ctx.triggered:
            # Initial load - get saved workspace
            workspace = dash_storage.get_data("workspace") or ""
            return workspace
        
        # Get the current value from the input
        current_value = value if value else ""
        
        # Determine which trigger caused the callback
        trigger_id = ctx.triggered[0]["prop_id"].split(".")[0]
        trigger_prop = ctx.triggered[0]["prop_id"].split(".")[1]
        
        # Save workspace for all triggers except initial load
        if trigger_prop != "id" and current_value:
            dash_storage.set_data("workspace", current_value)
        
        return current_value

    # Callback for filename input - saves to data storage
    @app.callback(
        Output("filename-input", "value"),
        [
            Input("filename-input", "value"),
            Input("filename-input", "n_blur"),
            Input("filename-input", "n_submit"),
            Input("filename-input", "id")
        ],
        prevent_initial_call=False
    )
    def handle_filename_input(value, n_blur, n_submit, component_id):
        """Handle filename input for all triggers: value change, blur, submit, and load."""
        ctx = dash.callback_context
        
        if not ctx.triggered:
            # Initial load - get saved filename
            filename = dash_storage.get_data("filename") or ""
            return filename
        
        # Get the current value from the input
        current_value = value if value else ""
        
        # Determine which trigger caused the callback
        trigger_id = ctx.triggered[0]["prop_id"].split(".")[0]
        trigger_prop = ctx.triggered[0]["prop_id"].split(".")[1]
        
        # Save filename for all triggers except initial load
        if trigger_prop != "id" and current_value:
            dash_storage.set_data("filename", current_value)
        
        return current_value

    # Callback for Open button - load project from file
    @app.callback(
        Output("main-content", "children", allow_duplicate=True),
        [Input("btn-open", "n_clicks")],
        prevent_initial_call=True
    )
    def handle_open_project(n_clicks):
        """Handle opening a project from file."""
        if n_clicks:
            data = dash_storage.get_data_storage()
            if "workspace" in data.keys():
                workspace = data["workspace"]
            else:
                print("No workspace found")
                return [
                    dbc.Alert(
                        "No workspace found",
                        color="danger",
                        className="mb-3"
                    )
                ] + create_overview_content()
            if "filename" in data.keys():
                filename = data["filename"]
            else:
                print("No filename found")
                return [
                    dbc.Alert(
                        "No filename found",
                        color="danger",
                        className="mb-3"
                    )
                ] + create_overview_content()
            
            fn = os.path.join(workspace, filename)
            if not os.path.exists(fn):
                print(f"File {fn} does not exist")
                return [
                    dbc.Alert(
                        f"File {fn} does not exist",
                        color="danger",
                        className="mb-3"
                    )
                ] + create_overview_content()
            try:
                df = pd.read_csv(fn)
                print(f"Loaded CSV with {len(df)} rows")
                for index, row in df.iterrows():
                    key = row["key"]
                    value = row["value"]
                    print(f"Setting data: {key} = {value}")
                    dash_storage.set_data(key, value)

                # Return success message and overview content
                overview_content = create_overview_content()
                return [
                    dbc.Alert(
                        f"Project loaded successfully from {fn}",
                        color="success",
                        className="mb-3"
                    )
                ] + overview_content
            except Exception as e:
                overview_content = create_overview_content()
                return [
                    dbc.Alert(
                        f"Error loading project: {str(e)}",
                        color="danger",
                        className="mb-3"
                    )
                ] + overview_content
        return dash.no_update

