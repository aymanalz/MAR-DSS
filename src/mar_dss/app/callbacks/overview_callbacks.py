"""
Overview tab callbacks for MAR DSS dashboard.
"""

import dash
import dash_bootstrap_components as dbc
from dash import Input, Output, html, dependencies
import mar_dss.app.utils.data_storage as dash_storage


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
            data = dash_storage.get_data("project_name")
            project_name = data.get("project_name", "") if data else ""
            return project_name
        
        # Get the current value from the input
        current_value = value if value else ""
        
        # Determine which trigger caused the callback
        trigger_id = ctx.triggered[0]["prop_id"].split(".")[0]
        trigger_prop = ctx.triggered[0]["prop_id"].split(".")[1]
        
        # Save project name for all triggers except initial load
        if trigger_prop != "id" and current_value:
            dash_storage.set_data("Project Name", current_value)
        
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
            data = dash_storage.get_data("analysis_date")
            analysis_date = data.get("analysis_date", "") if data else ""
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
            data = dash_storage.get_data("mar_purpose")
            mar_purpose = data.get("mar_purpose", ["secure_water_supply"]) if data else ["secure_water_supply"]
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
            data = dash_storage.get_data("workspace")
            workspace = data.get("workspace", "") if data else ""
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
            data = dash_storage.get_data("filename")
            filename = data.get("filename", "") if data else ""
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
