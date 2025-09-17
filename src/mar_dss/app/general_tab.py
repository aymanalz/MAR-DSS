"""
General tab content for MAR DSS dashboard.
"""

from dash import html, dcc
import dash_bootstrap_components as dbc


def create_general_tab_content():
    """Create the content for the General tab."""
    return [
        html.H3("General Information"),
        html.P("General information about the MAR DSS system and project details."),
        
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("MAR Purpose"),
                    dbc.CardBody([
                        html.P("MAR DSS - Managed Aquifer Recharge Decision Support System"),
                        html.P("Version: 0.1.0"),
                        html.P("Author: Ayman H. Alzraiee"),
                        html.P("Email: aalzraiee@gsi-net.com"),
                        html.Hr(),
                        html.Label("Goals:", className="fw-bold"),
                        dcc.Dropdown(
                            id="goals-dropdown",
                            options=[
                                {"label": "Goal 1", "value": "goal1"},
                                {"label": "Goal 2", "value": "goal2"},
                                {"label": "Goal 3", "value": "goal3"}
                            ],
                            value="goal1",
                            style={"margin-top": "10px"}
                        )
                    ])
                ])
            ], width=6),
            
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("Project Details"),
                    dbc.CardBody([
                        html.P("This dashboard provides monitoring and analysis capabilities for managed aquifer recharge systems."),
                        html.P("Features include water level monitoring, recharge rate analysis, and water quality assessment.")
                    ])
                ])
            ], width=6)
        ], className="mt-3")
    ]
