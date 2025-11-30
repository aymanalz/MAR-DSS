"""
Callbacks for Cost calculations and display in the Engineering tab.
"""

import dash
from dash import Input, Output, html
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

