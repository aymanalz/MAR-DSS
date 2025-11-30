"""
Callbacks for Cost calculations and display in the Engineering tab.
"""

import dash
from dash import Input, Output, html, dash_table
import dash_bootstrap_components as dbc
import pandas as pd


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
        import mar_dss.app.utils.data_storage as dash_storage
        
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
            Input("flow-capture-pump-check", "value"),
            Input("conveyance-method-radio", "value"),
            Input("distance-collection-to-sediment", "value"),
            Input("sediment-removal-pond-check", "value"),
            Input("sediment-removal-target-radio", "value"),
            Input("pumped-conveyance-storage-check", "value"),
            Input("storage-pond-check", "value"),
            Input("pumped-conveyance-infiltration-check", "value"),
            Input("infiltration-method-radio", "value"),
        ],
        prevent_initial_call=True
    )
    def update_cost_calculations(
        flow_capture_values,
        conveyance_method,
        distance_to_sediment,
        sediment_pond_values,
        sediment_target,
        pumped_storage_values,
        storage_pond_values,
        pumped_infiltration_values,
        infiltration_method,
    ):
        """Update cost calculations based on engineering inputs."""
        
        # For now, return default values
        # TODO: Implement actual cost calculations using CostCalculator

        cost_calculator = CostCalculator()
        #cost_calculator.calculate_cost()
        
        capital_cost = "$0"
        annual_maintenance_cost = "$0"
        npv_20_years = "$0"
        
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

