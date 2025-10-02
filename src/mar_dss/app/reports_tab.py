"""
Reports tab content for MAR DSS dashboard.
"""

import dash_bootstrap_components as dbc
from dash import html


def create_reports_tab_content():
    """Create the content for the Reports tab."""
    return [
        html.H3("Reports"),
        html.P("Generate and download reports here."),
        dbc.Button("Generate Report", color="primary", className="mt-3"),
    ]
