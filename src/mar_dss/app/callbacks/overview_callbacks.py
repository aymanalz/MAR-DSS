"""
Overview tab callbacks for MAR DSS dashboard.
"""

import dash
import dash_bootstrap_components as dbc
from dash import Input, Output, html, dependencies
import mar_dss.app.utils.data_storage as dash_storage
import mar_dss.app.utils.helpers as helpers
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
            # Initial load - get saved project name or use default, and save it
            project_name = dash_storage.get_data("project_name") or ""
            dash_storage.set_data("project_name", project_name)
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
            # Initial load - get saved analysis date or use default, and save it
            analysis_date = dash_storage.get_data("analysis_date")
            if analysis_date:
                # Ensure date is in YYYY-MM-DD format
                try:
                    if isinstance(analysis_date, str) and len(analysis_date) == 10 and analysis_date[4] == '-' and analysis_date[7] == '-':
                        formatted_date = analysis_date
                    else:
                        # Try to parse and reformat the date
                        from datetime import datetime
                        parsed_date = helpers.parse_unknown_date(analysis_date)
                        formatted_date = parsed_date.strftime("%Y-%m-%d")
                    dash_storage.set_data("analysis_date", formatted_date)
                    return formatted_date
                except:
                    # If parsing fails, use today's date
                    from datetime import datetime
                    default_date = datetime.now().strftime("%Y-%m-%d")
                    dash_storage.set_data("analysis_date", default_date)
                    return default_date
            else:
                # No data in storage, use today's date
                from datetime import datetime
                default_date = datetime.now().strftime("%Y-%m-%d")
                dash_storage.set_data("analysis_date", default_date)
                return default_date
        
        # Get the current value from the input
        current_value = value if value else ""
        
        # Determine which trigger caused the callback
        trigger_id = ctx.triggered[0]["prop_id"].split(".")[0]
        trigger_prop = ctx.triggered[0]["prop_id"].split(".")[1]
        
        # Save analysis date for all triggers except initial load
        if trigger_prop != "id" and current_value:
            # Ensure date is in YYYY-MM-DD format before saving
            try:
                from datetime import datetime
                # If it's already in correct format, use it
                if isinstance(current_value, str) and len(current_value) == 10 and current_value[4] == '-' and current_value[7] == '-':
                    formatted_date = current_value
                else:
                    # Try to parse and reformat
                    parsed_date = datetime.strptime(str(current_value), "%Y-%m-%d")
                    formatted_date = parsed_date.strftime("%Y-%m-%d")
                dash_storage.set_data("analysis_date", formatted_date)
            except:
                # If formatting fails, save as is
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
            # Initial load - get saved MAR purpose selections or use default, and save it
            mar_purpose = dash_storage.get_data("mar_purpose") or ["secure_water_supply"]
            dash_storage.set_data("mar_purpose", mar_purpose)
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
            # Initial load - get saved workspace or use default, and save it
            workspace = dash_storage.get_data("workspace") or ""
            dash_storage.set_data("workspace", workspace)
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
            # Initial load - get saved filename or use default, and save it
            filename = dash_storage.get_data("filename") or ""
            dash_storage.set_data("filename", filename)
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
                import ast
                for index, row in df.iterrows():
                    key = row["key"]
                    value = row["value"]
                    
                    # Handle list values that might be stored as strings in CSV
                    if isinstance(value, str) and value.startswith('[') and value.endswith(']'):
                        try:
                            value = ast.literal_eval(value)
                        except (ValueError, SyntaxError):
                            pass  # Keep as string if parsing fails
                    
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

    # Callback for ground surface slope input - saves to data storage
    @app.callback(
        Output("ground-slope-input", "value"),
        [
            Input("ground-slope-input", "value"),
            Input("ground-slope-input", "n_blur"),
            Input("ground-slope-input", "n_submit"),
            Input("ground-slope-input", "id")
        ],
        prevent_initial_call=False
    )
    def handle_ground_slope_input(value, n_blur, n_submit, component_id):
        """Handle ground surface slope input for all triggers: value change, blur, submit, and load."""
        ctx = dash.callback_context
        
        if not ctx.triggered:
            # Initial load - get saved ground slope or use default, and save it
            ground_slope = dash_storage.get_data("ground_surface_slope") or 0.5
            dash_storage.set_data("ground_surface_slope", ground_slope)
            return ground_slope
        
        # Get the current value from the input
        current_value = value if value is not None else 0.5
        
        # Determine which trigger caused the callback
        trigger_id = ctx.triggered[0]["prop_id"].split(".")[0]
        trigger_prop = ctx.triggered[0]["prop_id"].split(".")[1]
        
        # Save ground slope for all triggers except initial load
        if trigger_prop != "id":
            dash_storage.set_data("ground_surface_slope", current_value)
        
        return current_value

    # Callback for maximum available area input - saves to data storage
    @app.callback(
        Output("max-area-input", "value"),
        [
            Input("max-area-input", "value"),
            Input("max-area-input", "n_blur"),
            Input("max-area-input", "n_submit"),
            Input("max-area-input", "id")
        ],
        prevent_initial_call=False
    )
    def handle_max_area_input(value, n_blur, n_submit, component_id):
        """Handle maximum available area input for all triggers: value change, blur, submit, and load."""
        ctx = dash.callback_context
        
        if not ctx.triggered:
            # Initial load - get saved max area or use default, and save it
            max_area = dash_storage.get_data("max_available_area") or 1.0
            dash_storage.set_data("max_available_area", max_area)
            return max_area
        
        # Get the current value from the input
        current_value = value if value is not None else 1.0
        
        # Determine which trigger caused the callback
        trigger_id = ctx.triggered[0]["prop_id"].split(".")[0]
        trigger_prop = ctx.triggered[0]["prop_id"].split(".")[1]
        
        # Save max area for all triggers except initial load
        if trigger_prop != "id":
            dash_storage.set_data("max_available_area", current_value)
        
        return current_value

    # Callback for land use dropdown - saves to data storage
    @app.callback(
        Output("land-use-dropdown", "value"),
        [
            Input("land-use-dropdown", "value"),
            Input("land-use-dropdown", "id")
        ],
        prevent_initial_call=False
    )
    def handle_land_use_selection(value, component_id):
        """Handle land use dropdown selection and save to data storage."""
        ctx = dash.callback_context
        
        if not ctx.triggered:
            # Initial load - get saved land use or use default, and save it
            land_use = dash_storage.get_data("land_use") or "Urban Residential"
            dash_storage.set_data("land_use", land_use)
            return land_use
        
        # Get the current selection
        current_selection = value if value else "Urban Residential"
        
        # Save land use selection to data storage
        dash_storage.set_data("land_use", current_selection)
        
        return current_selection

