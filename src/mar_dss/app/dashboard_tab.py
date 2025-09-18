"""
Dashboard tab content for MAR DSS dashboard.
"""

from dash import html, dcc
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
import pandas as pd
import numpy as np


def create_dashboard_content():
    """Create content for Dashboard sidebar tab."""
    return html.Div([
        html.H3("Dashboard Overview"),
        html.P("Welcome to the MAR DSS Dashboard. Select a tab to begin your analysis."),
        dbc.Card([
            dbc.CardBody([
                html.H5("Quick Start Guide", className="card-title"),
                html.P("1. Configure your project details in the Overview tab"),
                html.P("2. Set up water source parameters in the Water Source tab"),
                html.P("3. Run analysis using the sidebar tools"),
                html.P("4. Review results and generate reports")
            ])
        ])
    ])
