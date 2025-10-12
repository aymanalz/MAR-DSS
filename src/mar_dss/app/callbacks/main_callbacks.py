"""
Main dashboard callbacks for MAR DSS.
"""

import dash
import dash_bootstrap_components as dbc
from dash import Input, Output, html

# Import content creation functions
try:
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
    from mar_dss.app.components.hydro_tab import create_hydro_tab_content
    from mar_dss.app.components.reports_tab import create_reports_tab_content
    from mar_dss.app.components.scenarios_comparison_tab import (
        create_scenarios_comparison_content,
    )
    from mar_dss.app.components.water_source_tab import (
        create_general_tab_content,
    )
except ImportError:
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


def setup_main_callbacks(app, dashboard_instance):
    """Set up all main dashboard callbacks."""
    
    @app.callback(
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
                            [dashboard_instance.create_mar_purpose_section()], width=6
                        ),
                        dbc.Col(
                            [dashboard_instance.create_location_map_section()], width=6
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
                                [dashboard_instance.create_mar_purpose_section()], width=6
                            ),
                            dbc.Col(
                                [dashboard_instance.create_location_map_section()],
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
                                [dashboard_instance.create_mar_purpose_section()], width=6
                            ),
                            dbc.Col(
                                [dashboard_instance.create_location_map_section()],
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
                            [dashboard_instance.create_mar_purpose_section()], width=6
                        ),
                        dbc.Col(
                            [dashboard_instance.create_location_map_section()], width=6
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

    @app.callback(
        [Output("theme-selector", "value"), Output("theme-css", "href")],
        [Input("theme-selector", "value")],
    )
    def update_theme(selected_theme):
        """Update theme based on selection."""
        if selected_theme:
            dashboard_instance.current_theme = selected_theme

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

    @app.callback(
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
    @app.callback(
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
    @app.callback(
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
    @app.callback(
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
