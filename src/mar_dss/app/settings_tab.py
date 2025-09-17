"""
Settings tab content for MAR DSS dashboard.
"""

from dash import html
import dash_bootstrap_components as dbc


def create_settings_tab_content():
    """Create the content for the Settings tab."""
    return [
        html.H3("Settings"),
        html.P("Configure dashboard settings here."),
        dbc.Form([
            dbc.Row([
                dbc.Label("Update Frequency:", width=3),
                dbc.Col([
                    dbc.Select(
                        options=[
                            {"label": "Real-time", "value": "realtime"},
                            {"label": "Every 5 minutes", "value": "5min"},
                            {"label": "Every hour", "value": "1hour"},
                            {"label": "Daily", "value": "daily"}
                        ],
                        value="1hour"
                    )
                ], width=9)
            ], className="mb-3"),
            
            dbc.Row([
                dbc.Label("Data Range:", width=3),
                dbc.Col([
                    dbc.Select(
                        options=[
                            {"label": "Last 7 days", "value": "7days"},
                            {"label": "Last 30 days", "value": "30days"},
                            {"label": "Last 3 months", "value": "3months"},
                            {"label": "Last year", "value": "1year"}
                        ],
                        value="30days"
                    )
                ], width=9)
            ])
        ])
    ]
