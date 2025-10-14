"""
Environmental Impact tab component.
"""

import dash_bootstrap_components as dbc
from dash import html


def create_environmental_impact_content():
    """Create the Environmental Impact tab content."""
    return [
        html.H3("Environmental Impact Analysis", className="mb-4"),
        html.P("This section will contain environmental impact analysis tools and visualizations.", className="mb-4"),
        
        dbc.Card([
            dbc.CardHeader("Environmental Impact Assessment", className="fw-bold bg-success text-white"),
            dbc.CardBody([
                html.P("Environmental impact analysis tools will be implemented here.", className="text-muted"),
                html.Small("This section is currently under development.", className="text-muted")
            ])
        ])
    ]
