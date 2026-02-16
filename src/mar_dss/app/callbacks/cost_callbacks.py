"""
Callbacks for Cost calculations and display in the Engineering tab.
"""

import dash
from dash import Input, Output, State, html, dash_table, dcc
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.graph_objects as go
import mar_dss.app.utils.data_storage as dash_storage


try:
    from mar_dss.app.callbacks.cost_calculator import CostCalculator
except ImportError:
    from .cost_calculator import CostCalculator


def setup_cost_callbacks(app):
    """Set up all cost-related callbacks."""
    
    # Callback to display water source in Design Metrics
    @app.callback(
        Output("design-metrics-water-source-display", "children"),
        [
            Input("top-tabs", "active_tab"),
        ],
        prevent_initial_call=False
    )
    def update_water_source_display(active_tab):
        """Update water source display in Design Metrics card."""
        import mar_dss.app.utils.data_storage as dash_storage
        
        # Get water source from data storage
        stored_value = dash_storage.get_data("water_source")
        
        # Map values to display labels
        water_source_labels = {
            "surface_water_sources": "(1) Surface Water Sources (streams, Reservoir, canals)",
            "urban_stormwater_runoff": "(2) Urban Stormwater Runoff",
            "rural_agricultural_runoff": "(3) Rural/Agricultural Runoff",
            "reclaimed_water": "(4) Reclaimed Water",
            "other_groundwater_basin": "(5) Other Groundwater Basin",
            "other_non_conventional_sources": "(6) Other Non-Conventional Sources"
        }
        
        if stored_value and stored_value in water_source_labels:
            return water_source_labels[stored_value]
        return "Not selected"
    
    # Callback to save hydrologic design method to data storage
    @app.callback(
        Output("hydrologic-design-method-radio", "value"),
        [
            Input("hydrologic-design-method-radio", "value"),
            Input("hydrologic-design-method-radio", "id")
        ],
        prevent_initial_call=False
    )
    def handle_hydrologic_design_method(value, component_id):
        """Handle hydrologic design method selection and save to data storage."""
        ctx = dash.callback_context
        
        if not ctx.triggered:
            # Initial load - get saved value or use default, and save it
            design_method = dash_storage.get_data("hydrologic_design_method") or "user_supplied"
            dash_storage.set_data("hydrologic_design_method", design_method)
            return design_method
        
        current_selection = value if value else "user_supplied"
        dash_storage.set_data("hydrologic_design_method", current_selection)
        return current_selection
    
    # Callback to save peak flow available input to data storage
    @app.callback(
        Output("peak-flow-available-input", "value"),
        [
            Input("peak-flow-available-input", "value"),
            Input("peak-flow-available-input", "n_blur"),
            Input("peak-flow-available-input", "n_submit"),
            Input("peak-flow-available-input", "id")
        ],
        prevent_initial_call=False
    )
    def handle_peak_flow_available(value, n_blur, n_submit, component_id):
        """Handle peak flow available input and save to data storage."""
        ctx = dash.callback_context
        
        if not ctx.triggered:
            # Initial load - get saved value or use default, and save it
            peak_flow = dash_storage.get_data("total_runoff_ft3") or 0.0
            dash_storage.set_data("total_runoff_ft3", peak_flow)
            return peak_flow
        
        current_value = value if value is not None else 0.0
        dash_storage.set_data("total_runoff_ft3", current_value)
        return current_value
    
    # Callback to save fraction flow capture input to data storage
    @app.callback(
        Output("fraction-flow-capture-input", "value"),
        [
            Input("fraction-flow-capture-input", "value"),
            Input("fraction-flow-capture-input", "n_blur"),
            Input("fraction-flow-capture-input", "n_submit"),
            Input("fraction-flow-capture-input", "id")
        ],
        prevent_initial_call=False
    )
    def handle_fraction_flow_capture(value, n_blur, n_submit, component_id):
        """Handle fraction flow capture input and save to data storage."""
        ctx = dash.callback_context
        
        if not ctx.triggered:
            # Initial load - get saved value or use default, and save it
            fraction = dash_storage.get_data("fraction_flow_capture") or 0.0
            dash_storage.set_data("fraction_flow_capture", fraction)
            return fraction
        
        current_value = value if value is not None else 0.0
        dash_storage.set_data("fraction_flow_capture", current_value)
        return current_value
    
    # Callback to save distance to storage pond input to data storage
    @app.callback(
        Output("distance-to-storage-pond-input", "value"),
        [
            Input("distance-to-storage-pond-input", "value"),
            Input("distance-to-storage-pond-input", "n_blur"),
            Input("distance-to-storage-pond-input", "n_submit"),
            Input("distance-to-storage-pond-input", "id")
        ],
        prevent_initial_call=False
    )
    def handle_distance_to_storage_pond(value, n_blur, n_submit, component_id):
        """Handle distance to storage pond input and save to data storage."""
        ctx = dash.callback_context
        
        if not ctx.triggered:
            # Initial load - get saved value or use default, and save it
            distance = dash_storage.get_data("distance_to_storage_pond_ft") or 500.0
            dash_storage.set_data("distance_to_storage_pond_ft", distance)
            return distance
        
        current_value = value if value is not None else 500.0
        dash_storage.set_data("distance_to_storage_pond_ft", current_value)
        return current_value
    
    # Callback to calculate and display design flow rate
    @app.callback(
        Output("design-flow-rate-display", "children"),
        [
            Input("peak-flow-available-input", "value"),
            Input("fraction-flow-capture-input", "value"),
        ],
        prevent_initial_call=False
    )
    def update_design_flow_rate(peak_flow, fraction):
        """Calculate and display design flow rate."""
        if peak_flow is None:
            peak_flow = 0.0
        if fraction is None:
            fraction = 0.0
        
        try:
            peak_flow = float(peak_flow)
            fraction = float(fraction)
            design_flow_rate = peak_flow * fraction
            return f"Design Flow Rate is: {design_flow_rate:.2f}"
        except (ValueError, TypeError):
            return "Design Flow Rate is: 0.0"
    
    # Callback to display water source data table
    @app.callback(
        Output("water-source-data-table", "children"),
        [
            Input("top-tabs", "active_tab"),
        ],
        prevent_initial_call=False
    )
    def update_water_source_data_table(active_tab):
        """Update water source data table in Design Metrics card."""
        
        
        # Get all water source data from storage
        water_source = dash_storage.get_data("water_source") or "Not set"
        proximity_distance = dash_storage.get_data("proximity_distance")
        water_conveyance = dash_storage.get_data("water_conveyance") or "Not set"
        water_ownership = dash_storage.get_data("water_ownership") or "Not set"
        pumping_needed = dash_storage.get_data("pumping_needed") or "Not set"
        # Map water source value to label
        water_source_labels = {
            "surface_water_sources": "(1) Surface Water Sources (streams, Reservoir, canals)",
            "urban_stormwater_runoff": "(2) Urban Stormwater Runoff",
            "rural_agricultural_runoff": "(3) Rural/Agricultural Runoff",
            "reclaimed_water": "(4) Reclaimed Water",
            "other_groundwater_basin": "(5) Other Groundwater Basin",
            "other_non_conventional_sources": "(6) Other Non-Conventional Sources"
        }
        water_source_display = water_source_labels.get(water_source, water_source)
        
        # Map water conveyance value to label
        conveyance_labels = {
            "open_canals_ditches": "Open canals/ditches",
            "pipelines": "Pipelines",
            "direct_diversion": "Direct Diversion",
            "other": "Other"
        }
        water_conveyance_display = conveyance_labels.get(water_conveyance, water_conveyance)
        
        # Map water ownership value to label
        ownership_labels = {
            "legal_rights": "Legal Rights",
            "none": "None"
        }
        water_ownership_display = ownership_labels.get(water_ownership, water_ownership)
        
        # Map pumping needed value to label
        pumping_labels = {
            "yes": "Yes",
            "no": "No"
        }
        pumping_needed_display = pumping_labels.get(pumping_needed, pumping_needed)
        
        # Format proximity distance
        if proximity_distance is not None:
            proximity_display = f"{proximity_distance} miles"
        else:
            proximity_display = "Not set"
        
        # Create table data
        table_data = [
            {"Parameter": "Water Source", "Value": water_source_display},
            {"Parameter": "Proximity Distance", "Value": proximity_display},
            {"Parameter": "Water Conveyance", "Value": water_conveyance_display},
            {"Parameter": "Water Ownership", "Value": water_ownership_display},
            {"Parameter": "Pumping Needed", "Value": pumping_needed_display},
        ]
        
        # Create DataTable
        table = dash_table.DataTable(
            data=table_data,
            columns=[
                {"name": "Parameter", "id": "Parameter"},
                {"name": "Value", "id": "Value"}
            ],
            style_cell={
                "textAlign": "left",
                "padding": "10px",
                "fontSize": "14px",
                "fontFamily": "Arial, sans-serif"
            },
            style_header={
                "backgroundColor": "#2c3e50",
                "color": "white",
                "fontWeight": "bold",
                "textAlign": "center"
            },
            style_data={
                "whiteSpace": "normal",
                "height": "auto",
                "border": "1px solid #dee2e6"
            },
            style_data_conditional=[
                {
                    "if": {"row_index": "odd"},
                    "backgroundColor": "#f8f9fa"
                }
            ],
            style_cell_conditional=[
                {
                    "if": {"column_id": "Parameter"},
                    "width": "40%",
                    "fontWeight": "bold"
                },
                {
                    "if": {"column_id": "Value"},
                    "width": "60%"
                }
            ],
        )
        
        return table
    
    # Callback to save flow capture checklist to data storage
    @app.callback(
        Output("flow-capture-pump-check", "value"),
        [
            Input("flow-capture-pump-check", "value"),
            Input("flow-capture-pump-check", "id")
        ],
        prevent_initial_call=False
    )
    def handle_flow_capture_checklist(value, component_id):
        """Handle flow capture checklist and save to data storage."""
        ctx = dash.callback_context
        
        if not ctx.triggered:
            # Initial load - get saved value or use default, and save it
            flow_capture = dash_storage.get_data("flow_capture_values") or ["flow_capture_structure", "rough_grading"]
            dash_storage.set_data("flow_capture_values", flow_capture)
            return flow_capture
        
        current_selection = value if value else []
        dash_storage.set_data("flow_capture_values", current_selection)
        return current_selection
    
    # Callback to save conveyance method to data storage
    @app.callback(
        Output("conveyance-method-radio", "value"),
        [
            Input("conveyance-method-radio", "value"),
            Input("conveyance-method-radio", "id")
        ],
        prevent_initial_call=False
    )
    def handle_conveyance_method(value, component_id):
        """Handle conveyance method selection and save to data storage."""
        ctx = dash.callback_context
        
        if not ctx.triggered:
            # Initial load - get saved value or use default, and save it
            method = dash_storage.get_data("conveyance_method") or "trapezoidal"
            dash_storage.set_data("conveyance_method", method)
            return method
        
        current_selection = value if value else "trapezoidal"
        dash_storage.set_data("conveyance_method", current_selection)
        return current_selection
    
    # Callback to save distance to sediment pond to data storage
    @app.callback(
        Output("distance-collection-to-sediment", "value"),
        [
            Input("distance-collection-to-sediment", "value"),
            Input("distance-collection-to-sediment", "n_blur"),
            Input("distance-collection-to-sediment", "n_submit"),
            Input("distance-collection-to-sediment", "id")
        ],
        prevent_initial_call=False
    )
    def handle_distance_to_sediment(value, n_blur, n_submit, component_id):
        """Handle distance to sediment pond input and save to data storage."""
        ctx = dash.callback_context
        
        if not ctx.triggered:
            # Initial load - get saved value or use default, and save it
            distance = dash_storage.get_data("distance_to_sediment") or 1.0
            dash_storage.set_data("distance_to_sediment", distance)
            return distance
        
        current_value = value if value is not None else 1.0
        dash_storage.set_data("distance_to_sediment", current_value)
        return current_value
    
    # Callback to save "Remove Sediment Removal Pond" checkbox to data storage
    @app.callback(
        Output("remove-sediment-removal-pond-check", "value"),
        [
            Input("remove-sediment-removal-pond-check", "value"),
            Input("remove-sediment-removal-pond-check", "id")
        ],
        prevent_initial_call=False
    )
    def handle_remove_sediment_pond_checkbox(value, component_id):
        """Handle remove sediment removal pond checkbox and save to data storage."""
        ctx = dash.callback_context
        
        if not ctx.triggered:
            # Initial load - get saved value or use default, and save it
            remove_sediment = dash_storage.get_data("remove_sediment_removal_pond") or False
            dash_storage.set_data("remove_sediment_removal_pond", remove_sediment)
            return remove_sediment
        
        current_value = value if value is not None else False
        dash_storage.set_data("remove_sediment_removal_pond", current_value)
        return current_value
    
    # Callback to enable/disable sediment removal pond components based on checkbox
    @app.callback(
        [
            Output("sediment-removal-pond-check-wrapper", "style"),
            Output("sediment-removal-target-radio-wrapper", "style"),
        ],
        [
            Input("remove-sediment-removal-pond-check", "value"),
        ],
        prevent_initial_call=False
    )
    def handle_sediment_pond_components_disabled(remove_sediment):
        """Enable/disable sediment removal pond components based on checkbox."""
        if remove_sediment is None:
            remove_sediment = False
        
        # If "Remove Sediment Removal Pond" is checked, disable all components
        if remove_sediment:
            disabled_style = {
                "opacity": "0.5",
                "pointerEvents": "none",
                "cursor": "not-allowed"
            }
        else:
            disabled_style = {
                "opacity": "1",
                "pointerEvents": "auto"
            }
        
        return disabled_style, disabled_style
    
    # Callback to save sediment removal pond checklist to data storage
    @app.callback(
        Output("sediment-removal-pond-check", "value"),
        [
            Input("sediment-removal-pond-check", "value"),
            Input("sediment-removal-pond-check", "id")
        ],
        prevent_initial_call=False
    )
    def handle_sediment_removal_pond_checklist(value, component_id):
        """Handle sediment removal pond checklist and save to data storage."""
        ctx = dash.callback_context
        
        if not ctx.triggered:
            # Initial load - get saved value or use default, and save it
            sediment_pond = dash_storage.get_data("sediment_pond_values") or ["trash_rack"]
            dash_storage.set_data("sediment_pond_values", sediment_pond)
            return sediment_pond
        
        current_selection = value if value else []
        dash_storage.set_data("sediment_pond_values", current_selection)
        return current_selection
    
    # Callback to save sediment removal target to data storage
    @app.callback(
        Output("sediment-removal-target-radio", "value"),
        [
            Input("sediment-removal-target-radio", "value"),
            Input("sediment-removal-target-radio", "id")
        ],
        prevent_initial_call=False
    )
    def handle_sediment_removal_target(value, component_id):
        """Handle sediment removal target selection and save to data storage."""
        ctx = dash.callback_context
        
        if not ctx.triggered:
            # Initial load - get saved value or use default, and save it
            target = dash_storage.get_data("sediment_target") or "medium_silt"
            dash_storage.set_data("sediment_target", target)
            return target
        
        current_selection = value if value else "medium_silt"
        dash_storage.set_data("sediment_target", current_selection)
        return current_selection
    
    # Callback to save pumped conveyance to storage checklist to data storage
    @app.callback(
        Output("pumped-conveyance-storage-check", "value"),
        [
            Input("pumped-conveyance-storage-check", "value"),
            Input("pumped-conveyance-storage-check", "id")
        ],
        prevent_initial_call=False
    )
    def handle_pumped_conveyance_storage_checklist(value, component_id):
        """Handle pumped conveyance to storage checklist and save to data storage."""
        ctx = dash.callback_context
        
        if not ctx.triggered:
            # Initial load - get saved value or use default, and save it
            pumped_storage = dash_storage.get_data("pumped_storage_values") or [
                "pipeline_cost",
                "pumping_bag_filter_cost",
                "controls",
                "electrical_system"
            ]
            dash_storage.set_data("pumped_storage_values", pumped_storage)
            return pumped_storage
        
        current_selection = value if value else []
        dash_storage.set_data("pumped_storage_values", current_selection)
        return current_selection
    
    # Callback to save storage pond checklist to data storage
    @app.callback(
        Output("storage-pond-check", "value"),
        [
            Input("storage-pond-check", "value"),
            Input("storage-pond-check", "id")
        ],
        prevent_initial_call=False
    )
    def handle_storage_pond_checklist(value, component_id):
        """Handle storage pond checklist and save to data storage."""
        ctx = dash.callback_context
        
        if not ctx.triggered:
            # Initial load - get saved value or use default, and save it
            storage_pond = dash_storage.get_data("storage_pond_values") or ["storage_pond_construction"]
            dash_storage.set_data("storage_pond_values", storage_pond)
            return storage_pond
        
        current_selection = value if value else []
        dash_storage.set_data("storage_pond_values", current_selection)
        return current_selection
    
    # Callback to enable/disable "Pumped Conveyance To Storage Pond" components based on Storage Pond
    @app.callback(
        [
            Output("pumped-conveyance-storage-check-wrapper", "style"),
            Output("distance-to-storage-pond-input-wrapper", "style"),
        ],
        [
            Input("storage-pond-check", "value"),
        ],
        prevent_initial_call=False
    )
    def handle_pumped_conveyance_storage_disabled(storage_pond_values):
        """Enable/disable pumped conveyance to storage pond components based on Storage Pond."""
        if storage_pond_values is None:
            storage_pond_values = []
        
        # Check if "storage_pond_construction" is in the list
        storage_pond_enabled = "storage_pond_construction" in storage_pond_values
        
        # If Storage Pond is False (not enabled), disable all components
        if not storage_pond_enabled:
            disabled_style = {
                "opacity": "0.5",
                "pointerEvents": "none",
                "cursor": "not-allowed"
            }
        else:
            disabled_style = {
                "opacity": "1",
                "pointerEvents": "auto"
            }
        
        return disabled_style, disabled_style
    
    # Callback to save pumped conveyance to infiltration checklist to data storage
    @app.callback(
        Output("pumped-conveyance-infiltration-check", "value"),
        [
            Input("pumped-conveyance-infiltration-check", "value"),
            Input("pumped-conveyance-infiltration-check", "id")
        ],
        prevent_initial_call=False
    )
    def handle_pumped_conveyance_infiltration_checklist(value, component_id):
        """Handle pumped conveyance to infiltration checklist and save to data storage."""
        ctx = dash.callback_context
        
        if not ctx.triggered:
            # Initial load - get saved value or use default, and save it
            pumped_infiltration = dash_storage.get_data("pumped_infiltration_values") or [
                "infiltration_pipeline_cost",
                "infiltration_pumping_bag_filter_cost",
                "infiltration_controls",
                "infiltration_electrical_system"
            ]
            dash_storage.set_data("pumped_infiltration_values", pumped_infiltration)
            return pumped_infiltration
        
        current_selection = value if value else []
        dash_storage.set_data("pumped_infiltration_values", current_selection)
        return current_selection
    
    # Callback to save infiltration method to data storage
    @app.callback(
        Output("infiltration-method-radio", "value"),
        [
            Input("infiltration-method-radio", "value"),
            Input("infiltration-method-radio", "id")
        ],
        prevent_initial_call=False
    )
    def handle_infiltration_method(value, component_id):
        """Handle infiltration method selection and save to data storage."""
        ctx = dash.callback_context
        
        if not ctx.triggered:
            # Initial load - get saved value or use default, and save it
            method = dash_storage.get_data("infiltration_method") or "infiltration_basin"
            dash_storage.set_data("infiltration_method", method)
            return method
        
        current_selection = value if value else "infiltration_basin"
        dash_storage.set_data("infiltration_method", current_selection)
        return current_selection
    
    # Callback to save maximum infiltration area to data storage
    @app.callback(
        Output("max-infiltration-area-input", "value"),
        [
            Input("max-infiltration-area-input", "value"),
            Input("max-infiltration-area-input", "n_blur"),
            Input("max-infiltration-area-input", "n_submit"),
            Input("max-infiltration-area-input", "id")
        ],
        prevent_initial_call=False
    )
    def handle_max_infiltration_area(value, n_blur, n_submit, component_id):
        """Handle maximum infiltration area input and save to data storage."""
        ctx = dash.callback_context
        
        if not ctx.triggered:
            # Initial load - get saved value or calculate default (60% of max available area)
            max_infiltration_area = dash_storage.get_data("max_infiltration_area")
            if max_infiltration_area is None:
                max_available_area = dash_storage.get_data("max_available_area")
                if max_available_area is None:
                    max_available_area = 1.0
                else:
                    try:
                        max_available_area = float(max_available_area)
                    except (ValueError, TypeError):
                        max_available_area = 1.0
                max_infiltration_area = round(0.6 * max_available_area, 2)
            else:
                try:
                    max_infiltration_area = float(max_infiltration_area)
                except (ValueError, TypeError):
                    max_available_area = dash_storage.get_data("max_available_area")
                    if max_available_area is None:
                        max_available_area = 1.0
                    else:
                        try:
                            max_available_area = float(max_available_area)
                        except (ValueError, TypeError):
                            max_available_area = 1.0
                    max_infiltration_area = round(0.6 * max_available_area, 2)
            dash_storage.set_data("max_infiltration_area", max_infiltration_area)
            return max_infiltration_area
        
        # User changed the value
        if value is not None:
            try:
                value = float(value)
            except (ValueError, TypeError):
                value = None
            if value is not None:
                dash_storage.set_data("max_infiltration_area", value)
                return value
        
        # Return saved value if no new value provided
        saved_value = dash_storage.get_data("max_infiltration_area")
        if saved_value is None:
            max_available_area = dash_storage.get_data("max_available_area")
            if max_available_area is None:
                max_available_area = 1.0
            else:
                try:
                    max_available_area = float(max_available_area)
                except (ValueError, TypeError):
                    max_available_area = 1.0
            saved_value = round(0.6 * max_available_area, 2)
            dash_storage.set_data("max_infiltration_area", saved_value)
        else:
            try:
                saved_value = float(saved_value)
            except (ValueError, TypeError):
                max_available_area = dash_storage.get_data("max_available_area")
                if max_available_area is None:
                    max_available_area = 1.0
                else:
                    try:
                        max_available_area = float(max_available_area)
                    except (ValueError, TypeError):
                        max_available_area = 1.0
                saved_value = round(0.6 * max_available_area, 2)
                dash_storage.set_data("max_infiltration_area", saved_value)
        return saved_value
    
    @app.callback(
        [
            Output("capital-cost-display", "children"),
            Output("annual-maintenance-cost-display", "children"),
            Output("npv-20-years-display", "children"),
            Output("capital-cost-table-content", "children"),
            Output("maintenance-cost-table-content", "children"),
            Output("npv-table-content", "children"),
        ],
        [
            Input("top-tabs", "active_tab"),
            Input("analysis-tabs", "active_tab"),
        ],
        prevent_initial_call=False
    )
    def update_cost_calculations(
        top_tab,
        analysis_tab,
    ):
        """Update cost calculations based on engineering inputs."""        
        
        # Only calculate if we're on the Analysis tab and Cost sub-tab is selected
        if not top_tab or not analysis_tab or top_tab != "analysis" or analysis_tab != "analysis-cost":
          
            return (
                dash.no_update,
                dash.no_update,
                dash.no_update,
                dash.no_update,
                dash.no_update,
                dash.no_update,
            )
       
        # Check if cost data already exists (from integrated analysis)
        existing_capital_costs = dash_storage.get_data("capital_cost_num")
        existing_capital_df = dash_storage.get_data("capital_costs_calculations_df")
        existing_maintenance_df = dash_storage.get_data("maintenance_costs_calculations_df")
        existing_npv_df = dash_storage.get_data("npv_calculations_df")
        
        if existing_capital_costs is not None and existing_capital_df is not None:
            # Cost data already exists from integrated analysis - use it without recalculating
            print("Using existing cost data from integrated analysis (skipping recalculation)")
            capital_cost_num = existing_capital_costs
            cost_calculator = None  # We'll use stored DataFrames instead
            
            # Get maintenance costs and NPV from storage
            maintenance_cost_num = dash_storage.get_data("maintenance_cost_num")
            net_val_dict = dash_storage.get_data("net_val") or {}
        else:
            # Cost data doesn't exist - run calculation
            print("Cost data not found - running cost calculation...")
            total_runoff_ft3 = dash_storage.get_data("total_runoff_ft3") or 0.0
            fraction_flow_capture = dash_storage.get_data("fraction_flow_capture") or 0.0
            runoff_volume_ft3 = float(total_runoff_ft3) * float(fraction_flow_capture)
            distance_to_sediment_miles = dash_storage.get_data("distance_to_sediment") or 1.0
            distance_to_sediment_ft = float(distance_to_sediment_miles) * 5280.0
            distance_to_storage_pond_ft = float(dash_storage.get_data("distance_to_storage_pond_ft")) or 1.0
            sediment_target = dash_storage.get_data("sediment_target") 
            sediment_target_display = "Medium Silt" if sediment_target == "medium_silt" else "Fine Silt"
            
            storm_design_depth = 1.8
            cost_calculator = CostCalculator(
            water_source="stormwater", storm_design_depth=storm_design_depth,
            drainage_basin_area_acres=35, # todo: this should be renamed to MAR site area.
            total_storm_volume_af=6.52, # todo: not used, remove if not needed
            basin_soil_type_infiltration_rate_in_per_hr=0.2,
            total_runoff_volume_ft3=runoff_volume_ft3,
            fine_sediment_removal_goal= sediment_target_display,
            distance_collection_to_sediment_pond_ft=distance_to_sediment_ft,
            distance_sediment_to_storage_pond_ft=distance_to_storage_pond_ft,
            dry_well_infiltration_rate_in_per_hr=5,
            dry_well_transfer_rate_gpm=50,
            injection_well_transfer_rate_gpm=50,
            number_of_injection_wells=5,
            collection_to_sediment_removal__conveyance_method="trapezoidal",
            dry_well_diameter_ft=6,
            recharge_method="dry_well"
        )
            cost_calculator.calculate_cost()
            cols = ['Spreading Pond Cost ($)', 'Injection Wells Cost ($)', 'Dry Wells Cost ($)']
            capital_cost_num = cost_calculator.capital_costs_calculations.loc['Capital Total Cost',
             cols]
            dash_storage.set_data("capital_cost_num",capital_cost_num)

            cols = [ 'Spreading Pond Maintenance Cost ($)', 'Injection Wells Maintenance Cost ($)', 'Dry Wells Maintenance Cost ($)']
            maintenance_cost_num = cost_calculator.maintenance_costs_calculations.loc['Annual Grand Maintenance Cost', cols]
            dash_storage.set_data("maintenance_cost_num",maintenance_cost_num)
            cols =['Spreading Pond Net Present Value ($)',
           'Injection Wells Net Present Value ($)',
           'Dry Wells Net Present Value ($)']
            net_val = cost_calculator.net_present_value_calculations[cols].values[-1]
            net_val_dict = {}
            for i, col in enumerate(cols):
                net_val_dict[col] =net_val[i]
            net_val = net_val_dict
            dash_storage.set_data("net_val",net_val_dict)
            
            # Store DataFrames for future use
            dash_storage.set_data("capital_costs_calculations_df", cost_calculator.capital_costs_calculations)
            dash_storage.set_data("maintenance_costs_calculations_df", cost_calculator.maintenance_costs_calculations)
            dash_storage.set_data("npv_calculations_df", cost_calculator.net_present_value_calculations)
        
        # Get selected technology to determine which cost to display
        selected_technology = dash_storage.get_data("selected_mar_technology")
        
        # Format costs - show all three or one based on selection
        def format_cost_display(cost_data, cost_type="Capital"):
            """Format cost display to show 3 values or 1 based on selection."""
            if cost_data is None:
                return "$0"
            
            if isinstance(cost_data, pd.Series):
                # We have three cost values
                # Get column names based on cost type
                if cost_type == "Capital":
                    spreading_col = "Spreading Pond Cost ($)"
                    injection_col = "Injection Wells Cost ($)"
                    dry_well_col = "Dry Wells Cost ($)"
                elif cost_type == "Maintenance":
                    spreading_col = "Spreading Pond Maintenance Cost ($)"
                    injection_col = "Injection Wells Maintenance Cost ($)"
                    dry_well_col = "Dry Wells Maintenance Cost ($)"
                elif cost_type == "NPV":
                    spreading_col = "Spreading Pond Net Present Value ($)"
                    injection_col = "Injection Wells Net Present Value ($)"
                    dry_well_col = "Dry Wells Net Present Value ($)"
                else:
                    spreading_col = "Spreading Pond Cost ($)"
                    injection_col = "Injection Wells Cost ($)"
                    dry_well_col = "Dry Wells Cost ($)"
                
                if selected_technology is None:
                    # Show all three values
                    spreading = cost_data.get(spreading_col, 0) if spreading_col in cost_data.index else 0
                    injection = cost_data.get(injection_col, 0) if injection_col in cost_data.index else 0
                    dry_well = cost_data.get(dry_well_col, 0) if dry_well_col in cost_data.index else 0
                    
                    spreading_str = f"${float(spreading):,.0f}" if pd.notna(spreading) and spreading != 0 else "$0"
                    injection_str = f"${float(injection):,.0f}" if pd.notna(injection) and injection != 0 else "$0"
                    dry_well_str = f"${float(dry_well):,.0f}" if pd.notna(dry_well) and dry_well != 0 else "$0"
                    return html.Div([
                        html.Div(f"Spreading: {spreading_str}", style={"margin-bottom": "5px"}),
                        html.Div(f"Injection: {injection_str}", style={"margin-bottom": "5px"}),
                        html.Div(f"Dry Well: {dry_well_str}")
                    ])
                else:
                    # Show selected technology cost
                    tech_mapping = {
                        "spreading_basins": spreading_col,
                        "Surface Recharge": spreading_col,
                        "injection_wells": injection_col,
                        "Injection Well": injection_col,
                        "dry_wells": dry_well_col,
                        "Dry Well": dry_well_col,
                    }
                    
                    # Try to find matching column
                    cost_column = None
                    for tech_key, col_name in tech_mapping.items():
                        if (tech_key.lower() in str(selected_technology).lower() or 
                            str(selected_technology).lower() in tech_key.lower()):
                            if col_name in cost_data.index:
                                cost_column = col_name
                                break
                    
                    if cost_column and cost_column in cost_data.index:
                        cost_value = cost_data[cost_column]
                        return f"${float(cost_value):,.0f}" if pd.notna(cost_value) else "$0"
                    else:
                        # Fallback: show all three
                        spreading = cost_data.get(spreading_col, 0) if spreading_col in cost_data.index else 0
                        injection = cost_data.get(injection_col, 0) if injection_col in cost_data.index else 0
                        dry_well = cost_data.get(dry_well_col, 0) if dry_well_col in cost_data.index else 0
                        
                        spreading_str = f"${float(spreading):,.0f}" if pd.notna(spreading) and spreading != 0 else "$0"
                        injection_str = f"${float(injection):,.0f}" if pd.notna(injection) and injection != 0 else "$0"
                        dry_well_str = f"${float(dry_well):,.0f}" if pd.notna(dry_well) and dry_well != 0 else "$0"
                        return html.Div([
                            html.Div(f"Spreading: {spreading_str}", style={"margin-bottom": "5px"}),
                            html.Div(f"Injection: {injection_str}", style={"margin-bottom": "5px"}),
                            html.Div(f"Dry Well: {dry_well_str}")
                        ])
            else:
                # Single value (old format)
                return f"${float(cost_data):,.0f}" if pd.notna(cost_data) else "$0"
        
        capital_cost = format_cost_display(capital_cost_num, "Capital")
        annual_maintenance_cost = format_cost_display(maintenance_cost_num, "Maintenance")
        
        # Format NPV display - convert dict to Series for format_cost_display
        if net_val_dict:
            npv_series = pd.Series(net_val_dict)
            npv_20_years = format_cost_display(npv_series, "NPV")
        else:
            npv_20_years = "$0"
        
        # Create Capital Cost Table
        # Use stored DataFrame if available, otherwise use cost_calculator
        if existing_capital_df is not None:
            capital_df = existing_capital_df.copy()
        else:
            capital_df = cost_calculator.capital_costs_calculations.copy()
        # Reset index to make it a column
        capital_df = capital_df.reset_index()
        # Rename the index column if it exists
        if 'index' in capital_df.columns:
            capital_df = capital_df.rename(columns={'index': 'Row Label'})
        
        # Format numeric columns
        if 'Number of Units' in capital_df.columns:
            def format_units(x):
                try:
                    if pd.notna(x) and x != '' and str(x).strip() != '':
                        return f"{float(x):.2f}"
                    return ''
                except (ValueError, TypeError):
                    return ''
            capital_df['Number of Units'] = capital_df['Number of Units'].apply(format_units)
        
        # Format technology-specific cost columns
        # Check what columns actually exist
        available_cost_columns = [col for col in capital_df.columns if 'Cost ($)' in col]
        cost_columns = ['Spreading Pond Cost ($)', 'Injection Wells Cost ($)', 'Dry Wells Cost ($)']
        
        def format_cost(x):
            try:
                if pd.notna(x) and x != '' and str(x).strip() != '':
                    return f"{float(x):,.1f}"
                return ''
            except (ValueError, TypeError):
                return ''
        
        # Format each cost column if it exists
        for col in cost_columns:
            if col in capital_df.columns:
                try:
                    capital_df[col] = capital_df[col].apply(format_cost)
                except Exception as e:
                    print(f"Warning: Could not format column {col}: {e}")
                    continue
        
        # Fill NaN values with empty strings for better display
        capital_df = capital_df.fillna('')
        
        # Get unique categories and assign colors
        categories = capital_df['Category'].dropna().unique() if 'Category' in capital_df.columns else []
        # Color palette for categories
        category_colors = [
            '#e8f5e9',  # Light green
            '#e3f2fd',  # Light blue
            '#fff3e0',  # Light orange
            '#f3e5f5',  # Light purple
            '#fce4ec',  # Light pink
            '#e0f2f1',  # Light teal
            '#fff9c4',  # Light yellow
            '#e1f5fe',  # Light cyan
        ]
        
        # Create conditional styling for categories
        category_styles = []
        for idx, category in enumerate(categories):
            if category and str(category).strip() != '':
                color = category_colors[idx % len(category_colors)]
                category_styles.append({
                    'if': {
                        'filter_query': f'{{Category}} = "{category}"'
                    },
                    'backgroundColor': color
                })
        
        # Add summary row styling
        summary_styles = [
            {
                'if': {
                    'filter_query': '{Row Label} contains "Total" || {Row Label} contains "Subtotal" || {Row Label} contains "Capital" || {Item} = null'
                },
                'backgroundColor': '#ecf0f1',
                'fontWeight': 'bold'
            }
        ]
        
        capital_cost_table = dash_table.DataTable(
            data=capital_df.to_dict('records'),
            columns=[
                {'name': col, 'id': col} for col in capital_df.columns
            ],
            style_cell={
                'textAlign': 'left',
                'padding': '10px',
                'fontFamily': 'Arial, sans-serif'
            },
            style_header={
                'backgroundColor': '#2c3e50',
                'color': 'white',
                'fontWeight': 'bold',
                'textAlign': 'center'
            },
            style_data={
                'whiteSpace': 'normal',
                'height': 'auto'
            },
            style_data_conditional=category_styles + summary_styles,
            page_size=50
        )
        
        # Create Maintenance Cost Table
        # Use stored DataFrame if available, otherwise use cost_calculator
        if existing_maintenance_df is not None:
            maintenance_df = existing_maintenance_df.copy()
        else:
            maintenance_df = cost_calculator.maintenance_costs_calculations.copy()
        # Reset index to make it a column
        maintenance_df = maintenance_df.reset_index()
        # Rename the index column if it exists
        if 'index' in maintenance_df.columns:
            maintenance_df = maintenance_df.rename(columns={'index': 'Row Label'})
        
        # Format numeric columns
        if 'Number of Units' in maintenance_df.columns:
            def format_units(x):
                try:
                    if pd.notna(x) and x != '' and str(x).strip() != '':
                        return f"{float(x):.2f}"
                    return ''
                except (ValueError, TypeError):
                    return ''
            maintenance_df['Number of Units'] = maintenance_df['Number of Units'].apply(format_units)
        
        # Format technology-specific maintenance cost columns
        maintenance_cost_columns = ['Spreading Pond Maintenance Cost ($)', 'Injection Wells Maintenance Cost ($)', 'Dry Wells Maintenance Cost ($)']
        def format_cost(x):
            try:
                if pd.notna(x) and x != '' and str(x).strip() != '':
                    return f"{float(x):,.1f}"
                return ''
            except (ValueError, TypeError):
                return ''
        
        # Format each maintenance cost column if it exists
        for col in maintenance_cost_columns:
            if col in maintenance_df.columns:
                try:
                    maintenance_df[col] = maintenance_df[col].apply(format_cost)
                except Exception as e:
                    print(f"Warning: Could not format column {col}: {e}")
                    continue
        
        # Fill NaN values with empty strings for better display
        maintenance_df = maintenance_df.fillna('')
        
        # Get unique categories and assign colors (same as capital cost table)
        maintenance_categories = maintenance_df['Category'].dropna().unique() if 'Category' in maintenance_df.columns else []
        
        # Create conditional styling for categories
        maintenance_category_styles = []
        for idx, category in enumerate(maintenance_categories):
            if category and str(category).strip() != '':
                color = category_colors[idx % len(category_colors)]
                maintenance_category_styles.append({
                    'if': {
                        'filter_query': f'{{Category}} = "{category}"'
                    },
                    'backgroundColor': color
                })
        
        # Add summary row styling for maintenance costs
        maintenance_summary_styles = [
            {
                'if': {
                    'filter_query': '{Row Label} contains "Total" || {Row Label} contains "Subtotal" || {Row Label} contains "Maintenance" || {Item} = null'
                },
                'backgroundColor': '#ecf0f1',
                'fontWeight': 'bold'
            }
        ]
        
        maintenance_cost_table = dash_table.DataTable(
            data=maintenance_df.to_dict('records'),
            columns=[
                {'name': col, 'id': col} for col in maintenance_df.columns
            ],
            style_cell={
                'textAlign': 'left',
                'padding': '10px',
                'fontFamily': 'Arial, sans-serif'
            },
            style_header={
                'backgroundColor': '#2c3e50',
                'color': 'white',
                'fontWeight': 'bold',
                'textAlign': 'center'
            },
            style_data={
                'whiteSpace': 'normal',
                'height': 'auto'
            },
            style_data_conditional=maintenance_category_styles + maintenance_summary_styles,
            page_size=50
        )
        
        # Create Net Present Value Table and Plot
        # Use stored DataFrame if available, otherwise use cost_calculator
        if existing_npv_df is not None:
            npv_df = existing_npv_df.copy()
        else:
            npv_df = cost_calculator.net_present_value_calculations.copy()
        # Reset index to make Year a column
        npv_df = npv_df.reset_index()
        # Rename the index column if it exists
        if 'index' in npv_df.columns:
            npv_df = npv_df.rename(columns={'index': 'Year'})
        elif 'Year' not in npv_df.columns and npv_df.index.name == 'Year':
            npv_df.index.name = None
            npv_df = npv_df.reset_index()
            npv_df = npv_df.rename(columns={'index': 'Year'})
        
        # Keep a copy of numeric values for the plot
        npv_df_plot = npv_df.copy()
        
        # Get selected technology to determine which NPV to display
        selected_technology = dash_storage.get_data("selected_mar_technology")
        
        # NPV column names
        npv_columns = [
            'Spreading Pond Net Present Value ($)',
            'Injection Wells Net Present Value ($)',
            'Dry Wells Net Present Value ($)'
        ]
        
        # Format NPV columns for table display
        def format_npv(x):
            try:
                if pd.notna(x) and x != '' and str(x).strip() != '':
                    return f"${float(x):,.1f}"
                return ''
            except (ValueError, TypeError):
                return ''
        
        # Format all NPV columns that exist
        for col in npv_columns:
            if col in npv_df.columns:
                npv_df[col] = npv_df[col].apply(format_npv)
        
        # Fill NaN values with empty strings for better display
        npv_df = npv_df.fillna('')
        
        # Create the bar plot
        npv_plot = go.Figure()
        
        # Map technology to column name
        tech_to_column = {
            "spreading_basins": "Spreading Pond Net Present Value ($)",
            "Surface Recharge": "Spreading Pond Net Present Value ($)",
            "injection_wells": "Injection Wells Net Present Value ($)",
            "Injection Well": "Injection Wells Net Present Value ($)",
            "dry_wells": "Dry Wells Net Present Value ($)",
            "Dry Well": "Dry Wells Net Present Value ($)",
        }
        
        if selected_technology is None:
            # Show all three technologies
            colors = ['#3498db', '#2ecc71', '#e74c3c']
            for i, col in enumerate(npv_columns):
                if col in npv_df_plot.columns:
                    npv_plot.add_trace(go.Bar(
                        x=npv_df_plot['Year'],
                        y=npv_df_plot[col],
                        name=col.replace(' Net Present Value ($)', ''),
                        marker_color=colors[i],
                        text=[f"${val:,.0f}" for val in npv_df_plot[col]],
                        textposition='outside',
                        hovertemplate=f'Year: %{{x}}<br>{col}: $%{{y:,.0f}}<extra></extra>'
                    ))
            npv_plot.update_layout(
                title='Net Present Value Over 20 Years',
                xaxis_title='Year',
                yaxis_title='Net Present Value ($)',
                xaxis=dict(tickmode='linear', tick0=1, dtick=1),
                yaxis=dict(tickformat='$,.0f'),
                height=500,
                autosize=True,
                margin=dict(l=50, r=50, t=50, b=50),
                plot_bgcolor='white',
                paper_bgcolor='white',
                barmode='group'
            )
        else:
            # Show selected technology only
            cost_column = None
            for tech_key, col_name in tech_to_column.items():
                if (tech_key.lower() in str(selected_technology).lower() or 
                    str(selected_technology).lower() in tech_key.lower()):
                    if col_name in npv_df_plot.columns:
                        cost_column = col_name
                        break
            
            if cost_column and cost_column in npv_df_plot.columns:
                npv_plot.add_trace(go.Bar(
                    x=npv_df_plot['Year'],
                    y=npv_df_plot[cost_column],
                    marker_color='#3498db',
                    text=[f"${val:,.0f}" for val in npv_df_plot[cost_column]],
                    textposition='outside',
                    hovertemplate=f'Year: %{{x}}<br>{cost_column}: $%{{y:,.0f}}<extra></extra>'
                ))
            else:
                # Fallback: show all three
                colors = ['#3498db', '#2ecc71', '#e74c3c']
                for i, col in enumerate(npv_columns):
                    if col in npv_df_plot.columns:
                        npv_plot.add_trace(go.Bar(
                            x=npv_df_plot['Year'],
                            y=npv_df_plot[col],
                            name=col.replace(' Net Present Value ($)', ''),
                            marker_color=colors[i],
                            text=[f"${val:,.0f}" for val in npv_df_plot[col]],
                            textposition='outside',
                            hovertemplate=f'Year: %{{x}}<br>{col}: $%{{y:,.0f}}<extra></extra>'
                        ))
            
            npv_plot.update_layout(
                title='Net Present Value Over 20 Years',
                xaxis_title='Year',
                yaxis_title='Net Present Value ($)',
                xaxis=dict(tickmode='linear', tick0=1, dtick=1),
                yaxis=dict(tickformat='$,.0f'),
                height=500,
                autosize=True,
                margin=dict(l=50, r=50, t=50, b=50),
                plot_bgcolor='white',
                paper_bgcolor='white'
            )
        
        npv_table = dash_table.DataTable(
            data=npv_df.to_dict('records'),
            columns=[
                {'name': col, 'id': col} for col in npv_df.columns
            ],
            style_cell={
                'textAlign': 'left',
                'padding': '10px',
                'fontFamily': 'Arial, sans-serif'
            },
            style_header={
                'backgroundColor': '#2c3e50',
                'color': 'white',
                'fontWeight': 'bold',
                'textAlign': 'center'
            },
            style_data={
                'whiteSpace': 'normal',
                'height': 'auto'
            },
            style_data_conditional=[
                {
                    'if': {'row_index': 'odd'},
                    'backgroundColor': '#f8f9fa'
                },
                {
                    'if': {'row_index': len(npv_df) - 1},
                    'backgroundColor': '#ecf0f1',
                    'fontWeight': 'bold'
                }
            ],
            page_size=25
        )
        
        # Combine table and plot in a row layout
        npv_table = dbc.Container([
            dbc.Row([
                dbc.Col([
                    html.H5("Net Present Value Chart", className="mb-3"),
                    dcc.Graph(
                        figure=npv_plot,
                        id='npv-chart',
                        style={'height': '500px'}
                    )
                ], width=12)
            ]),
            dbc.Row([
                dbc.Col([
                    html.H5("Net Present Value Table", className="mb-3"),
                    npv_table
                ], width=12)
            ])
        ], fluid=True)
        
        return (
            capital_cost,
            annual_maintenance_cost,
            npv_20_years,
            capital_cost_table,
            maintenance_cost_table,
            npv_table,
        )

