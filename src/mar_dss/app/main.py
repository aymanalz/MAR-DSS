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
    from mar_dss.app.water_source_tab import create_general_tab_content
    from mar_dss.app.reports_tab import create_reports_tab_content
    from mar_dss.app.hydro_tab import create_settings_tab_content
    from mar_dss.app.dashboard_tab import create_dashboard_content
    from mar_dss.app.dss_algorithm_tab import create_dss_algorithm_content
    from mar_dss.app.decision_sensitivity_tab import create_decision_sensitivity_content
    from mar_dss.app.decision_interpretation_tab import create_decision_interpretation_content
    from mar_dss.app.scenarios_comparison_tab import create_scenarios_comparison_content
    from mar_dss.app.ai_generated_decision_tab import create_ai_generated_decision_content
    from mar_dss.app.data_export_tab import create_data_export_content
except ImportError:
    # Fallback to relative imports (when run directly)
    from .water_source_tab import create_general_tab_content
    from .reports_tab import create_reports_tab_content
    from .hydro_tab import create_settings_tab_content
    from .dashboard_tab import create_dashboard_content
    from .dss_algorithm_tab import create_dss_algorithm_content
    from .decision_sensitivity_tab import create_decision_sensitivity_content
    from .decision_interpretation_tab import create_decision_interpretation_content
    from .scenarios_comparison_tab import create_scenarios_comparison_content
    from .ai_generated_decision_tab import create_ai_generated_decision_content
    from .data_export_tab import create_data_export_content


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
    
    def create_mar_purpose_section(self):
        """Create MAR Project Purpose section for overview."""
        return dbc.Card([
            dbc.CardHeader("MAR Project Purpose", className="fw-bold bg-primary text-white"),
            dbc.CardBody([
                html.Label("Project Name:", className="fw-bold"),
                dbc.Input(
                    id="project-name-input",
                    type="text",
                    placeholder="Enter your MAR project name...",
                    value="",
                    style={"margin-bottom": "15px"}
                ),
                html.Label("Analysis Date:", className="fw-bold"),
                dbc.Input(
                    id="analysis-date-input",
                    type="date",
                    value=datetime.now().strftime("%Y-%m-%d"),
                    style={"margin-bottom": "15px"}
                ),
                html.Label("Project Location:", className="fw-bold"),
                dbc.Input(
                    id="project-location-input",
                    type="text",
                    placeholder="Enter project location (e.g., Sacramento, CA)...",
                    value="",
                    style={"margin-bottom": "20px"}
                ),
                html.Label("MAR Project Purpose:", className="fw-bold"),
                html.P("Select one or more purposes for your MAR project:", className="text-muted small"),
                dbc.Checklist(
                    id="mar-purpose-checklist",
                    options=[
                        {"label": "Secure Water Supply", "value": "secure_water_supply"},
                        {"label": "Restore Depleted Aquifer Storage", "value": "restore_aquifer_storage"},
                        {"label": "Reduce Flood Impact", "value": "reduce_flood_impact"},
                        {"label": "Mitigate Seawater Intrusion", "value": "mitigate_seawater_intrusion"},
                        {"label": "Improve Water Quality", "value": "improve_water_quality"}
                    ],
                    value=["secure_water_supply"],  # Default selection
                    inline=False,
                    style={"margin-top": "10px"}
                )
            ])
        ])
    
    def create_location_map_section(self):
        """Create location map section for overview."""
        # Import the function from water_source_tab
        try:
            from mar_dss.app.water_source_tab import create_location_map
        except ImportError:
            from .water_source_tab import create_location_map
        
        return dbc.Card([
            dbc.CardHeader("Project Location - Sacramento, California, United States", id="location-card-header", className="fw-bold bg-primary text-white"),
            dbc.CardBody([
                dcc.Graph(
                    figure=create_location_map(),
                    config={'displayModeBar': True},
                    id="location-map"
                )
            ])
        ])
    
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
                        html.Div([
                            html.Img(
                                src="assets/logo2.png",
                                alt="MAR DSS Logo 2",
                                style={
                                    "height": "100px",
                                    "width": "auto",
                                    "margin-right": "12px",
                                    "vertical-align": "middle"
                                }
                            ),
                            html.H1("Managed Aquifer Recharge Decision Support System", 
                                   className="text-left mb-4",
                                   style={"font-family": "'Segoe UI', Tahoma, sans-serif", 
                                          "font-size": "2.75rem", 
                                          "font-weight": "700",
                                          "color": "#2C3E50",
                                          "background-color": "transparent",
                                          "padding": "0px",
                                          "border-radius": "8px",
                                          "border": "none",
                                          "width": "fit-content",
                                          "display": "inline-block",
                                          "vertical-align": "middle"})
                        ], style={"display": "flex", "align-items": "center", "justify-content": "flex-start"}),
                        
                        # Action Icons Row
                        html.Div([
                            dbc.ButtonGroup([
                                dbc.Button([
                                    html.I(className="fas fa-folder-open me-1"),
                                    "Open"
                                ], id="btn-open", color="outline-primary", size="sm", className="me-1", style={"padding": "4px 8px"}),
                                dbc.Button([
                                    html.I(className="fas fa-save me-1"),
                                    "Save"
                                ], id="btn-save", color="outline-success", size="sm", className="me-1", style={"padding": "4px 8px"}),
                                dbc.Button([
                                    html.I(className="fas fa-plus me-1"),
                                    "New"
                                ], id="btn-new", color="outline-info", size="sm", style={"padding": "4px 8px"})
                            ], className="mb-2")
                        ], style={"margin-top": "5px"}),
                        
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
                                    "height": "160px",
                                    "width": "auto",
                                    "max-width": "300px",
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
                        dbc.CardHeader("Analysis", className="fw-bold"),
                        dbc.CardBody([
                            dbc.Nav([
                                dbc.NavItem([
                                    dbc.NavLink("Dashboard", id="nav-dashboard", 
                                              href="#", active=True)
                                ]),
                                dbc.NavItem([
                                    dbc.NavLink("DSS Algorithm", id="nav-water-levels", 
                                              href="#")
                                ]),
                                dbc.NavItem([
                                    dbc.NavLink("Decision Sensitivity", id="nav-recharge", 
                                              href="#")
                                ]),
                                dbc.NavItem([
                                    dbc.NavLink("Decision Interpretation", id="nav-quality", 
                                              href="#")
                                ]),
                                dbc.NavItem([
                                    dbc.NavLink("Scenarios Comparison", id="nav-scenarios", 
                                              href="#")
                                ]),
                                dbc.NavItem([
                                    dbc.NavLink("AI Generated Decision", id="nav-ai-decision", 
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
                                dbc.Tab(label="Water Source", tab_id="analysis"),
                                dbc.Tab(label="Hydrogeology", tab_id="settings"),
                                dbc.Tab(label="Environmental Impact", tab_id="environmental"),
                                dbc.Tab(label="Legal Constraints", tab_id="legal"),
                                dbc.Tab(label="Reports", tab_id="reports")
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
        ], fluid=True, id="app-container"),
        
        # Global data store for stratigraphy layers
        dcc.Store(id="stratigraphy-data-store", data=[], storage_type='memory')
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
             Input("nav-scenarios", "n_clicks"),
             Input("nav-ai-decision", "n_clicks"),
             Input("nav-export", "n_clicks")]
        )
        def update_main_content(active_tab, dash_clicks, water_clicks, 
                              recharge_clicks, quality_clicks, scenarios_clicks, ai_clicks, export_clicks):
            """Update main content based on navigation."""
            ctx = dash.callback_context
            
            if not ctx.triggered:
                # Default content (overview)
                return [
                    dbc.Row([
                        dbc.Col([
                            self.create_mar_purpose_section()
                        ], width=6),
                        dbc.Col([
                            self.create_location_map_section()
                        ], width=6)
                    ], className="mb-4")
                ]
            
            # Check if sidebar navigation was triggered
            if ctx.triggered[0]["prop_id"].startswith("nav-"):
                button_id = ctx.triggered[0]["prop_id"].split(".")[0]
                
                if button_id == "nav-dashboard":
                    # Show overview content
                    return [
                        dbc.Row([
                            dbc.Col([
                                self.create_mar_purpose_section()
                            ], width=6),
                            dbc.Col([
                                self.create_location_map_section()
                            ], width=6)
                        ], className="mb-4")
                    ]
                elif button_id == "nav-dashboard":
                    return create_dashboard_content()
                elif button_id == "nav-water-levels":
                    return create_dss_algorithm_content()
                elif button_id == "nav-recharge":
                    return create_decision_sensitivity_content()
                elif button_id == "nav-quality":
                    return create_decision_interpretation_content()
                elif button_id == "nav-scenarios":
                    return create_scenarios_comparison_content()
                elif button_id == "nav-ai-decision":
                    return create_ai_generated_decision_content()
                elif button_id == "nav-export":
                    return create_data_export_content()
            
            # Handle top tab navigation - check if it's a top tab change
            if "top-tabs" in ctx.triggered[0]["prop_id"] or ctx.triggered[0]["prop_id"] == "top-tabs.active_tab":
                if active_tab == "overview":
                    return [
                        dbc.Row([
                            dbc.Col([
                                self.create_mar_purpose_section()
                            ], width=6),
                            dbc.Col([
                                self.create_location_map_section()
                            ], width=6)
                        ], className="mb-4")
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
                        dbc.Col([
                            self.create_mar_purpose_section()
                        ], width=6),
                        dbc.Col([
                            self.create_location_map_section()
                        ], width=6)
                    ], className="mb-4")
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
             Output("nav-scenarios", "active"),
             Output("nav-ai-decision", "active"),
             Output("nav-export", "active")],
            [Input("nav-dashboard", "n_clicks"),
             Input("nav-water-levels", "n_clicks"),
             Input("nav-recharge", "n_clicks"),
             Input("nav-quality", "n_clicks"),
             Input("nav-scenarios", "n_clicks"),
             Input("nav-ai-decision", "n_clicks"),
             Input("nav-export", "n_clicks")]
        )
        def update_sidebar_active_states(dash_clicks, water_clicks, 
                                       recharge_clicks, quality_clicks, 
                                       scenarios_clicks, ai_clicks, export_clicks):
            """Update sidebar navigation active states."""
            ctx = dash.callback_context
            
            if not ctx.triggered:
                return True, False, False, False, False, False, False
            
            button_id = ctx.triggered[0]["prop_id"].split(".")[0]
            
            return (
                button_id == "nav-dashboard",
                button_id == "nav-water-levels",
                button_id == "nav-recharge",
                button_id == "nav-quality",
                button_id == "nav-scenarios",
                button_id == "nav-ai-decision",
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
                
                # Import the function from water_source_tab
                try:
                    from mar_dss.app.water_source_tab import get_location_details
                except ImportError:
                    from .water_source_tab import get_location_details
                
                location_name = get_location_details(lat, lon)
                return f"Project Location - {location_name}"
            
            # Default fallback
            return "Project Location - Sacramento, California, United States"
        
        # Add callback to create the editable table
        @self.app.callback(
            Output("flow-table-container", "children"),
            [Input("flow-data-store", "data")]
        )
        def create_flow_table(flow_data):
            """Create the editable flow table."""
            try:
                from mar_dss.app.water_source_tab import create_editable_flow_table
            except ImportError:
                from .water_source_tab import create_editable_flow_table
            
            return create_editable_flow_table()
        
        # Add callback for updating monthly flow chart from table
        @self.app.callback(
            Output("monthly-flow-chart", "figure"),
            [Input("flow-data-table", "data")]
        )
        def update_monthly_flow_chart_from_table(table_data):
            """Update the monthly flow chart based on table data."""
            if not table_data:
                # Return default chart if no data
                try:
                    from mar_dss.app.water_source_tab import create_monthly_flow_chart
                except ImportError:
                    from .water_source_tab import create_monthly_flow_chart
                return create_monthly_flow_chart()
            
            # Extract flow data from table
            flow_data = {}
            for row in table_data:
                month = row['Month']
                flow = row.get('Flow (m³/month)', 0)
                flow_data[month] = flow if flow is not None else 0
            
            # Create chart with the data
            try:
                from mar_dss.app.water_source_tab import create_monthly_flow_chart
            except ImportError:
                from .water_source_tab import create_monthly_flow_chart
            
            return create_monthly_flow_chart(flow_data)
        
        # Unified callback for both adding and deleting layers
        @self.app.callback(
            [Output("stratigraphy-profile", "children"),
             Output("profile-summary", "children"),
             Output("stratigraphy-data-store", "data", allow_duplicate=True),
             Output("stratigraphy-data-store-local", "data", allow_duplicate=True)],
            [Input("add-layer-btn", "n_clicks"),
             Input({"type": "delete-layer", "index": dash.dependencies.ALL}, "n_clicks")],
            [dash.dependencies.State("layer-thickness-input", "value"),
             dash.dependencies.State("layer-type-select", "value"),
             dash.dependencies.State("layer-conductivity", "value"),
             dash.dependencies.State("layer-porosity", "value"),
             dash.dependencies.State("stratigraphy-data-store", "data"),
             dash.dependencies.State("stratigraphy-data-store-local", "data")],
            prevent_initial_call=True
        )
        def manage_stratigraphy_layers(add_clicks, delete_clicks, thickness, layer_type, 
                                      conductivity, porosity, current_data, local_data):
            """Manage adding and deleting stratigraphy layers."""
            ctx = dash.callback_context
            
            # Use whichever data store has data
            layers_data = current_data or local_data or []
            
            if not ctx.triggered:
                # Initial state - preserve existing data
                if not layers_data:
                    return [
                        html.Div([
                            html.P("No layers added yet. Use the form on the left to add layers.", 
                                   className="text-muted text-center p-3")
                        ])
                    ], [
                        html.P("Total Depth: 0 m", className="mb-1"),
                        html.P("Aquifer Layers: 0", className="mb-1"),
                        html.P("Aquitard Layers: 0", className="mb-0")
                    ], layers_data, layers_data
            
            # Check if this is an add operation
            if "add-layer-btn" in ctx.triggered[0]["prop_id"]:
                if thickness and layer_type:
                    import time
                    new_layer_data = {
                        'id': len(layers_data),
                        'timestamp': time.time(),
                        'thickness': float(thickness),
                        'layer_type': layer_type,
                        'conductivity': conductivity or 0,
                        'porosity': porosity or 0
                    }
                    layers_data.append(new_layer_data)
            
            # Check if this is a delete operation
            elif "delete-layer" in ctx.triggered[0]["prop_id"]:
                try:
                    import json
                    triggered_id = ctx.triggered[0]["prop_id"].split('.')[0]
                    component_id = json.loads(triggered_id)
                    delete_index = component_id["index"]
                    
                    if 0 <= delete_index < len(layers_data):
                        layers_data = [layer for i, layer in enumerate(layers_data) if i != delete_index]
                except (ValueError, KeyError, IndexError):
                    pass
            
            # Render the profile
            if not layers_data:
                return [
                    html.Div([
                        html.P("No layers added yet. Use the form on the left to add layers.", 
                               className="text-muted text-center p-3")
                    ])
                ], [
                    html.P("Total Depth: 0 m", className="mb-1"),
                    html.P("Aquifer Layers: 0", className="mb-1"),
                    html.P("Aquitard Layers: 0", className="mb-0")
                ], layers_data, layers_data
            
            # Create layer cards
            layer_cards = []
            layer_type_colors = {
                'aquifer': '#28a745',
                'aquitard': '#ffc107', 
                'confining': '#dc3545',
                'bedrock': '#6c757d',
                'topsoil': '#8b4513',
                'clay': '#8b4513',
                'silt': '#a0522d'
            }
            
            layer_display_names = {
                'aquifer': 'Aquifer (High Permeability)',
                'aquitard': 'Aquitard (Low Permeability)',
                'confining': 'Confining Layer',
                'bedrock': 'Bedrock',
                'topsoil': 'Topsoil',
                'clay': 'Clay Lens',
                'silt': 'Silt Layer'
            }
            
            total_depth = 0
            aquifer_count = 0
            aquitard_count = 0
            
            for i, layer_data in enumerate(layers_data):
                layer_type = layer_data.get('layer_type', 'aquifer')
                thickness = layer_data.get('thickness', 0)
                color = layer_type_colors.get(layer_type, '#6c757d')
                display_name = layer_display_names.get(layer_type, layer_type.title())
                
                # Create layer card
                layer_card = dbc.Card([
                    dbc.CardBody([
                        dbc.Row([
                            dbc.Col([
                                html.H6(display_name, className="mb-0 fw-bold", style={"font-size": "0.9rem"}),
                                html.P(f"Thickness: {thickness} m", className="mb-0 small", style={"font-size": "0.75rem"}),
                                html.P(f"Type: {layer_type.title()}", className="mb-0 small text-muted", style={"font-size": "0.7rem"})
                            ], width=8),
                            dbc.Col([
                                dbc.Button(
                                    html.I(className="fas fa-trash"),
                                    id={"type": "delete-layer", "index": i},
                                    color="outline-danger",
                                    size="sm",
                                    className="float-end",
                                    style={"padding": "2px 6px", "font-size": "0.7rem"}
                                )
                            ], width=4)
                        ])
                    ], style={"padding": "8px 12px"})
                ], className="mb-1", style={"border-left": f"4px solid {color}", "border-radius": "4px"})
                
                layer_cards.append(layer_card)
                
                # Update summary
                total_depth += thickness
                if layer_type == 'aquifer':
                    aquifer_count += 1
                elif layer_type in ['aquitard', 'confining']:
                    aquitard_count += 1
            
            # Create summary
            summary = [
                html.P(f"Total Depth: {total_depth:.1f} m", className="mb-1"),
                html.P(f"Aquifer Layers: {aquifer_count}", className="mb-1"),
                html.P(f"Aquitard Layers: {aquitard_count}", className="mb-0")
            ]
            
            return layer_cards, summary, layers_data, layers_data
        
        # Add callback to trigger stratigraphy rendering when hydrogeology tab is active
        @self.app.callback(
            [Output("stratigraphy-profile", "children", allow_duplicate=True),
             Output("profile-summary", "children", allow_duplicate=True)],
            [Input("top-tabs", "active_tab")],
            [dash.dependencies.State("stratigraphy-data-store-local", "data")],
            prevent_initial_call=True
        )
        def refresh_stratigraphy_on_tab_change(active_tab, layers_data):
            """Refresh stratigraphy display when hydrogeology tab becomes active."""
            if active_tab == "settings":  # settings tab is the hydrogeology tab
                # Trigger the main stratigraphy callback by returning the current data
                # This will cause the main callback to re-render with existing data
                if layers_data:
                    # Re-render existing layers
                    layer_cards = []
                    layer_type_colors = {
                        'aquifer': '#28a745',
                        'aquitard': '#ffc107', 
                        'confining': '#dc3545',
                        'bedrock': '#6c757d',
                        'topsoil': '#8b4513',
                        'clay': '#8b4513',
                        'silt': '#a0522d'
                    }
                    
                    layer_display_names = {
                        'aquifer': 'Aquifer (High Permeability)',
                        'aquitard': 'Aquitard (Low Permeability)',
                        'confining': 'Confining Layer',
                        'bedrock': 'Bedrock',
                        'topsoil': 'Topsoil',
                        'clay': 'Clay Lens',
                        'silt': 'Silt Layer'
                    }
                    
                    total_depth = 0
                    aquifer_count = 0
                    aquitard_count = 0
                    
                    for i, layer_data in enumerate(layers_data):
                        layer_type = layer_data.get('layer_type', 'aquifer')
                        thickness = layer_data.get('thickness', 0)
                        color = layer_type_colors.get(layer_type, '#6c757d')
                        display_name = layer_display_names.get(layer_type, layer_type.title())
                        
                        # Create layer card
                        layer_card = dbc.Card([
                            dbc.CardBody([
                                dbc.Row([
                                    dbc.Col([
                                        html.H6(display_name, className="mb-0 fw-bold", style={"font-size": "0.9rem"}),
                                        html.P(f"Thickness: {thickness} m", className="mb-0 small", style={"font-size": "0.75rem"}),
                                        html.P(f"Type: {layer_type.title()}", className="mb-0 small text-muted", style={"font-size": "0.7rem"})
                                    ], width=8),
                                    dbc.Col([
                                        dbc.Button(
                                            html.I(className="fas fa-trash"),
                                            id={"type": "delete-layer", "index": i},
                                            color="outline-danger",
                                            size="sm",
                                            className="float-end",
                                            style={"padding": "2px 6px", "font-size": "0.7rem"}
                                        )
                                    ], width=4)
                                ])
                            ], style={"padding": "8px 12px"})
                        ], className="mb-1", style={"border-left": f"4px solid {color}", "border-radius": "4px"})
                        
                        layer_cards.append(layer_card)
                        
                        # Update summary
                        total_depth += thickness
                        if layer_type == 'aquifer':
                            aquifer_count += 1
                        elif layer_type in ['aquitard', 'confining']:
                            aquitard_count += 1
                    
                    # Create summary
                    summary = [
                        html.P(f"Total Depth: {total_depth:.1f} m", className="mb-1"),
                        html.P(f"Aquifer Layers: {aquifer_count}", className="mb-1"),
                        html.P(f"Aquitard Layers: {aquitard_count}", className="mb-0")
                    ]
                    
                    return layer_cards, summary
                else:
                    return [
                        html.Div([
                            html.P("No layers added yet. Use the form on the left to add layers.", 
                                   className="text-muted text-center p-3")
                        ])
                    ], [
                        html.P("Total Depth: 0 m", className="mb-1"),
                        html.P("Aquifer Layers: 0", className="mb-1"),
                        html.P("Aquitard Layers: 0", className="mb-0")
                    ]
            return dash.no_update, dash.no_update
        
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
