"""
Analysis tab component with all analysis sub-tabs.
"""

import dash_bootstrap_components as dbc
from dash import html

# Import all the analysis components
try:
    from mar_dss.app.components.dashboard_tab import create_dashboard_content
    from mar_dss.app.components.dss_algorithm_tab import create_dss_algorithm_content
    from mar_dss.app.components.decision_sensitivity_tab import create_decision_sensitivity_content
    from mar_dss.app.components.decision_interpretation_tab import create_decision_interpretation_content
    from mar_dss.app.components.scenarios_comparison_tab import create_scenarios_comparison_content
    from mar_dss.app.components.ai_generated_decision_tab import create_ai_generated_decision_content
    from mar_dss.app.components.data_export_tab import create_data_export_content
    from mar_dss.app.components.engineering_options_tab import create_cost_content
except ImportError:
    from .dashboard_tab import create_dashboard_content
    from .dss_algorithm_tab import create_dss_algorithm_content
    from .decision_sensitivity_tab import create_decision_sensitivity_content
    from .decision_interpretation_tab import create_decision_interpretation_content
    from .scenarios_comparison_tab import create_scenarios_comparison_content
    from .ai_generated_decision_tab import create_ai_generated_decision_content
    from .data_export_tab import create_data_export_content
    from .engineering_options_tab import create_cost_content


def create_analysis_tab_content():
    """Create the Analysis tab with lazy-loaded sub-tabs."""
    return [
        dbc.Tabs(
            [
                dbc.Tab(
                    label="Feasible MAR Technologies",
                    tab_id="analysis-dashboard",
                    children=create_dashboard_content(),  # Load immediately
                    label_style={
                        "color": "#ffffff", 
                        "fontWeight": "bold",
                        "backgroundColor": "#007bff",
                        "border": "1px solid #007bff"
                    },
                    active_label_style={
                        "color": "#ffffff", 
                        "backgroundColor": "#0056b3",
                        "border": "1px solid #0056b3"
                    },
                ),
                dbc.Tab(
                    label="Cost",
                    tab_id="analysis-cost",
                    children=create_cost_content(),
                    label_style={
                        "color": "#ffffff", 
                        "fontWeight": "bold",
                        "backgroundColor": "#85c1e9",
                        "border": "1px solid #85c1e9"
                    },
                    active_label_style={
                        "color": "#ffffff", 
                        "backgroundColor": "#73b3e0",
                        "border": "1px solid #73b3e0"
                    },
                ),
                dbc.Tab(
                    label="DSS Algorithm",
                    tab_id="analysis-dss-algorithm",
                    children=[html.Div(id="analysis-dss-algorithm-content", children="Loading...")],  # Lazy load
                    label_style={
                        "color": "#ffffff", 
                        "fontWeight": "bold",
                        "backgroundColor": "#28a745",
                        "border": "1px solid #28a745"
                    },
                    active_label_style={
                        "color": "#ffffff", 
                        "backgroundColor": "#1e7e34",
                        "border": "1px solid #1e7e34"
                    },
                ),
                dbc.Tab(
                    label="Decision Sensitivity",
                    tab_id="analysis-decision-sensitivity",
                    children=[html.Div(id="analysis-decision-sensitivity-content", children="Loading...")],  # Lazy load
                    label_style={
                        "color": "#ffffff", 
                        "fontWeight": "bold",
                        "backgroundColor": "#ffc107",
                        "border": "1px solid #ffc107"
                    },
                    active_label_style={
                        "color": "#ffffff", 
                        "backgroundColor": "#e0a800",
                        "border": "1px solid #e0a800"
                    },
                ),
                dbc.Tab(
                    label="Decision Interpretation",
                    tab_id="analysis-decision-interpretation",
                    children=[html.Div(id="analysis-decision-interpretation-content", children="Loading...")],  # Lazy load
                    label_style={
                        "color": "#ffffff", 
                        "fontWeight": "bold",
                        "backgroundColor": "#17a2b8",
                        "border": "1px solid #17a2b8"
                    },
                    active_label_style={
                        "color": "#ffffff", 
                        "backgroundColor": "#138496",
                        "border": "1px solid #138496"
                    },
                ),
                dbc.Tab(
                    label="Scenarios Comparison",
                    tab_id="analysis-scenarios-comparison",
                    children=[html.Div(id="analysis-scenarios-comparison-content", children="Loading...")],  # Lazy load
                    label_style={
                        "color": "#ffffff", 
                        "fontWeight": "bold",
                        "backgroundColor": "#6f42c1",
                        "border": "1px solid #6f42c1"
                    },
                    active_label_style={
                        "color": "#ffffff", 
                        "backgroundColor": "#5a32a3",
                        "border": "1px solid #5a32a3"
                    },
                ),
                dbc.Tab(
                    label="AI Generated Decision",
                    tab_id="analysis-ai-decision",
                    children=[html.Div(id="analysis-ai-decision-content", children="Loading...")],  # Lazy load
                    label_style={
                        "color": "#ffffff", 
                        "fontWeight": "bold",
                        "backgroundColor": "#fd7e14",
                        "border": "1px solid #fd7e14"
                    },
                    active_label_style={
                        "color": "#ffffff", 
                        "backgroundColor": "#e8590c",
                        "border": "1px solid #e8590c"
                    },
                ),
                dbc.Tab(
                    label="Data Export",
                    tab_id="analysis-data-export",
                    children=[html.Div(id="analysis-data-export-content", children="Loading...")],  # Lazy load
                    label_style={
                        "color": "#ffffff", 
                        "fontWeight": "bold",
                        "backgroundColor": "#6c757d",
                        "border": "1px solid #6c757d"
                    },
                    active_label_style={
                        "color": "#ffffff", 
                        "backgroundColor": "#545b62",
                        "border": "1px solid #545b62"
                    },
                ),
            ],
            id="analysis-tabs",
            active_tab="analysis-dashboard",
        )
    ]
