"""
Main dashboard callbacks for MAR DSS.
"""
import tempfile
import os
from datetime import datetime
import pandas as pd


import dash
import dash_bootstrap_components as dbc
from dash import Input, Output, html, dependencies
from dash.dependencies import ClientsideFunction
import mar_dss.app.utils.data_storage as dash_storage

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
    from mar_dss.app.components.scenarios_comparison_tab import (
        create_scenarios_comparison_content,
    )
    from mar_dss.app.components.water_source_tab import (
        create_general_tab_content,
    )
    from mar_dss.app.components.overview_tab import (
        create_overview_content,
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
    from .components.scenarios_comparison_tab import (
        create_scenarios_comparison_content,
    )
    from .components.water_source_tab import create_general_tab_content
    from .components.overview_tab import create_overview_content


def setup_main_callbacks(app, dashboard_instance):
    """Set up all main dashboard callbacks."""
    
    # Import and set up overview callbacks
    try:
        from mar_dss.app.callbacks.overview_callbacks import setup_overview_callbacks
    except ImportError:
        from .overview_callbacks import setup_overview_callbacks
    
    setup_overview_callbacks(app)
    
    @app.callback(
        Output("main-content", "children"),
        [
            Input("top-tabs", "active_tab"),
        ],
    )
    def update_main_content(active_tab):
        """Update main content based on navigation."""
        if active_tab == "overview":
            return create_overview_content()
        elif active_tab == "water-source":
            return create_general_tab_content()
        elif active_tab == "hydrogeology":
            return create_hydro_tab_content()
        elif active_tab == "environmental":
            # Import environmental impact tab content
            try:
                from mar_dss.app.components.environmental_impact_tab import create_environmental_impact_content
            except ImportError:
                from ..components.environmental_impact_tab import create_environmental_impact_content
            return create_environmental_impact_content()
        elif active_tab == "legal":
            # Import legal constraints tab content
            try:
                from mar_dss.app.components.legal_constraints_tab import create_legal_constraints_content
            except ImportError:
                from ..components.legal_constraints_tab import create_legal_constraints_content
            return create_legal_constraints_content()
        elif active_tab == "engineering-options":
            # Import engineering options tab content
            try:
                from mar_dss.app.components.engineering_options_tab import create_engineering_options_content
            except ImportError:
                from ..components.engineering_options_tab import create_engineering_options_content
            return create_engineering_options_content()
        elif active_tab == "analysis":
            # Import analysis tab content
            try:
                from mar_dss.app.components.analysis_tab import create_analysis_tab_content
            except ImportError:
                from ..components.analysis_tab import create_analysis_tab_content
            return create_analysis_tab_content()
        else:
            return create_overview_content()

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


    # Add callback to sync flow-data-store with dash_storage when tab is accessed
    @app.callback(
        Output("flow-data-store", "data"),
        [
            Input("top-tabs", "active_tab"),
        ],
        prevent_initial_call=False
    )
    def sync_flow_data_store(active_tab):
        """Sync flow-data-store with dash_storage when water source tab is accessed."""
        # Get flow data from dash_storage
        months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
        default_flows = [4500, 4200, 2800, 2200, 1800, 1500, 1200, 1000, 1300, 2000, 3800, 4100]
        monthly_flows_raw = dash_storage.get_data("monthly_flow")
        
        # Handle case where data might be loaded as string from CSV
        if monthly_flows_raw is None:
            monthly_flows = default_flows
        elif isinstance(monthly_flows_raw, str):
            # Try to parse string representation of list
            try:
                import ast
                monthly_flows = ast.literal_eval(monthly_flows_raw)
                if not isinstance(monthly_flows, list) or len(monthly_flows) != 12:
                    monthly_flows = default_flows
            except (ValueError, SyntaxError):
                monthly_flows = default_flows
        elif isinstance(monthly_flows_raw, list):
            monthly_flows = monthly_flows_raw
        else:
            monthly_flows = default_flows
        
        # Ensure we have exactly 12 values
        if len(monthly_flows) != 12:
            monthly_flows = default_flows
        
        # Ensure all values are numeric
        try:
            monthly_flows = [float(flow) if flow is not None else 0.0 for flow in monthly_flows]
        except (ValueError, TypeError):
            monthly_flows = default_flows
        
        # Convert list to dictionary format
        flow_data = {month: flow for month, flow in zip(months, monthly_flows)}
        return flow_data
    
    # Add callback to sync stratigraphy-data-store with dash_storage when hydrogeology tab is accessed
    @app.callback(
        Output("stratigraphy-data-store", "data", allow_duplicate=True),
        [
            Input("top-tabs", "active_tab"),
        ],
        prevent_initial_call=True
    )
    def sync_stratigraphy_data_store(active_tab):
        """Sync stratigraphy-data-store with dash_storage when hydrogeology tab is accessed."""
        if active_tab == "hydrogeology":
            stored_data = dash_storage.get_data("stratigraphy_data")
            if stored_data:
                return stored_data
            # Return defaults if no stored data
            return [
                {"layer": "Sand", "thickness": 60.0, "conductivity": 10.0, "storage": 0.0001, "yield": 0.25, "selected": False},
                {"layer": "Silt", "thickness": 60.0, "conductivity": 0.01, "storage": 0.0001, "yield": 0.10, "selected": False},
                {"layer": "Gravel", "thickness": 60.0, "conductivity": 100.0, "storage": 0.0001, "yield": 0.30, "selected": False}
            ]
        return dash.no_update
    
    # Add callback to sync groundwater-data-store with dash_storage when hydrogeology tab is accessed
    @app.callback(
        Output("groundwater-data-store", "data", allow_duplicate=True),
        [
            Input("top-tabs", "active_tab"),
        ],
        prevent_initial_call=True
    )
    def sync_groundwater_data_store(active_tab):
        """Sync groundwater-data-store with dash_storage when hydrogeology tab is accessed."""
        if active_tab == "hydrogeology":
            stored_data = dash_storage.get_data("groundwater_data")
            if stored_data:
                return stored_data
            # Return defaults if no stored data
            return [
                {"month": "January", "elevation": 75.0, "selected": False},
                {"month": "February", "elevation": 72.0, "selected": False},
                {"month": "March", "elevation": 78.0, "selected": False},
                {"month": "April", "elevation": 82.0, "selected": False},
                {"month": "May", "elevation": 85.0, "selected": False},
                {"month": "June", "elevation": 88.0, "selected": False},
                {"month": "July", "elevation": 90.0, "selected": False},
                {"month": "August", "elevation": 89.0, "selected": False},
                {"month": "September", "elevation": 86.0, "selected": False},
                {"month": "October", "elevation": 83.0, "selected": False},
                {"month": "November", "elevation": 79.0, "selected": False},
                {"month": "December", "elevation": 76.0, "selected": False}
            ]
        return dash.no_update

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

    # Add callback for updating monthly flow chart from table and saving to data storage
    @app.callback(
        Output("monthly-flow-chart", "figure"),
        [Input("flow-data-table", "data")],
    )
    def update_monthly_flow_chart_from_table(table_data):
        """Update the monthly flow chart based on table data and save to data storage."""
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

        # Extract flow data from table and save to data storage as list of 12 values
        monthly_flows = []
        flow_data = {}
        for row in table_data:
            month = row["Month"]
            flow = row.get("Flow (m³/month)", 0)
            flow_value = flow if flow is not None else 0
            flow_data[month] = flow_value
            monthly_flows.append(flow_value)
        
        # Save to data storage as list of 12 values
        dash_storage.set_data("monthly_flow", monthly_flows)

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


    # Callback for Save button - save current project
    @app.callback(
        Output("main-content", "children", allow_duplicate=True),
        [Input("btn-save", "n_clicks")],
        prevent_initial_call=True
    )
    def handle_save_project(n_clicks):
        """Handle saving the current project."""
        if n_clicks:
            # Save current data to storage
            try:
                # Get current data from storage
                data = dash_storage.get_data_storage()
                if not data:
                    data = {}
                
                # Add timestamp                
                data["last_saved"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                if "workspace" in data:
                    folder_path = data["workspace"]
                else:
                    # Create a temporary folder                    
                    temp_dir = tempfile.mkdtemp(prefix="mar_dss_temp_")
                    folder_path = temp_dir
                if "filename" in data:
                    filename = data["filename"]
                else:
                    # Create filename with timestamp
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    filename = f"mar_dss_project_{timestamp}.csv"
                fn = os.path.join(folder_path, filename)

                # covert the data to pandas dataframe, keys are in a column called "key" and values are in a column called "value"
                df_ = []
                for key, value in data.items():
                    df_.append([key, value])
                df = pd.DataFrame(df_, columns=["key", "value"])
                df.to_csv(fn, index=False)

                
                # Save to storage
                #dash_storage.set_data("all_data", data)
                
                import dash_bootstrap_components as dbc
                return [
                    dbc.Alert(
                        f"Project saved successfully at {fn}",
                        color="success",
                        className="mb-3"
                    ),
                    create_overview_content()[0]  # Show overview content
                ]
            except Exception as e:
                import dash_bootstrap_components as dbc
                return [
                    dbc.Alert(
                        f"Error saving project: {str(e)}",
                        color="danger",
                        className="mb-3"
                    ),
                    create_overview_content()[0]  # Show overview content
                ]
        return dash.no_update

    # Callback for New button - create new project
    @app.callback(
        Output("main-content", "children", allow_duplicate=True),
        [Input("btn-new", "n_clicks")],
        prevent_initial_call=True
    )
    def handle_new_project(n_clicks):
        """Handle creating a new project."""
        if n_clicks:
            # Clear all data storage
            dash_storage.clear_data()
            
            # Reset to default values
            dash_storage.set_data("project_name", "")
            dash_storage.set_data("analysis_date", "")
            dash_storage.set_data("mar_purpose", ["secure_water_supply"])
            dash_storage.set_data("ground_surface_slope", 0.5)
            dash_storage.set_data("max_available_area", 1.0)
            dash_storage.set_data("land_use", "Urban Residential")
            dash_storage.set_data("water_source", "surface_water_sources")
            dash_storage.set_data("proximity_distance", 1.0)
            dash_storage.set_data("water_conveyance", "open_canals_ditches")
            dash_storage.set_data("water_ownership", "legal_rights")
            dash_storage.set_data("pumping_needed", "no")
            dash_storage.set_data("monthly_flow", [4500, 4200, 2800, 2200, 1800, 1500, 1200, 1000, 1300, 2000, 3800, 4100])
            dash_storage.set_data("physical_parameters", [])
            dash_storage.set_data("chemical_parameters", [])
            dash_storage.set_data("biological_indicators", [])
            dash_storage.set_data("emerging_contaminants", [])
            # Reset water quality and geochemistry data
            dash_storage.set_data("tss_turbidity_risk", "LOW RISK")
            dash_storage.set_data("doc_toc_risk", "LOW RISK")
            dash_storage.set_data("ph_alkalinity_risk", "LOW RISK")
            dash_storage.set_data("tds_salinity_risk", "LOW RISK")
            dash_storage.set_data("inorganic_contaminants_risk", "LOW RISK")
            dash_storage.set_data("emerging_contaminants_risk", "LOW RISK")
            dash_storage.set_data("redox_compatibility_risk", "LOW RISK")
            dash_storage.set_data("pathogen_risk", "LOW RISK")
            dash_storage.set_data("vadose_zone_pollution", "None")
            # Reset hydrogeology data
            dash_storage.set_data("aquifer_type", "unconfined")
            dash_storage.set_data("max_allowed_head", 1.0)
            dash_storage.set_data("stratigraphy_data", [
                {"layer": "Sand", "thickness": 60.0, "conductivity": 10.0, "storage": 0.0001, "yield": 0.25, "selected": False},
                {"layer": "Silt", "thickness": 60.0, "conductivity": 0.01, "storage": 0.0001, "yield": 0.10, "selected": False},
                {"layer": "Gravel", "thickness": 60.0, "conductivity": 100.0, "storage": 0.0001, "yield": 0.30, "selected": False}
            ])
            dash_storage.set_data("groundwater_data", [
                {"month": "January", "elevation": 75.0, "selected": False},
                {"month": "February", "elevation": 72.0, "selected": False},
                {"month": "March", "elevation": 78.0, "selected": False},
                {"month": "April", "elevation": 82.0, "selected": False},
                {"month": "May", "elevation": 85.0, "selected": False},
                {"month": "June", "elevation": 88.0, "selected": False},
                {"month": "July", "elevation": 90.0, "selected": False},
                {"month": "August", "elevation": 89.0, "selected": False},
                {"month": "September", "elevation": 86.0, "selected": False},
                {"month": "October", "elevation": 83.0, "selected": False},
                {"month": "November", "elevation": 79.0, "selected": False},
                {"month": "December", "elevation": 76.0, "selected": False}
            ])
            dash_storage.set_data("ground_surface_elevation", 120.0)
            dash_storage.set_data("max_mar_storage_depth", 20.0)
            dash_storage.set_data("extension_length", 100.0)
            dash_storage.set_data("extension_width", 50.0)
            dash_storage.set_data("extension_rotation", 0.0)
            dash_storage.set_data("upstream_head", 10.0)
            dash_storage.set_data("downstream_head", 5.0)
            
            import dash_bootstrap_components as dbc
            return [
                dbc.Alert(
                    "New project created! All data has been reset to defaults.",
                    color="info",
                    className="mb-3"
                ),
                create_overview_content()[0]  # Show overview content
            ]
        return dash.no_update

    # Callback for Save As button - save project with new name
    @app.callback(
        Output("main-content", "children", allow_duplicate=True),
        [Input("btn-save-as", "n_clicks")],
        prevent_initial_call=True
    )
    def handle_save_as_project(n_clicks):
        """Handle saving the project with a new name."""
        if n_clicks:
            # Create a file dialog using dcc.Upload component
            import dash_bootstrap_components as dbc
            from dash import dcc
            from datetime import datetime
            
            # Create a clean, serializable data structure
            project_data = {
                "project_name": dash_storage.get_data("project_name") or "",
                "analysis_date": dash_storage.get_data("analysis_date") or "",
                "mar_purpose": dash_storage.get_data("mar_purpose") or ["secure_water_supply"],
                "last_saved": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "version": "1.0",
                "description": "MAR DSS Project File"
            }
            
            # Create JSON string for download
            project_data = dash_storage.get_data_storage()
            
            # Create a clean, serializable copy to avoid circular references
            clean_data = {}
            for key, value in project_data.items():
                try:
                    # Test if the value can be serialized
                    json.dumps(value)
                    clean_data[key] = value
                except (TypeError, ValueError):
                    # Skip values that can't be serialized
                    continue
            
            import json
            json_string = json.dumps(clean_data, indent=2)
            
            # Create a download interface with file save dialog
            from dash import dcc
            return [
                dbc.Alert(
                    "Save As - Click the download button below to save your project. The browser will open a file save dialog.",
                    color="info",
                    className="mb-3"
                ),
                dbc.Card([
                    dbc.CardBody([
                        html.H5("Save Project As", className="card-title"),
                        html.P("Your project data will be saved as a JSON file that you can load later using the Open button."),
                        dbc.Button(
                            [html.I(className="fas fa-download me-2"), "Download Project File"],
                            id="download-project-btn",
                            color="success",
                            className="mb-3"
                        ),
                        dcc.Download(
                            id="download-project-file",
                            data=dict(content=json_string, filename="mar_project.json")
                        )
                    ])
                ], className="mb-3"),
                create_overview_content()[0]  # Show overview content
            ]
        return dash.no_update

    # Callback for download button - trigger file download
    @app.callback(
        Output("download-project-file", "data"),
        [Input("download-project-btn", "n_clicks")],
        prevent_initial_call=True
    )
    def trigger_download(n_clicks):
        """Trigger the project file download."""
        if n_clicks:
            # Create a clean, serializable data structure
            # project_data = {
            #     "project_name": dash_storage.get_data("project_name") or "",
            #     "analysis_date": dash_storage.get_data("analysis_date") or "",
            #     "mar_purpose": dash_storage.get_data("mar_purpose") or ["secure_water_supply"],
            #     "last_saved": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            #     "version": "1.0",
            #     "description": "MAR DSS Project File"
            # }
            
            # Create JSON string for download
            project_data = dash_storage.get_data_storage()
            
            # Create a clean, serializable copy to avoid circular references
            clean_data = {}
            for key, value in project_data.items():
                try:
                    # Test if the value can be serialized
                    json.dumps(value)
                    clean_data[key] = value
                except (TypeError, ValueError):
                    # Skip values that can't be serialized
                    continue
            
            import json
            json_string = json.dumps(clean_data, indent=2)
            
            # Generate filename with timestamp
            from datetime import datetime
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"mar_project_{timestamp}.json"
            
            return dict(content=json_string, filename=filename)
        return dash.no_update


    # Client-side resize to force Leaflet/Mapbox to re-render when tab becomes visible
    app.clientside_callback(
        ClientsideFunction(namespace="clientside", function_name="resizeMapOnTab"),
        Output("runoff-map", "id", allow_duplicate=True),  # dummy output; will always return no_update
        Input("water-source-tabs", "active_tab"),
        prevent_initial_call=True,
    )

    # Callback for water source dropdown - saves to data storage
    @app.callback(
        Output("water-source-dropdown", "value"),
        [
            Input("water-source-dropdown", "value"),
            Input("water-source-dropdown", "id")
        ],
        prevent_initial_call=False
    )
    def handle_water_source_selection(value, component_id):
        """Handle water source selection and save to data storage."""
        ctx = dash.callback_context
        
        if not ctx.triggered:
            # Initial load - get saved water source or use default, and save it
            water_source = dash_storage.get_data("water_source") or "surface_water_sources"
            dash_storage.set_data("water_source", water_source)
            return water_source
        
        # Get the current selection
        current_selection = value if value else "surface_water_sources"
        
        # Save water source selection to data storage
        dash_storage.set_data("water_source", current_selection)
        
        return current_selection

    # Callback for proximity distance input - saves to data storage
    @app.callback(
        Output("proximity-distance-input", "value"),
        [
            Input("proximity-distance-input", "value"),
            Input("proximity-distance-input", "n_blur"),
            Input("proximity-distance-input", "n_submit"),
            Input("proximity-distance-input", "id")
        ],
        prevent_initial_call=False
    )
    def handle_proximity_distance_input(value, n_blur, n_submit, component_id):
        """Handle proximity distance input for all triggers: value change, blur, submit, and load."""
        ctx = dash.callback_context
        
        if not ctx.triggered:
            # Initial load - get saved proximity distance or use default, and save it
            proximity_distance = dash_storage.get_data("proximity_distance") or 1.0
            dash_storage.set_data("proximity_distance", proximity_distance)
            return proximity_distance
        
        # Get the current value from the input
        current_value = value if value is not None else 1.0
        
        # Determine which trigger caused the callback
        trigger_id = ctx.triggered[0]["prop_id"].split(".")[0]
        trigger_prop = ctx.triggered[0]["prop_id"].split(".")[1]
        
        # Save proximity distance for all triggers except initial load
        if trigger_prop != "id":
            dash_storage.set_data("proximity_distance", current_value)
        
        return current_value

    # Callback for water conveyance dropdown - saves to data storage
    @app.callback(
        Output("water-conveyance-dropdown", "value"),
        [
            Input("water-conveyance-dropdown", "value"),
            Input("water-conveyance-dropdown", "id")
        ],
        prevent_initial_call=False
    )
    def handle_water_conveyance_selection(value, component_id):
        """Handle water conveyance selection and save to data storage."""
        ctx = dash.callback_context
        
        if not ctx.triggered:
            # Initial load - get saved water conveyance or use default, and save it
            water_conveyance = dash_storage.get_data("water_conveyance") or "open_canals_ditches"
            dash_storage.set_data("water_conveyance", water_conveyance)
            return water_conveyance
        
        # Get the current selection
        current_selection = value if value else "open_canals_ditches"
        
        # Save water conveyance selection to data storage
        dash_storage.set_data("water_conveyance", current_selection)
        
        return current_selection

    # Callback for water ownership radio - saves to data storage
    @app.callback(
        Output("water-ownership-radio", "value"),
        [
            Input("water-ownership-radio", "value"),
            Input("water-ownership-radio", "id")
        ],
        prevent_initial_call=False
    )
    def handle_water_ownership_selection(value, component_id):
        """Handle water ownership selection and save to data storage."""
        ctx = dash.callback_context
        
        if not ctx.triggered:
            # Initial load - get saved water ownership or use default, and save it
            water_ownership = dash_storage.get_data("water_ownership") or "legal_rights"
            dash_storage.set_data("water_ownership", water_ownership)
            return water_ownership
        
        # Get the current selection
        current_selection = value if value else "legal_rights"
        
        # Save water ownership selection to data storage
        dash_storage.set_data("water_ownership", current_selection)
        
        return current_selection

    # Callback for pumping needed radio - saves to data storage
    @app.callback(
        Output("pumping-needed-radio", "value"),
        [
            Input("pumping-needed-radio", "value"),
            Input("pumping-needed-radio", "id")
        ],
        prevent_initial_call=False
    )
    def handle_pumping_needed_selection(value, component_id):
        """Handle pumping needed selection and save to data storage."""
        ctx = dash.callback_context
        
        if not ctx.triggered:
            # Initial load - get saved pumping needed value or use default, and save it
            pumping_needed = dash_storage.get_data("pumping_needed") or "no"
            dash_storage.set_data("pumping_needed", pumping_needed)
            return pumping_needed
        
        # Get the current selection
        current_selection = value if value else "no"
        
        # Save pumping needed selection to data storage
        dash_storage.set_data("pumping_needed", current_selection)
        
        return current_selection

    # Callback for physical parameters checklist - saves to data storage
    @app.callback(
        Output("physical-parameters", "value"),
        [
            Input("physical-parameters", "value"),
            Input("physical-parameters", "id")
        ],
        prevent_initial_call=False
    )
    def handle_physical_parameters_selection(value, component_id):
        """Handle physical parameters checklist selections and save to data storage."""
        ctx = dash.callback_context
        
        if not ctx.triggered:
            # Initial load - get saved physical parameters or use default, and save it
            physical_params = dash_storage.get_data("physical_parameters") or []
            dash_storage.set_data("physical_parameters", physical_params)
            return physical_params
        
        # Get the current selections
        current_selections = value if value else []
        
        # Save physical parameters to data storage
        dash_storage.set_data("physical_parameters", current_selections)
        
        return current_selections

    # Callback for chemical parameters checklist - saves to data storage
    @app.callback(
        Output("chemical-parameters", "value"),
        [
            Input("chemical-parameters", "value"),
            Input("chemical-parameters", "id")
        ],
        prevent_initial_call=False
    )
    def handle_chemical_parameters_selection(value, component_id):
        """Handle chemical parameters checklist selections and save to data storage."""
        ctx = dash.callback_context
        
        if not ctx.triggered:
            # Initial load - get saved chemical parameters or use default, and save it
            chemical_params = dash_storage.get_data("chemical_parameters") or []
            dash_storage.set_data("chemical_parameters", chemical_params)
            return chemical_params
        
        # Get the current selections
        current_selections = value if value else []
        
        # Save chemical parameters to data storage
        dash_storage.set_data("chemical_parameters", current_selections)
        
        return current_selections

    # Callback for biological indicators checklist - saves to data storage
    @app.callback(
        Output("biological-indicators", "value"),
        [
            Input("biological-indicators", "value"),
            Input("biological-indicators", "id")
        ],
        prevent_initial_call=False
    )
    def handle_biological_indicators_selection(value, component_id):
        """Handle biological indicators checklist selections and save to data storage."""
        ctx = dash.callback_context
        
        if not ctx.triggered:
            # Initial load - get saved biological indicators or use default, and save it
            biological_indicators = dash_storage.get_data("biological_indicators") or []
            dash_storage.set_data("biological_indicators", biological_indicators)
            return biological_indicators
        
        # Get the current selections
        current_selections = value if value else []
        
        # Save biological indicators to data storage
        dash_storage.set_data("biological_indicators", current_selections)
        
        return current_selections

    # Callback for emerging contaminants checklist - saves to data storage
    @app.callback(
        Output("emerging-contaminants", "value"),
        [
            Input("emerging-contaminants", "value"),
            Input("emerging-contaminants", "id")
        ],
        prevent_initial_call=False
    )
    def handle_emerging_contaminants_selection(value, component_id):
        """Handle emerging contaminants checklist selections and save to data storage."""
        ctx = dash.callback_context
        
        if not ctx.triggered:
            # Initial load - get saved emerging contaminants or use default, and save it
            emerging_contaminants = dash_storage.get_data("emerging_contaminants") or []
            dash_storage.set_data("emerging_contaminants", emerging_contaminants)
            return emerging_contaminants
        
        # Get the current selections
        current_selections = value if value else []
        
        # Save emerging contaminants to data storage
        dash_storage.set_data("emerging_contaminants", current_selections)
        
        return current_selections

