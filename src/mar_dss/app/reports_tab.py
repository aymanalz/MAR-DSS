"""
Reports tab content for MAR DSS dashboard.
"""

from dash import html
import dash_bootstrap_components as dbc


def create_reports_tab_content():
    """Create the content for the Reports tab."""
    return [
        html.H3("Reports"),
        html.P("Generate and download reports here."),
        dbc.Button("Generate Report", color="primary", 
                 className="mt-3")
    ]
