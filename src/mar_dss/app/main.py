"""
Main dashboard application for MAR DSS.
"""

import dash
from dash import dcc, html, Input, Output, State, callback
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json
try:
    # Try absolute imports first (when run as module)
    from mar_dss.app.general_tab import create_general_tab_content
    from mar_dss.app.reports_tab import create_reports_tab_content
    from mar_dss.app.settings_tab import create_settings_tab_content
    from mar_dss.app.sidebar_content import (
        create_water_levels_content, 
        create_recharge_content, 
        create_quality_content, 
        create_export_content
    )
except ImportError:
    # Fallback to relative imports (when run directly)
    from .general_tab import create_general_tab_content
    from .reports_tab import create_reports_tab_content
    from .settings_tab import create_settings_tab_content
    from .sidebar_content import (
        create_water_levels_content, 
        create_recharge_content, 
        create_quality_content, 
        create_export_content
    )


class DashboardApp:
    """Main dashboard application class."""
    
    def __init__(self):
        """Initialize the dashboard application."""
        self.app = dash.Dash(
            __name__,
            external_stylesheets=[
                "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css"
            ],
            suppress_callback_exceptions=True,
            assets_folder="assets"
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
        self.data = self.create_sample_data()
        
        # Create charts
        self.water_level_chart = self.create_water_level_chart(self.data)
        self.recharge_chart = self.create_recharge_chart(self.data)
        self.quality_chart = self.create_quality_chart(self.data)
        self.summary_cards = self.create_summary_cards(self.data)
        
        # Main layout
        self.app.layout = html.Div([
            # Dynamic theme CSS link
            html.Link(
                id="theme-css",
                rel="stylesheet",
                href="https://cdn.jsdelivr.net/npm/bootswatch@5.3.2/dist/cerulean/bootstrap.min.css"
            ),
            dbc.Container([
            # Header with Logo and Theme Selector
            dbc.Row([
                dbc.Col([
                    html.Div([
                        # Title
                        html.H1("MAR DSS Dashboard", className="text-center mb-4"),
                        
                        # Theme Selector and Logo Row
                        html.Div([
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
                            ], style={"display": "inline-block", "margin-right": "20px"}),
                            
                            html.Img(
                                src="assets/logo.jpg",
                                alt="MAR DSS Logo",
                                style={
                                    "height": "80px",
                                    "width": "auto",
                                    "max-width": "150px",
                                    "vertical-align": "middle"
                                }
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
                                dbc.Tab(label="General", tab_id="analysis"),
                                dbc.Tab(label="Reports", tab_id="reports"),
                                dbc.Tab(label="Settings", tab_id="settings")
                            ], id="top-tabs", active_tab="overview")
                        ]),
                        dbc.CardBody([
                            # Main Content Area - switches based on navigation
                            html.Div(id="main-content", children=[
                                # Default content (overview)
                                dbc.Row([
                                    dbc.Col(card, width=4) for card in self.summary_cards
                                ], className="mb-4"),
                                
                                dbc.Row([
                                    dbc.Col([
                                        dcc.Graph(figure=self.water_level_chart)
                                    ], width=6),
                                    dbc.Col([
                                        dcc.Graph(figure=self.recharge_chart)
                                    ], width=6)
                                ]),
                                
                                dbc.Row([
                                    dbc.Col([
                                        dcc.Graph(figure=self.quality_chart)
                                    ], width=12)
                                ], className="mt-4")
                            ])
                        ])
                    ])
                ], width=9)
            ])
        ], fluid=True, id="app-container")
        ])
    
    def setup_callbacks(self):
        """Set up dashboard callbacks."""
        
        @self.app.callback(
            Output("main-content", "children"),
            [Input("top-tabs", "active_tab"),
             Input("nav-dashboard", "n_clicks"),
             Input("nav-water-levels", "n_clicks"),
             Input("nav-recharge", "n_clicks"),
             Input("nav-quality", "n_clicks"),
             Input("nav-export", "n_clicks")]
        )
        def update_main_content(active_tab, dash_clicks, water_clicks, 
                              recharge_clicks, quality_clicks, export_clicks):
            """Update main content based on navigation."""
            ctx = dash.callback_context
            
            if not ctx.triggered:
                # Default content (overview)
                return [
                    dbc.Row([
                        dbc.Col(card, width=4) for card in self.summary_cards
                    ], className="mb-4"),
                    
                    dbc.Row([
                        dbc.Col([
                            dcc.Graph(figure=self.water_level_chart)
                        ], width=6),
                        dbc.Col([
                            dcc.Graph(figure=self.recharge_chart)
                        ], width=6)
                    ]),
                    
                    dbc.Row([
                        dbc.Col([
                            dcc.Graph(figure=self.quality_chart)
                        ], width=12)
                    ], className="mt-4")
                ]
            
            # Check if sidebar navigation was triggered
            if ctx.triggered[0]["prop_id"].startswith("nav-"):
                button_id = ctx.triggered[0]["prop_id"].split(".")[0]
                
                if button_id == "nav-dashboard":
                    # Show overview content
                    return [
                        dbc.Row([
                            dbc.Col(card, width=4) for card in self.summary_cards
                        ], className="mb-4"),
                        
                        dbc.Row([
                            dbc.Col([
                                dcc.Graph(figure=self.water_level_chart)
                            ], width=6),
                            dbc.Col([
                                dcc.Graph(figure=self.recharge_chart)
                            ], width=6)
                        ]),
                        
                        dbc.Row([
                            dbc.Col([
                                dcc.Graph(figure=self.quality_chart)
                            ], width=12)
                        ], className="mt-4")
                    ]
                elif button_id == "nav-water-levels":
                    return create_water_levels_content()
                elif button_id == "nav-recharge":
                    return create_recharge_content()
                elif button_id == "nav-quality":
                    return create_quality_content()
                elif button_id == "nav-export":
                    return create_export_content()
            
            # Handle top tab navigation - check if it's a top tab change
            if "top-tabs" in ctx.triggered[0]["prop_id"] or ctx.triggered[0]["prop_id"] == "top-tabs.active_tab":
                if active_tab == "overview":
                    return [
                        dbc.Row([
                            dbc.Col(card, width=4) for card in self.summary_cards
                        ], className="mb-4"),
                        
                        dbc.Row([
                            dbc.Col([
                                dcc.Graph(figure=self.water_level_chart)
                            ], width=6),
                            dbc.Col([
                                dcc.Graph(figure=self.recharge_chart)
                            ], width=6)
                        ]),
                        
                        dbc.Row([
                            dbc.Col([
                                dcc.Graph(figure=self.quality_chart)
                            ], width=12)
                        ], className="mt-4")
                    ]
                elif active_tab == "analysis":
                    return create_general_tab_content()
                elif active_tab == "reports":
                    return create_reports_tab_content()
                elif active_tab == "settings":
                    return create_settings_tab_content()
            
            # Fallback: handle based on active_tab value regardless of trigger
            if active_tab == "overview":
                return [
                    dbc.Row([
                        dbc.Col(card, width=4) for card in self.summary_cards
                    ], className="mb-4"),
                    
                    dbc.Row([
                        dbc.Col([
                            dcc.Graph(figure=self.water_level_chart)
                        ], width=6),
                        dbc.Col([
                            dcc.Graph(figure=self.recharge_chart)
                        ], width=6)
                    ]),
                    
                    dbc.Row([
                        dbc.Col([
                            dcc.Graph(figure=self.quality_chart)
                        ], width=12)
                    ], className="mt-4")
                ]
            elif active_tab == "analysis":
                return create_general_tab_content()
            elif active_tab == "reports":
                return create_reports_tab_content()
            elif active_tab == "settings":
                return create_settings_tab_content()
            
            # Default fallback
            return []
        
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
        def update_sidebar_active_states(dash_clicks, water_clicks, 
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
        
        # Add callback for map interactions to update location title
        @self.app.callback(
            Output("location-card-header", "children"),
            [Input("location-map", "relayoutData")]
        )
        def update_location_title(relayout_data):
            """Update the location card title based on map interactions."""
            if relayout_data and 'mapbox.center' in relayout_data:
                center = relayout_data['mapbox.center']
                lat = center['lat']
                lon = center['lon']
                
                # Import the function from general_tab
                try:
                    from mar_dss.app.general_tab import get_location_details
                except ImportError:
                    from .general_tab import get_location_details
                
                location_name = get_location_details(lat, lon)
                return f"Project Location - {location_name}"
            
            # Default fallback
            return "Project Location - Sacramento, California, United States"
        
    def get_theme_css(self, theme_name):
        """Get CSS for the selected theme."""
        theme_map = {
            "CERULEAN": dbc.themes.CERULEAN,
            "DARKLY": dbc.themes.DARKLY,
            "FLATLY": dbc.themes.FLATLY,
            "CYBORG": dbc.themes.CYBORG,
            "SLATE": dbc.themes.SLATE     }  
        return theme_map.get(theme_name, dbc.themes.CERULEAN)
    
    def run(self, debug=True, port=8050, open_browser=True):
        """Run the dashboard application."""
        url = f"http://127.0.0.1:{port}/"
        print(f"Dashboard running at: {url}")
        print("Open the URL in your browser to view the dashboard.")
        
        if open_browser:
            import webbrowser
            print(f"Opening browser to: {url}")
            webbrowser.open(url)
            
        self.app.run(debug=debug, port=port)


def main(port: int = 8050, open_browser: bool = True):
    """Main function to run the dashboard."""
    dashboard = DashboardApp()
    dashboard.run(port=port, open_browser=open_browser)


if __name__ == "__main__":
    port = 8050
    main(port)
