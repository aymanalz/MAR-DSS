"""
Main dashboard application for MAR DSS.
"""

import webbrowser
import dash
from dash import dcc, html, Input, Output, State, callback
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json


class DashboardApp:
    """Main dashboard application class."""
    
    def __init__(self):
        """Initialize the dashboard application."""
        self.app = dash.Dash(
            __name__,
            external_stylesheets=[
                "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css"
            ],
            suppress_callback_exceptions=True
        )
        self.current_theme = "CERULEAN"
        self.setup_layout()
        self.setup_callbacks()
    
    def create_sample_data(self):
        """Create sample data for demonstration."""
        # Generate sample time series data
        dates = pd.date_range(start='2023-01-01', end='2023-12-31', freq='D')
        
        # Water level data
        water_levels = np.random.normal(100, 10, len(dates)) + \
                      5 * np.sin(np.arange(len(dates)) * 2 * np.pi / 365)
        
        # Recharge data
        recharge_data = np.random.exponential(2, len(dates)) * \
                       (1 + 0.5 * np.sin(np.arange(len(dates)) * 2 * np.pi / 365))
        
        # Quality data
        quality_data = np.random.normal(7.5, 0.5, len(dates))
        
        return {
            'dates': dates,
            'water_levels': water_levels,
            'recharge_data': recharge_data,
            'quality_data': quality_data
        }
    
    def create_water_level_chart(self, data):
        """Create water level time series chart."""
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=data['dates'],
            y=data['water_levels'],
            mode='lines+markers',
            name='Water Level',
            line=dict(color='#1f77b4', width=2),
            marker=dict(size=4)
        ))
        
        fig.update_layout(
            title='Water Level Over Time',
            xaxis_title='Date',
            yaxis_title='Water Level (m)',
            hovermode='x unified',
            template='plotly_white'
        )
        
        return fig
    
    def create_recharge_chart(self, data):
        """Create recharge rate chart."""
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=data['dates'],
            y=data['recharge_data'],
            name='Recharge Rate',
            marker_color='#2ca02c'
        ))
        
        fig.update_layout(
            title='Recharge Rate Over Time',
            xaxis_title='Date',
            yaxis_title='Recharge Rate (mm/day)',
            template='plotly_white'
        )
        
        return fig
    
    def create_quality_chart(self, data):
        """Create water quality chart."""
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=data['dates'],
            y=data['quality_data'],
            mode='lines+markers',
            name='pH Level',
            line=dict(color='#ff7f0e', width=2),
            marker=dict(size=4)
        ))
        
        fig.update_layout(
            title='Water Quality (pH) Over Time',
            xaxis_title='Date',
            yaxis_title='pH Level',
            hovermode='x unified',
            template='plotly_white'
        )
        
        return fig
    
    def create_summary_cards(self, data):
        """Create summary cards for the dashboard."""
        current_level = data['water_levels'][-1]
        avg_recharge = np.mean(data['recharge_data'])
        current_quality = data['quality_data'][-1]
        
        cards = [
            dbc.Card([
                dbc.CardBody([
                    html.H4(f"{current_level:.1f} m", className="card-title"),
                    html.P("Current Water Level", className="card-text"),
                    html.I(className="fas fa-tint fa-2x text-primary")
                ])
            ], className="text-center mb-3"),
            
            dbc.Card([
                dbc.CardBody([
                    html.H4(f"{avg_recharge:.2f} mm/day", className="card-title"),
                    html.P("Average Recharge Rate", className="card-text"),
                    html.I(className="fas fa-cloud-rain fa-2x text-success")
                ])
            ], className="text-center mb-3"),
            
            dbc.Card([
                dbc.CardBody([
                    html.H4(f"{current_quality:.2f}", className="card-title"),
                    html.P("Current pH Level", className="card-text"),
                    html.I(className="fas fa-flask fa-2x text-warning")
                ])
            ], className="text-center mb-3")
        ]
        
        return cards
    
    def setup_layout(self):
        """Set up the main dashboard layout."""
        # Sample data
        data = self.create_sample_data()
        
        # Create charts
        water_level_chart = self.create_water_level_chart(data)
        recharge_chart = self.create_recharge_chart(data)
        quality_chart = self.create_quality_chart(data)
        summary_cards = self.create_summary_cards(data)
        
        # Main layout
        self.app.layout = html.Div([
            # Dynamic theme CSS link
            html.Link(
                id="theme-css",
                rel="stylesheet",
                href="https://cdn.jsdelivr.net/npm/bootswatch@5.3.2/dist/cerulean/bootstrap.min.css"
            ),
            dbc.Container([
            # Header with Theme Selector
            dbc.Row([
                dbc.Col([
                    html.Div([
                        html.H1("MAR DSS Dashboard", className="text-center mb-4"),
                        html.Div([
                            html.Label("Theme", className="small text-muted"),
                            dbc.Select(
                                id="theme-selector",
                                options=[
                                    {"label": "Cerulean", "value": "CERULEAN"},
                                    {"label": "Darkly", "value": "DARKLY"},
                                    {"label": "Flatly", "value": "FLATLY"},
                                    {"label": "Cyborg", "value": "CYBORG"},
                                    {"label": "Slate", "value": "SLATE"}
                                ],
                                value="CERULEAN",
                                size="sm",
                                style={"width": "120px"}
                            )
                        ], className="position-absolute", 
                           style={"top": "10px", "right": "20px"})
                    ], className="position-relative"),
                    html.Hr()
                ])
            ]),
            
            # Main Content Area with Sidebar and Tabs
            dbc.Row([
                # Left Sidebar
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader("Navigation"),
                        dbc.CardBody([
                            dbc.Nav([
                                dbc.NavItem([
                                    dbc.NavLink("Dashboard", id="nav-dashboard", 
                                              href="#", active=True)
                                ]),
                                dbc.NavItem([
                                    dbc.NavLink("Water Levels", id="nav-water-levels", 
                                              href="#")
                                ]),
                                dbc.NavItem([
                                    dbc.NavLink("Recharge Rates", id="nav-recharge", 
                                              href="#")
                                ]),
                                dbc.NavItem([
                                    dbc.NavLink("Water Quality", id="nav-quality", 
                                              href="#")
                                ]),
                                dbc.NavItem([
                                    dbc.NavLink("Data Export", id="nav-export", 
                                              href="#")
                                ])
                            ], vertical=True, pills=True)
                        ])
                    ])
                ], width=3),
                
                # Right Content Area with Tabs
                dbc.Col([
                    # Top Navigation Tabs (now on the right)
                    dbc.Card([
                        dbc.CardHeader([
                            dbc.Tabs([
                                dbc.Tab(label="Overview", tab_id="overview"),
                                dbc.Tab(label="Analysis", tab_id="analysis"),
                                dbc.Tab(label="Reports", tab_id="reports"),
                                dbc.Tab(label="Settings", tab_id="settings")
                            ], id="top-tabs", active_tab="overview")
                        ]),
                        dbc.CardBody([
                            # Overview Tab Content
                            html.Div(id="overview-content", children=[
                                dbc.Row([
                                    dbc.Col(card, width=4) for card in summary_cards
                                ], className="mb-4"),
                                
                                dbc.Row([
                                    dbc.Col([
                                        dcc.Graph(figure=water_level_chart)
                                    ], width=6),
                                    dbc.Col([
                                        dcc.Graph(figure=recharge_chart)
                                    ], width=6)
                                ]),
                                
                                dbc.Row([
                                    dbc.Col([
                                        dcc.Graph(figure=quality_chart)
                                    ], width=12)
                                ], className="mt-4")
                            ]),
                            
                            # Analysis Tab Content
                            html.Div(id="analysis-content", children=[
                                html.H3("Analysis Tools"),
                                html.P("Advanced analysis tools will be implemented here."),
                                dbc.Alert("Analysis features coming soon!", 
                                        color="info", className="mt-3")
                            ], style={"display": "none"}),
                            
                            # Reports Tab Content
                            html.Div(id="reports-content", children=[
                                html.H3("Reports"),
                                html.P("Generate and download reports here."),
                                dbc.Button("Generate Report", color="primary", 
                                         className="mt-3")
                            ], style={"display": "none"}),
                            
                            # Settings Tab Content
                            html.Div(id="settings-content", children=[
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
                            ], style={"display": "none"})
                        ])
                    ])
                ], width=9)
            ])
        ], fluid=True, id="app-container")
        ])
    
    def setup_callbacks(self):
        """Set up dashboard callbacks."""
        
        @self.app.callback(
            [Output("overview-content", "style"),
             Output("analysis-content", "style"),
             Output("reports-content", "style"),
             Output("settings-content", "style")],
            [Input("top-tabs", "active_tab")]
        )
        def update_tab_content(active_tab):
            """Update content based on active tab."""
            styles = [
                {"display": "none"},
                {"display": "none"},
                {"display": "none"},
                {"display": "none"}
            ]
            
            if active_tab == "overview":
                styles[0] = {"display": "block"}
            elif active_tab == "analysis":
                styles[1] = {"display": "block"}
            elif active_tab == "reports":
                styles[2] = {"display": "block"}
            elif active_tab == "settings":
                styles[3] = {"display": "block"}
            
            return styles
        
        @self.app.callback(
            [Output("theme-selector", "value"),
             Output("theme-css", "href")],
            [Input("theme-selector", "value")]
        )
        def update_theme(selected_theme):
            """Update theme based on selection."""
            if selected_theme:
                self.current_theme = selected_theme
                
                # Map theme names to their CDN URLs
                theme_urls = {
                    "CERULEAN": "https://cdn.jsdelivr.net/npm/bootswatch@5.3.2/dist/cerulean/bootstrap.min.css",
                    "DARKLY": "https://cdn.jsdelivr.net/npm/bootswatch@5.3.2/dist/darkly/bootstrap.min.css",
                    "FLATLY": "https://cdn.jsdelivr.net/npm/bootswatch@5.3.2/dist/flatly/bootstrap.min.css",
                    "CYBORG": "https://cdn.jsdelivr.net/npm/bootswatch@5.3.2/dist/cyborg/bootstrap.min.css",
                    "SLATE": "https://cdn.jsdelivr.net/npm/bootswatch@5.3.2/dist/slate/bootstrap.min.css"
                }
                
                theme_url = theme_urls.get(selected_theme, theme_urls["CERULEAN"])
                return selected_theme, theme_url
            return "CERULEAN", "https://cdn.jsdelivr.net/npm/bootswatch@5.3.2/dist/cerulean/bootstrap.min.css"
        
        @self.app.callback(
            [Output("nav-dashboard", "active"),
             Output("nav-water-levels", "active"),
             Output("nav-recharge", "active"),
             Output("nav-quality", "active"),
             Output("nav-export", "active")],
            [Input("nav-dashboard", "n_clicks"),
             Input("nav-water-levels", "n_clicks"),
             Input("nav-recharge", "n_clicks"),
             Input("nav-quality", "n_clicks"),
             Input("nav-export", "n_clicks")]
        )
        def update_sidebar_navigation(dash_clicks, water_clicks, 
                                    recharge_clicks, quality_clicks, 
                                    export_clicks):
            """Update sidebar navigation active states."""
            ctx = dash.callback_context
            
            if not ctx.triggered:
                return True, False, False, False, False
            
            button_id = ctx.triggered[0]["prop_id"].split(".")[0]
            
            return (
                button_id == "nav-dashboard",
                button_id == "nav-water-levels",
                button_id == "nav-recharge",
                button_id == "nav-quality",
                button_id == "nav-export"
            )
    
    def get_theme_css(self, theme_name):
        """Get CSS for the selected theme."""
        theme_map = {
            "CERULEAN": dbc.themes.CERULEAN,
            "DARKLY": dbc.themes.DARKLY,
            "FLATLY": dbc.themes.FLATLY,
            "CYBORG": dbc.themes.CYBORG,
            "SLATE": dbc.themes.SLATE
        }
        return theme_map.get(theme_name, dbc.themes.CERULEAN)
    
    def run(self, debug=False, port=8050):
        """Run the dashboard application."""
        url = f"http://127.0.0.1:{port}/"
        webbrowser.open(url)
        self.app.run(debug=debug, port=port)


def main(port: int = 8050):
    """Main function to run the dashboard."""
    dashboard = DashboardApp()
    dashboard.run(port=port)


if __name__ == "__main__":
    port = 8050
    main(port)
