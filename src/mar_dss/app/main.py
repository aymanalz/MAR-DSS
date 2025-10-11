"""
Main dashboard application for MAR DSS.
"""

from datetime import datetime

import dash
import dash_bootstrap_components as dbc
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from dash import Input, Output, dcc, html

try:
    # Try absolute imports first (when run as module)
    from mar_dss.app.components.ai_generated_decision_tab import (
        create_ai_generated_decision_content,
    )
    from mar_dss.app.components.dashboard_tab import create_dashboard_content
    from mar_dss.app.components.data_export_tab import (
        create_data_export_content,
    )
    from mar_dss.app.components.decision_interpretation_tab import (
        create_decision_interpretation_content,
    )
    from mar_dss.app.components.decision_sensitivity_tab import (
        create_decision_sensitivity_content,
    )
    from mar_dss.app.components.dss_algorithm_tab import (
        create_dss_algorithm_content,
    )
    from mar_dss.app.components.hydro_tab import create_hydro_tab_content, _build_stratigraphy_row
    from mar_dss.app.components.reports_tab import create_reports_tab_content
    from mar_dss.app.components.scenarios_comparison_tab import (
        create_scenarios_comparison_content,
    )
    from mar_dss.app.components.water_source_tab import (
        create_general_tab_content,
    )
except ImportError:
    # Fallback to relative imports (when run directly)
    from .components.ai_generated_decision_tab import (
        create_ai_generated_decision_content,
    )
    from .components.dashboard_tab import create_dashboard_content
    from .components.data_export_tab import create_data_export_content
    from .components.decision_interpretation_tab import (
        create_decision_interpretation_content,
    )
    from .components.decision_sensitivity_tab import (
        create_decision_sensitivity_content,
    )
    from .components.dss_algorithm_tab import create_dss_algorithm_content
    from .components.hydro_tab import create_hydro_tab_content
    from .components.reports_tab import create_reports_tab_content
    from .components.scenarios_comparison_tab import (
        create_scenarios_comparison_content,
    )
    from .components.water_source_tab import create_general_tab_content


class DashboardApp:
    """Main dashboard application class."""

    def __init__(self):
        """Initialize the dashboard application."""
        # 
        self.app = dash.Dash(
            __name__,
            external_stylesheets=[
                "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css"
            ],
            suppress_callback_exceptions=True,
            assets_folder="assets",
        )
        self.current_theme = "CERULEAN"
        self.setup_layout()
        self.setup_callbacks()

    def create_sample_data(self):
        """Create sample data for demonstration."""
        # Generate sample time series data
        dates = pd.date_range(start="2023-01-01", end="2023-12-31", freq="D")

        # Water level data
        water_levels = np.random.normal(100, 10, len(dates)) + 5 * np.sin(
            np.arange(len(dates)) * 2 * np.pi / 365
        )

        # Recharge data
        recharge_data = np.random.exponential(2, len(dates)) * (
            1 + 0.5 * np.sin(np.arange(len(dates)) * 2 * np.pi / 365)
        )

        # Quality data
        quality_data = np.random.normal(7.5, 0.5, len(dates))

        return {
            "dates": dates,
            "water_levels": water_levels,
            "recharge_data": recharge_data,
            "quality_data": quality_data,
        }

    def create_water_level_chart(self, data):
        """Create water level time series chart."""
        fig = go.Figure()
        fig.add_trace(
            go.Scatter(
                x=data["dates"],
                y=data["water_levels"],
                mode="lines+markers",
                name="Water Level",
                line=dict(color="#1f77b4", width=2),
                marker=dict(size=4),
            )
        )

        fig.update_layout(
            title="Water Level Over Time",
            xaxis_title="Date",
            yaxis_title="Water Level (m)",
            hovermode="x unified",
            template="plotly_white",
        )

        return fig

    def create_recharge_chart(self, data):
        """Create recharge rate chart."""
        fig = go.Figure()
        fig.add_trace(
            go.Bar(
                x=data["dates"],
                y=data["recharge_data"],
                name="Recharge Rate",
                marker_color="#2ca02c",
            )
        )

        fig.update_layout(
            title="Recharge Rate Over Time",
            xaxis_title="Date",
            yaxis_title="Recharge Rate (mm/day)",
            template="plotly_white",
        )

        return fig

    def create_quality_chart(self, data):
        """Create water quality chart."""
        fig = go.Figure()
        fig.add_trace(
            go.Scatter(
                x=data["dates"],
                y=data["quality_data"],
                mode="lines+markers",
                name="pH Level",
                line=dict(color="#ff7f0e", width=2),
                marker=dict(size=4),
            )
        )

        fig.update_layout(
            title="Water Quality (pH) Over Time",
            xaxis_title="Date",
            yaxis_title="pH Level",
            hovermode="x unified",
            template="plotly_white",
        )

        return fig

    def create_summary_cards(self, data):
        """Create summary cards for the dashboard."""
        current_level = data["water_levels"][-1]
        avg_recharge = np.mean(data["recharge_data"])
        current_quality = data["quality_data"][-1]

        cards = [
            dbc.Card(
                [
                    dbc.CardBody(
                        [
                            html.H4(
                                f"{current_level:.1f} m", className="card-title"
                            ),
                            html.P(
                                "Current Water Level", className="card-text"
                            ),
                            html.I(className="fas fa-tint fa-2x text-primary"),
                        ]
                    )
                ],
                className="text-center mb-3",
            ),
            dbc.Card(
                [
                    dbc.CardBody(
                        [
                            html.H4(
                                f"{avg_recharge:.2f} mm/day",
                                className="card-title",
                            ),
                            html.P(
                                "Average Recharge Rate", className="card-text"
                            ),
                            html.I(
                                className="fas fa-cloud-rain fa-2x text-success"
                            ),
                        ]
                    )
                ],
                className="text-center mb-3",
            ),
            dbc.Card(
                [
                    dbc.CardBody(
                        [
                            html.H4(
                                f"{current_quality:.2f}", className="card-title"
                            ),
                            html.P("Current pH Level", className="card-text"),
                            html.I(className="fas fa-flask fa-2x text-warning"),
                        ]
                    )
                ],
                className="text-center mb-3",
            ),
        ]

        return cards

    def create_mar_purpose_section(self):
        """Create MAR Project Purpose section for overview."""
        return dbc.Card(
            [
                dbc.CardHeader(
                    "MAR Project Purpose",
                    className="fw-bold bg-primary text-white",
                ),
                dbc.CardBody(
                    [
                        html.Label("Project Name:", className="fw-bold"),
                        dbc.Input(
                            id="project-name-input",
                            type="text",
                            placeholder="Enter your MAR project name...",
                            value="",
                            style={"margin-bottom": "15px"},
                        ),
                        html.Label("Analysis Date:", className="fw-bold"),
                        dbc.Input(
                            id="analysis-date-input",
                            type="date",
                            value=datetime.now().strftime("%Y-%m-%d"),
                            style={"margin-bottom": "15px"},
                        ),
                        html.Label("Project Location:", className="fw-bold"),
                        dbc.Input(
                            id="project-location-input",
                            type="text",
                            placeholder="Enter project location (e.g., Sacramento, CA)...",
                            value="",
                            style={"margin-bottom": "20px"},
                        ),
                        html.Label("MAR Project Purpose:", className="fw-bold"),
                        html.P(
                            "Select one or more purposes for your MAR project:",
                            className="text-muted small",
                        ),
                        dbc.Checklist(
                            id="mar-purpose-checklist",
                            options=[
                                {
                                    "label": "Secure Water Supply",
                                    "value": "secure_water_supply",
                                },
                                {
                                    "label": "Restore Depleted Aquifer Storage",
                                    "value": "restore_aquifer_storage",
                                },
                                {
                                    "label": "Reduce Flood Impact",
                                    "value": "reduce_flood_impact",
                                },
                                {
                                    "label": "Mitigate Seawater Intrusion",
                                    "value": "mitigate_seawater_intrusion",
                                },
                                {
                                    "label": "Improve Water Quality",
                                    "value": "improve_water_quality",
                                },
                            ],
                            value=["secure_water_supply"],  # Default selection
                            inline=False,
                            style={"margin-top": "10px"},
                        ),
                    ]
                ),
            ]
        )

    def create_location_map_section(self):
        """Create location map section for overview."""
        # Import the function from components.water_source_tab
        try:
            from mar_dss.app.components.water_source_tab import (
                create_location_map,
            )
        except ImportError:
            from .components.water_source_tab import create_location_map

        return dbc.Card(
            [
                dbc.CardHeader(
                    "Project Location - Sacramento, California, United States",
                    id="location-card-header",
                    className="fw-bold bg-primary text-white",
                ),
                dbc.CardBody(
                    [
                        dcc.Graph(
                            figure=create_location_map(),
                            config={"displayModeBar": True},
                            id="location-map",
                        )
                    ]
                ),
            ]
        )

    def setup_layout(self):
        """Set up the main dashboard layout by delegating to layout module."""
        # Import locally to avoid potential circular imports
        try:
            from mar_dss.app.components.layout import (
                setup_layout as _setup_layout,
            )
        except ImportError:
            from .components.layout import setup_layout as _setup_layout

        _setup_layout(self)

    def setup_callbacks(self):
        """Set up dashboard callbacks."""

        @self.app.callback(
            Output("main-content", "children"),
            [
                Input("top-tabs", "active_tab"),
                Input("nav-dashboard", "n_clicks"),
                Input("nav-water-levels", "n_clicks"),
                Input("nav-recharge", "n_clicks"),
                Input("nav-quality", "n_clicks"),
                Input("nav-scenarios", "n_clicks"),
                Input("nav-ai-decision", "n_clicks"),
                Input("nav-export", "n_clicks"),
            ],
        )
        def update_main_content(
            active_tab,
            dash_clicks,
            water_clicks,
            recharge_clicks,
            quality_clicks,
            scenarios_clicks,
            ai_clicks,
            export_clicks,
        ):
            """Update main content based on navigation."""
            ctx = dash.callback_context

            if not ctx.triggered:
                # Default content (overview)
                return [
                    dbc.Row(
                        [
                            dbc.Col(
                                [self.create_mar_purpose_section()], width=6
                            ),
                            dbc.Col(
                                [self.create_location_map_section()], width=6
                            ),
                        ],
                        className="mb-4",
                    )
                ]

            # Check if sidebar navigation was triggered
            if ctx.triggered[0]["prop_id"].startswith("nav-"):
                button_id = ctx.triggered[0]["prop_id"].split(".")[0]

                if button_id == "nav-dashboard":
                    # Show overview content
                    return [
                        dbc.Row(
                            [
                                dbc.Col(
                                    [self.create_mar_purpose_section()], width=6
                                ),
                                dbc.Col(
                                    [self.create_location_map_section()],
                                    width=6,
                                ),
                            ],
                            className="mb-4",
                        )
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
            if (
                "top-tabs" in ctx.triggered[0]["prop_id"]
                or ctx.triggered[0]["prop_id"] == "top-tabs.active_tab"
            ):
                if active_tab == "overview":
                    return [
                        dbc.Row(
                            [
                                dbc.Col(
                                    [self.create_mar_purpose_section()], width=6
                                ),
                                dbc.Col(
                                    [self.create_location_map_section()],
                                    width=6,
                                ),
                            ],
                            className="mb-4",
                        )
                    ]
                elif active_tab == "analysis":
                    return create_general_tab_content()
                elif active_tab == "reports":
                    return create_reports_tab_content()
                elif active_tab == "settings":
                    return create_hydro_tab_content()

            # Fallback: handle based on active_tab value regardless of trigger
            if active_tab == "overview":
                return [
                    dbc.Row(
                        [
                            dbc.Col(
                                [self.create_mar_purpose_section()], width=6
                            ),
                            dbc.Col(
                                [self.create_location_map_section()], width=6
                            ),
                        ],
                        className="mb-4",
                    )
                ]
            elif active_tab == "analysis":
                return create_general_tab_content()
            elif active_tab == "reports":
                return create_reports_tab_content()
            elif active_tab == "settings":
                return create_hydro_tab_content()

            # Default fallback
            return []

        @self.app.callback(
            [Output("theme-selector", "value"), Output("theme-css", "href")],
            [Input("theme-selector", "value")],
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
                    "SLATE": "https://cdn.jsdelivr.net/npm/bootswatch@5.3.2/dist/slate/bootstrap.min.css",
                }

                theme_url = theme_urls.get(
                    selected_theme, theme_urls["CERULEAN"]
                )
                return selected_theme, theme_url
            return (
                "CERULEAN",
                "https://cdn.jsdelivr.net/npm/bootswatch@5.3.2/dist/cerulean/bootstrap.min.css",
            )

        @self.app.callback(
            [
                Output("nav-dashboard", "active"),
                Output("nav-water-levels", "active"),
                Output("nav-recharge", "active"),
                Output("nav-quality", "active"),
                Output("nav-scenarios", "active"),
                Output("nav-ai-decision", "active"),
                Output("nav-export", "active"),
            ],
            [
                Input("nav-dashboard", "n_clicks"),
                Input("nav-water-levels", "n_clicks"),
                Input("nav-recharge", "n_clicks"),
                Input("nav-quality", "n_clicks"),
                Input("nav-scenarios", "n_clicks"),
                Input("nav-ai-decision", "n_clicks"),
                Input("nav-export", "n_clicks"),
            ],
        )
        def update_sidebar_active_states(
            dash_clicks,
            water_clicks,
            recharge_clicks,
            quality_clicks,
            scenarios_clicks,
            ai_clicks,
            export_clicks,
        ):
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
                button_id == "nav-export",
            )

        # Add callback for map interactions to update location title
        @self.app.callback(
            Output("location-card-header", "children"),
            [Input("location-map", "relayoutData")],
        )
        def update_location_title(relayout_data):
            """Update the location card title based on map interactions."""
            if relayout_data and "mapbox.center" in relayout_data:
                center = relayout_data["mapbox.center"]
                lat = center["lat"]
                lon = center["lon"]

                # Import the function from components.water_source_tab
                try:
                    from mar_dss.app.components.water_source_tab import (
                        get_location_details,
                    )
                except ImportError:
                    from .components.water_source_tab import get_location_details

                location_name = get_location_details(lat, lon)
                return f"Project Location - {location_name}"

            # Default fallback
            return "Project Location - Sacramento, California, United States"

        # Add callback to create the editable table
        @self.app.callback(
            Output("flow-table-container", "children"),
            [Input("flow-data-store", "data")],
        )
        def create_flow_table(flow_data):
            """Create the editable flow table."""
            try:
                from mar_dss.app.components.water_source_tab import (
                    create_editable_flow_table,
                )
            except ImportError:
                from .components.water_source_tab import (
                    create_editable_flow_table,
                )

            return create_editable_flow_table()

        # Add callback for updating monthly flow chart from table
        @self.app.callback(
            Output("monthly-flow-chart", "figure"),
            [Input("flow-data-table", "data")],
        )
        def update_monthly_flow_chart_from_table(table_data):
            """Update the monthly flow chart based on table data."""
            if not table_data:
                # Return default chart if no data
                try:
                    from mar_dss.app.components.water_source_tab import (
                        create_monthly_flow_chart,
                    )
                except ImportError:
                    from .components.water_source_tab import (
                        create_monthly_flow_chart,
                    )
                return create_monthly_flow_chart()

            # Extract flow data from table
            flow_data = {}
            for row in table_data:
                month = row["Month"]
                flow = row.get("Flow (m³/month)", 0)
                flow_data[month] = flow if flow is not None else 0

            # Create chart with the data
            try:
                from mar_dss.app.components.water_source_tab import (
                    create_monthly_flow_chart,
                )
            except ImportError:
                from .components.water_source_tab import (
                    create_monthly_flow_chart,
                )

            return create_monthly_flow_chart(flow_data)

        # Unified callback for both adding and deleting layers
        @self.app.callback(
            [
                Output("stratigraphy-profile", "children"),
                Output("profile-summary", "children"),
                Output("stratigraphy-data-store", "data", allow_duplicate=True),
                Output(
                    "stratigraphy-data-store-local",
                    "data",
                    allow_duplicate=True,
                ),
            ],
            [
                Input("add-layer-btn", "n_clicks"),
                Input(
                    {"type": "delete-layer", "index": dash.dependencies.ALL},
                    "n_clicks",
                ),
            ],
            [
                dash.dependencies.State("layer-thickness-input", "value"),
                dash.dependencies.State("layer-type-select", "value"),
                dash.dependencies.State("layer-conductivity", "value"),
                dash.dependencies.State("layer-porosity", "value"),
                dash.dependencies.State("stratigraphy-data-store", "data"),
                dash.dependencies.State(
                    "stratigraphy-data-store-local", "data"
                ),
            ],
            prevent_initial_call=True,
        )
        def manage_stratigraphy_layers(
            add_clicks,
            delete_clicks,
            thickness,
            layer_type,
            conductivity,
            porosity,
            current_data,
            local_data,
        ):
            """Manage adding and deleting stratigraphy layers."""
            ctx = dash.callback_context

            # Use whichever data store has data
            layers_data = current_data or local_data or []

            if not ctx.triggered:
                # Initial state - preserve existing data
                if not layers_data:
                    return (
                        [
                            html.Div(
                                [
                                    html.P(
                                        "No layers added yet. Use the form on the left to add layers.",
                                        className="text-muted text-center p-3",
                                    )
                                ]
                            )
                        ],
                        [
                            html.P("Total Depth: 0 m", className="mb-1"),
                            html.P("Aquifer Layers: 0", className="mb-1"),
                            html.P("Aquitard Layers: 0", className="mb-0"),
                        ],
                        layers_data,
                        layers_data,
                    )

            # Check if this is an add operation
            if "add-layer-btn" in ctx.triggered[0]["prop_id"]:
                if thickness and layer_type:
                    import time

                    new_layer_data = {
                        "id": len(layers_data),
                        "timestamp": time.time(),
                        "thickness": float(thickness),
                        "layer_type": layer_type,
                        "conductivity": conductivity or 0,
                        "porosity": porosity or 0,
                    }
                    layers_data.append(new_layer_data)

            # Check if this is a delete operation
            elif "delete-layer" in ctx.triggered[0]["prop_id"]:
                try:
                    import json

                    triggered_id = ctx.triggered[0]["prop_id"].split(".")[0]
                    component_id = json.loads(triggered_id)
                    delete_index = component_id["index"]

                    if 0 <= delete_index < len(layers_data):
                        layers_data = [
                            layer
                            for i, layer in enumerate(layers_data)
                            if i != delete_index
                        ]
                except (ValueError, KeyError, IndexError):
                    pass

            # Render the profile
            if not layers_data:
                return (
                    [
                        html.Div(
                            [
                                html.P(
                                    "No layers added yet. Use the form on the left to add layers.",
                                    className="text-muted text-center p-3",
                                )
                            ]
                        )
                    ],
                    [
                        html.P("Total Depth: 0 m", className="mb-1"),
                        html.P("Aquifer Layers: 0", className="mb-1"),
                        html.P("Aquitard Layers: 0", className="mb-0"),
                    ],
                    layers_data,
                    layers_data,
                )

            # Create layer cards
            layer_cards = []
            layer_type_colors = {
                "aquifer": "#28a745",
                "aquitard": "#ffc107",
                "confining": "#dc3545",
                "bedrock": "#6c757d",
                "topsoil": "#8b4513",
                "clay": "#8b4513",
                "silt": "#a0522d",
            }

            layer_display_names = {
                "aquifer": "Aquifer (High Permeability)",
                "aquitard": "Aquitard (Low Permeability)",
                "confining": "Confining Layer",
                "bedrock": "Bedrock",
                "topsoil": "Topsoil",
                "clay": "Clay Lens",
                "silt": "Silt Layer",
            }

            total_depth = 0
            aquifer_count = 0
            aquitard_count = 0

            for i, layer_data in enumerate(layers_data):
                layer_type = layer_data.get("layer_type", "aquifer")
                thickness = layer_data.get("thickness", 0)
                color = layer_type_colors.get(layer_type, "#6c757d")
                display_name = layer_display_names.get(
                    layer_type, layer_type.title()
                )

                # Create layer card
                layer_card = dbc.Card(
                    [
                        dbc.CardBody(
                            [
                                dbc.Row(
                                    [
                                        dbc.Col(
                                            [
                                                html.H6(
                                                    display_name,
                                                    className="mb-0 fw-bold",
                                                    style={
                                                        "font-size": "0.9rem"
                                                    },
                                                ),
                                                html.P(
                                                    f"Thickness: {thickness} m",
                                                    className="mb-0 small",
                                                    style={
                                                        "font-size": "0.75rem"
                                                    },
                                                ),
                                                html.P(
                                                    f"Type: {layer_type.title()}",
                                                    className="mb-0 small text-muted",
                                                    style={
                                                        "font-size": "0.7rem"
                                                    },
                                                ),
                                            ],
                                            width=8,
                                        ),
                                        dbc.Col(
                                            [
                                                dbc.Button(
                                                    html.I(
                                                        className="fas fa-trash"
                                                    ),
                                                    id={
                                                        "type": "delete-layer",
                                                        "index": i,
                                                    },
                                                    color="outline-danger",
                                                    size="sm",
                                                    className="float-end",
                                                    style={
                                                        "padding": "2px 6px",
                                                        "font-size": "0.7rem",
                                                    },
                                                )
                                            ],
                                            width=4,
                                        ),
                                    ]
                                )
                            ],
                            style={"padding": "8px 12px"},
                        )
                    ],
                    className="mb-1",
                    style={
                        "border-left": f"4px solid {color}",
                        "border-radius": "4px",
                    },
                )

                layer_cards.append(layer_card)

                # Update summary
                total_depth += thickness
                if layer_type == "aquifer":
                    aquifer_count += 1
                elif layer_type in ["aquitard", "confining"]:
                    aquitard_count += 1

            # Create summary
            summary = [
                html.P(f"Total Depth: {total_depth:.1f} m", className="mb-1"),
                html.P(f"Aquifer Layers: {aquifer_count}", className="mb-1"),
                html.P(f"Aquitard Layers: {aquitard_count}", className="mb-0"),
            ]

            return layer_cards, summary, layers_data, layers_data

        # Add callback to trigger stratigraphy rendering when hydrogeology tab is active
        @self.app.callback(
            [
                Output(
                    "stratigraphy-profile", "children", allow_duplicate=True
                ),
                Output("profile-summary", "children", allow_duplicate=True),
            ],
            [Input("top-tabs", "active_tab")],
            [dash.dependencies.State("stratigraphy-data-store-local", "data")],
            prevent_initial_call=True,
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
                        "aquifer": "#28a745",
                        "aquitard": "#ffc107",
                        "confining": "#dc3545",
                        "bedrock": "#6c757d",
                        "topsoil": "#8b4513",
                        "clay": "#8b4513",
                        "silt": "#a0522d",
                    }

                    layer_display_names = {
                        "aquifer": "Aquifer (High Permeability)",
                        "aquitard": "Aquitard (Low Permeability)",
                        "confining": "Confining Layer",
                        "bedrock": "Bedrock",
                        "topsoil": "Topsoil",
                        "clay": "Clay Lens",
                        "silt": "Silt Layer",
                    }

                    total_depth = 0
                    aquifer_count = 0
                    aquitard_count = 0

                    for i, layer_data in enumerate(layers_data):
                        layer_type = layer_data.get("layer_type", "aquifer")
                        thickness = layer_data.get("thickness", 0)
                        color = layer_type_colors.get(layer_type, "#6c757d")
                        display_name = layer_display_names.get(
                            layer_type, layer_type.title()
                        )

                        # Create layer card
                        layer_card = dbc.Card(
                            [
                                dbc.CardBody(
                                    [
                                        dbc.Row(
                                            [
                                                dbc.Col(
                                                    [
                                                        html.H6(
                                                            display_name,
                                                            className="mb-0 fw-bold",
                                                            style={
                                                                "font-size": "0.9rem"
                                                            },
                                                        ),
                                                        html.P(
                                                            f"Thickness: {thickness} m",
                                                            className="mb-0 small",
                                                            style={
                                                                "font-size": "0.75rem"
                                                            },
                                                        ),
                                                        html.P(
                                                            f"Type: {layer_type.title()}",
                                                            className="mb-0 small text-muted",
                                                            style={
                                                                "font-size": "0.7rem"
                                                            },
                                                        ),
                                                    ],
                                                    width=8,
                                                ),
                                                dbc.Col(
                                                    [
                                                        dbc.Button(
                                                            html.I(
                                                                className="fas fa-trash"
                                                            ),
                                                            id={
                                                                "type": "delete-layer",
                                                                "index": i,
                                                            },
                                                            color="outline-danger",
                                                            size="sm",
                                                            className="float-end",
                                                            style={
                                                                "padding": "2px 6px",
                                                                "font-size": "0.7rem",
                                                            },
                                                        )
                                                    ],
                                                    width=4,
                                                ),
                                            ]
                                        )
                                    ],
                                    style={"padding": "8px 12px"},
                                )
                            ],
                            className="mb-1",
                            style={
                                "border-left": f"4px solid {color}",
                                "border-radius": "4px",
                            },
                        )

                        layer_cards.append(layer_card)

                        # Update summary
                        total_depth += thickness
                        if layer_type == "aquifer":
                            aquifer_count += 1
                        elif layer_type in ["aquitard", "confining"]:
                            aquitard_count += 1

                    # Create summary
                    summary = [
                        html.P(
                            f"Total Depth: {total_depth:.1f} m",
                            className="mb-1",
                        ),
                        html.P(
                            f"Aquifer Layers: {aquifer_count}", className="mb-1"
                        ),
                        html.P(
                            f"Aquitard Layers: {aquitard_count}",
                            className="mb-0",
                        ),
                    ]

                    return layer_cards, summary
                else:
                    return [
                        html.Div(
                            [
                                html.P(
                                    "No layers added yet. Use the form on the left to add layers.",
                                    className="text-muted text-center p-3",
                                )
                            ]
                        )
                    ], [
                        html.P("Total Depth: 0 m", className="mb-1"),
                        html.P("Aquifer Layers: 0", className="mb-1"),
                        html.P("Aquitard Layers: 0", className="mb-0"),
                    ]
            return dash.no_update, dash.no_update

        # Callback for stratigraphy table management
        @self.app.callback(
            [
                Output("stratigraphy-table-body", "children"),
                Output("stratigraphy-table-data", "data"),
                Output("remove-stratigraphy-row-btn", "disabled"),
            ],
            [
                Input("add-stratigraphy-row-btn", "n_clicks"),
                Input("remove-stratigraphy-row-btn", "n_clicks"),
                Input({"type": "remove-stratigraphy-row", "index": dash.dependencies.ALL}, "n_clicks"),
                Input({"type": "move-stratigraphy-up", "index": dash.dependencies.ALL}, "n_clicks"),
                Input({"type": "move-stratigraphy-down", "index": dash.dependencies.ALL}, "n_clicks"),
            ],
            [
                dash.dependencies.State("stratigraphy-table-data", "data"),
            ],
            prevent_initial_call=True,
        )
        def manage_stratigraphy_table(
            add_clicks,
            remove_clicks,
            individual_remove_clicks,
            move_up_clicks,
            move_down_clicks,
            table_data,
        ):
            """Manage adding and removing rows from the stratigraphy table."""
            import pandas as pd
            
            ctx = dash.callback_context

            # Initialize DataFrame if needed
            if not table_data or not isinstance(table_data, dict):
                df = pd.DataFrame({
                    "parameter": ["Top Soil Thickness", "Water Table Depth", "Bedrock Depth"],
                    "depth": ["1", "20", "50"]
                })
            else:
                df = pd.DataFrame(table_data)
                # Ensure mandatory rows exist
                mandatory_params = ["Top Soil Thickness", "Water Table Depth", "Bedrock Depth"]
                existing_params = df["parameter"].tolist()
                
                # Add missing mandatory parameters
                for param in mandatory_params:
                    if param not in existing_params:
                        new_row = pd.DataFrame({
                            "parameter": [param],
                            "depth": [""]
                        })
                        df = pd.concat([df, new_row], ignore_index=True)

            if not ctx.triggered:
                # Initial state
                rows = []
                for i in range(len(df)):
                    row_data = {
                        "parameter": df.iloc[i]["parameter"],
                        "depth": df.iloc[i]["depth"]
                    }
                    rows.append(_build_stratigraphy_row(i, len(df), row_data))
                return rows, df.to_dict('list'), len(df) <= 1

            # Check if this is an add operation
            if "add-stratigraphy-row-btn" in ctx.triggered[0]["prop_id"]:
                # Find the position to insert (above Bedrock Depth, below Top Soil Thickness)
                bedrock_idx = None
                for i, param in enumerate(df["parameter"]):
                    if param == "Bedrock Depth":
                        bedrock_idx = i
                        break
                
                # Insert new row above Bedrock Depth (or at end if Bedrock Depth not found)
                insert_position = bedrock_idx if bedrock_idx is not None else len(df)
                
                new_row = pd.DataFrame({
                    "parameter": ["Sand Layer Thickness"],
                    "depth": ["50"]
                })
                
                # Insert at the calculated position
                if insert_position == 0:
                    # Insert at beginning (after Top Soil Thickness)
                    df = pd.concat([df.iloc[:1], new_row, df.iloc[1:]], ignore_index=True)
                else:
                    # Insert at the calculated position
                    df = pd.concat([df.iloc[:insert_position], new_row, df.iloc[insert_position:]], ignore_index=True)
                
                # Build all rows
                rows = []
                for i in range(len(df)):
                    row_data = {
                        "parameter": df.iloc[i]["parameter"],
                        "depth": df.iloc[i]["depth"]
                    }
                    rows.append(_build_stratigraphy_row(i, len(df), row_data))
                
                return rows, df.to_dict('list'), len(df) <= 1

            # Check if this is a remove last row operation
            elif "remove-stratigraphy-row-btn" in ctx.triggered[0]["prop_id"]:
                if len(df) > 1:
                    df = df.iloc[:-1]
                
                # Build all rows
                rows = []
                for i in range(len(df)):
                    row_data = {
                        "parameter": df.iloc[i]["parameter"],
                        "depth": df.iloc[i]["depth"]
                    }
                    rows.append(_build_stratigraphy_row(i, len(df), row_data))
                
                return rows, df.to_dict('list'), len(df) <= 1

            # Check if this is an individual row removal
            elif "remove-stratigraphy-row" in ctx.triggered[0]["prop_id"]:
                try:
                    import json
                    triggered_id = ctx.triggered[0]["prop_id"].split(".")[0]
                    component_id = json.loads(triggered_id)
                    remove_index = component_id["index"]
                    
                    if 0 <= remove_index < len(df):
                        # Check if trying to remove a mandatory row
                        param_to_remove = df.iloc[remove_index]["parameter"]
                        mandatory_params = ["Top Soil Thickness", "Water Table Depth", "Bedrock Depth"]
                        
                        if param_to_remove not in mandatory_params:
                            df = df.drop(df.index[remove_index]).reset_index(drop=True)
                        
                        # Rebuild rows with new indices
                        rows = []
                        for i in range(len(df)):
                            row_data = {
                                "parameter": df.iloc[i]["parameter"],
                                "depth": df.iloc[i]["depth"]
                            }
                            rows.append(_build_stratigraphy_row(i, len(df), row_data))
                        
                        return rows, df.to_dict('list'), len(df) <= 1
                except (ValueError, KeyError, IndexError):
                    pass

            # Check if this is a move up operation
            elif "move-stratigraphy-up" in ctx.triggered[0]["prop_id"]:
                try:
                    import json
                    triggered_id = ctx.triggered[0]["prop_id"].split(".")[0]
                    component_id = json.loads(triggered_id)
                    move_index = component_id["index"]
                    
                    if move_index > 0 and move_index < len(df):
                        param_to_move = df.iloc[move_index]["parameter"]
                        param_above = df.iloc[move_index - 1]["parameter"]
                        
                        # Prevent moving "Bedrock Depth" up
                        # Prevent moving anything above "Top Soil Thickness"
                        if (param_to_move != "Bedrock Depth" and 
                            param_above != "Top Soil Thickness"):
                            # Swap rows in DataFrame
                            df.iloc[move_index], df.iloc[move_index - 1] = \
                                df.iloc[move_index - 1].copy(), df.iloc[move_index].copy()
                        
                        # Rebuild rows with new order
                        rows = []
                        for i in range(len(df)):
                            row_data = {
                                "parameter": df.iloc[i]["parameter"],
                                "depth": df.iloc[i]["depth"]
                            }
                            rows.append(_build_stratigraphy_row(i, len(df), row_data))
                        
                        return rows, df.to_dict('list'), len(df) <= 1
                except (ValueError, KeyError, IndexError):
                    pass

            # Check if this is a move down operation
            elif "move-stratigraphy-down" in ctx.triggered[0]["prop_id"]:
                try:
                    import json
                    triggered_id = ctx.triggered[0]["prop_id"].split(".")[0]
                    component_id = json.loads(triggered_id)
                    move_index = component_id["index"]
                    
                    if move_index >= 0 and move_index < len(df) - 1:
                        param_to_move = df.iloc[move_index]["parameter"]
                        param_below = df.iloc[move_index + 1]["parameter"]
                        
                        # Prevent moving "Top Soil Thickness" down
                        # Prevent moving anything below "Bedrock Depth"
                        if (param_to_move != "Top Soil Thickness" and 
                            param_below != "Bedrock Depth"):
                            # Swap rows in DataFrame
                            df.iloc[move_index], df.iloc[move_index + 1] = \
                                df.iloc[move_index + 1].copy(), df.iloc[move_index].copy()
                        
                        # Rebuild rows with new order
                        rows = []
                        for i in range(len(df)):
                            row_data = {
                                "parameter": df.iloc[i]["parameter"],
                                "depth": df.iloc[i]["depth"]
                            }
                            rows.append(_build_stratigraphy_row(i, len(df), row_data))
                        
                        return rows, df.to_dict('list'), len(df) <= 1
                except (ValueError, KeyError, IndexError):
                    pass

            # Ensure correct order: Top Soil Thickness first, Bedrock Depth last
            def enforce_order(df):
                """Ensure Top Soil Thickness is first and Bedrock Depth is last."""
                if len(df) == 0:
                    return df
                
                # Find indices of mandatory parameters
                top_soil_idx = None
                bedrock_idx = None
                
                for i, param in enumerate(df["parameter"]):
                    if param == "Top Soil Thickness":
                        top_soil_idx = i
                    elif param == "Bedrock Depth":
                        bedrock_idx = i
                
                # Move Top Soil Thickness to first position if it exists
                if top_soil_idx is not None and top_soil_idx != 0:
                    top_soil_row = df.iloc[top_soil_idx].copy()
                    df = df.drop(df.index[top_soil_idx]).reset_index(drop=True)
                    df = pd.concat([pd.DataFrame([top_soil_row]), df], ignore_index=True)
                    # Update bedrock index if it was affected
                    if bedrock_idx is not None and bedrock_idx > top_soil_idx:
                        bedrock_idx -= 1
                
                # Move Bedrock Depth to last position if it exists
                if bedrock_idx is not None and bedrock_idx != len(df) - 1:
                    bedrock_row = df.iloc[bedrock_idx].copy()
                    df = df.drop(df.index[bedrock_idx]).reset_index(drop=True)
                    df = pd.concat([df, pd.DataFrame([bedrock_row])], ignore_index=True)
                
                return df
            
            # Apply order enforcement
            df = enforce_order(df)
            
            # Default fallback
            rows = []
            for i in range(len(df)):
                row_data = {
                    "parameter": df.iloc[i]["parameter"],
                    "depth": df.iloc[i]["depth"]
                }
                rows.append(_build_stratigraphy_row(i, len(df), row_data))
            return rows, df.to_dict('list'), len(df) <= 1

        # Callback to update table data when inputs change
        @self.app.callback(
            Output("stratigraphy-table-data", "data", allow_duplicate=True),
            [
                Input({"type": "stratigraphy-parameter", "index": dash.dependencies.ALL}, "value"),
                Input({"type": "stratigraphy-depth", "index": dash.dependencies.ALL}, "value"),
            ],
            [
                dash.dependencies.State("stratigraphy-table-data", "data"),
            ],
            prevent_initial_call=True,
        )
        def update_stratigraphy_data(parameter_values, depth_values, table_data):
            """Update table data when parameter or depth values change."""
            import pandas as pd
            
            if not table_data or not isinstance(table_data, dict):
                return table_data
            
            # Convert to DataFrame
            df = pd.DataFrame(table_data)
            
            # Update the data with new values
            for i, (param_val, depth_val) in enumerate(zip(parameter_values, depth_values)):
                if i < len(df):
                    df.iloc[i, df.columns.get_loc("parameter")] = param_val or "Top Soil Thickness"
                    df.iloc[i, df.columns.get_loc("depth")] = depth_val or ""
            
            return df.to_dict('list')

    def get_theme_css(self, theme_name):
        """Get CSS for the selected theme."""
        theme_map = {
            "CERULEAN": dbc.themes.CERULEAN,
            "DARKLY": dbc.themes.DARKLY,
            "FLATLY": dbc.themes.FLATLY,
            "CYBORG": dbc.themes.CYBORG,
            "SLATE": dbc.themes.SLATE,
        }
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
