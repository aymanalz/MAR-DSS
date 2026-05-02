"""
Decision Sensitivity tab content for MAR DSS dashboard.

This tab allows users to perform sensitivity analysis on input parameters
to understand how changes affect DSS decision outcomes.
"""

import dash_bootstrap_components as dbc
from dash import dcc, html


def create_decision_sensitivity_content():
    """Create content for Decision Sensitivity sidebar tab."""
    
    return html.Div(
        [
            html.H4("Decision Sensitivity Analysis", className="mb-3", style={"fontSize": "1.3rem"}),
            html.P(
                "Investigate how changes in input parameters affect decision outcomes. "
                "Select a parameter below and run sensitivity analysis to see how it impacts "
                "MAR option statuses, rankings, and scores.",
                className="text-muted mb-4 small",
            ),
            
            # Parameter Selection Section
            dbc.Card([
                dbc.CardHeader([
                    html.H5("1. Select Parameter", className="mb-0", style={"fontSize": "1.1rem"}),
                ], className="bg-primary text-white py-2"),
                dbc.CardBody([
                    html.Label("Parameter to Analyze:", className="fw-bold mb-2 small"),
                    dcc.Dropdown(
                        id="sensitivity-parameter-selector",
                        placeholder="Select a parameter...",
                        className="mb-3",
                    ),
                    dbc.Tooltip(
                        "DSS input or derived quantity to vary while holding others fixed",
                        target="sensitivity-parameter-selector",
                        placement="top",
                    ),
                    html.Div(id="sensitivity-variation-settings"),
                ], style={"padding": "1rem"}),
            ], className="mb-3"),
            
            # Analysis Controls
            dbc.Card([
                dbc.CardHeader([
                    html.H5("2. Run Analysis", className="mb-0", style={"fontSize": "1.1rem"}),
                ], className="bg-success text-white py-2"),
                dbc.CardBody([
                    html.P(
                        "Configure variation settings above, then click the button below to run sensitivity analysis. "
                        "This may take a few minutes depending on the number of variation points.",
                        className="text-muted small mb-3",
                    ),
                    dbc.Button(
                        "Run Sensitivity Analysis",
                        id="sensitivity-run-button",
                        color="success",
                        className="w-100",
                        n_clicks=0,
                        title="Run tornado / status analysis for the selected parameter range",
                    ),
                    html.Div(id="sensitivity-progress", className="mt-3"),
                ], style={"padding": "1rem"}),
            ], className="mb-3"),
            
            # Results Section
            html.Div(id="sensitivity-results-container", className="mb-3"),
            
            # Info Alert
            dbc.Alert([
                html.H6("How to Use Sensitivity Analysis", className="alert-heading"),
                html.P([
                    "1. Select a parameter from the dropdown above.",
                    html.Br(),
                    "2. Configure variation settings (for numeric parameters).",
                    html.Br(),
                    "3. Click 'Run Sensitivity Analysis' to start the analysis.",
                    html.Br(),
                    "4. Review the results to understand parameter impact on decisions.",
                ], className="mb-0 small"),
            ], color="info", className="mt-3"),
        ],
        style={"padding": "1rem"}
    )
