"""
Callbacks for Cost calculations and display in the Engineering tab.
"""

import dash
from dash import Input, Output, State, html, dash_table
import dash_bootstrap_components as dbc
import pandas as pd
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
        
        # Debug: Print to see if callback is triggered
        print(f"DEBUG: update_cost_calculations called - top_tab: {top_tab}, analysis_tab: {analysis_tab}")
        
        # Only calculate if we're on the Analysis tab and Cost sub-tab is selected
        if not top_tab or not analysis_tab or top_tab != "analysis" or analysis_tab != "analysis-cost":
            print(f"DEBUG: Conditions not met - returning no_update")
            return (
                dash.no_update,
                dash.no_update,
                dash.no_update,
                dash.no_update,
                dash.no_update,
                dash.no_update,
            )
        
        print(f"DEBUG: Conditions met - proceeding with calculations")
        
        total_runoff_ft3 = dash_storage.get_data("total_runoff_ft3") or 0.0
        fraction_flow_capture = dash_storage.get_data("fraction_flow_capture") or 0.0
        runoff_volume_ft3 = float(total_runoff_ft3) * float(fraction_flow_capture)

        # storm_stat = pd.DataFrame(dash_storage.get_data("runoff_calculations_table"))
        # storm_design_depth = storm_stat.loc[storm_stat["Parameter"] == "24-hour Rainfall (inches)", "Value"].values[0]
        # drainage_basin_area_acres = storm_stat.loc[storm_stat["Parameter"] == "Area (acres)", "Value"].values[0]
        # runoff_volume_ft3 = storm_stat.loc[storm_stat["Parameter"] == "Runoff Volume (ft3)", "Value"].values[0]
        # # flow_capture_values = dash_storage.get_data("flow_capture_values") or ["flow_capture_structure", "rough_grading"]
        # # conveyance_method = dash_storage.get_data("conveyance_method") or "trapezoidal"
        distance_to_sediment_miles = dash_storage.get_data("distance_to_sediment") or 1.0
        distance_to_sediment_ft = float(distance_to_sediment_miles) * 5280.0
        distance_to_storage_pond_ft = float(dash_storage.get_data("distance_to_storage_pond_ft")) or 1.0
        # sediment_pond_values = dash_storage.get_data("sediment_pond_values") or ["trash_rack"]
        sediment_target = dash_storage.get_data("sediment_target") 
        sediment_target_display = "Medium Silt" if sediment_target == "medium_silt" else "Fine Silt"
        # pumped_storage_values = dash_storage.get_data("pumped_storage_values") or []
        # storage_pond_values = dash_storage.get_data("storage_pond_values") or []
        # pumped_infiltration_values = dash_storage.get_data("pumped_infiltration_values") or []
        # infiltration_method = dash_storage.get_data("infiltration_method") or "infiltration_basin"
        
        # For now, return default values
        # TODO: Implement actual cost calculations using CostCalculator
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
        
        capital_cost_num = cost_calculator.capital_costs_calculations.loc['Capital Total Cost',
         'Total Cost ($)']
        maintenance_cost_num = cost_calculator.maintenance_costs_calculations.loc['Annual Grand Maintenance Cost']['Total Cost ($)']
        net_val = cost_calculator.net_present_value_calculations['Total Net Present Value'].values[-1]
        capital_cost = f"${capital_cost_num:,.0f}"
        annual_maintenance_cost = f"${maintenance_cost_num:,.0f}"
        npv_20_years = f"${net_val:,.0f}"
        
        capital_cost_table = html.P("Capital Cost Table will be displayed here.")
        maintenance_cost_table = html.P(
            "Maintenance Cost Table will be displayed here."
        )
        npv_table = html.P("Net Present Value Table will be displayed here.")
        
        return (
            capital_cost,
            annual_maintenance_cost,
            npv_20_years,
            capital_cost_table,
            maintenance_cost_table,
            npv_table,
        )

