"""
Callbacks for the Analysis tab lazy loading.
"""

import dash
from dash import Input, Output, html

# Import all the analysis components
try:
    from mar_dss.app.components.dss_algorithm_tab import create_dss_algorithm_content
    from mar_dss.app.components.decision_sensitivity_tab import create_decision_sensitivity_content
    from mar_dss.app.components.decision_interpretation_tab import create_decision_interpretation_content
    from mar_dss.app.components.scenarios_comparison_tab import create_scenarios_comparison_content
    from mar_dss.app.components.ai_generated_decision_tab import create_ai_generated_decision_content
    from mar_dss.app.components.data_export_tab import create_data_export_content
except ImportError:
    from ..components.dss_algorithm_tab import create_dss_algorithm_content
    from ..components.decision_sensitivity_tab import create_decision_sensitivity_content
    from ..components.decision_interpretation_tab import create_decision_interpretation_content
    from ..components.scenarios_comparison_tab import create_scenarios_comparison_content
    from ..components.ai_generated_decision_tab import create_ai_generated_decision_content
    from ..components.data_export_tab import create_data_export_content


def setup_analysis_callbacks(app):
    """Set up callbacks for lazy loading analysis tab content."""
    
    @app.callback(
        Output("analysis-dss-algorithm-content", "children"),
        [Input("analysis-tabs", "active_tab")],
        prevent_initial_call=True
    )
    def load_dss_algorithm_content(active_tab):
        if active_tab == "analysis-dss-algorithm":
            return create_dss_algorithm_content()
        return "Loading..."
    
    @app.callback(
        Output("analysis-decision-sensitivity-content", "children"),
        [Input("analysis-tabs", "active_tab")],
        prevent_initial_call=True
    )
    def load_decision_sensitivity_content(active_tab):
        if active_tab == "analysis-decision-sensitivity":
            return create_decision_sensitivity_content()
        return "Loading..."
    
    @app.callback(
        Output("analysis-decision-interpretation-content", "children"),
        [Input("analysis-tabs", "active_tab")],
        prevent_initial_call=True
    )
    def load_decision_interpretation_content(active_tab):
        if active_tab == "analysis-decision-interpretation":
            return create_decision_interpretation_content()
        return "Loading..."
    
    @app.callback(
        Output("analysis-scenarios-comparison-content", "children"),
        [Input("analysis-tabs", "active_tab")],
        prevent_initial_call=True
    )
    def load_scenarios_comparison_content(active_tab):
        if active_tab == "analysis-scenarios-comparison":
            return create_scenarios_comparison_content()
        return "Loading..."
    
    @app.callback(
        Output("analysis-ai-decision-content", "children"),
        [Input("analysis-tabs", "active_tab")],
        prevent_initial_call=True
    )
    def load_ai_decision_content(active_tab):
        if active_tab == "analysis-ai-decision":
            return create_ai_generated_decision_content()
        return "Loading..."
    
    @app.callback(
        Output("analysis-data-export-content", "children"),
        [Input("analysis-tabs", "active_tab")],
        prevent_initial_call=True
    )
    def load_data_export_content(active_tab):
        if active_tab == "analysis-data-export":
            return create_data_export_content()
        return "Loading..."
