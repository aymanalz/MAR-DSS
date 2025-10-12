"""
Hydrogeology tab callbacks for MAR DSS dashboard.
"""

import dash
import dash_bootstrap_components as dbc
import pandas as pd
from dash import Input, Output, dcc, html

from mar_dss.app.components.hydro_tab import create_hydro_tab_content, _build_stratigraphy_row


def setup_hydro_callbacks(app):
    """Set up all hydrogeology-related callbacks."""
    
    # Callback for stratigraphy layer management (existing stratigraphy section)
    @app.callback(
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
            display_name = layer_display_names.get(layer_type, layer_type)

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
                                                f"{display_name}",
                                                className="mb-1 fw-bold",
                                            ),
                                            html.P(
                                                f"Thickness: {thickness:.1f} m",
                                                className="mb-1 text-muted small",
                                            ),
                                        ],
                                        width=8,
                                    ),
                                    dbc.Col(
                                        [
                                            dbc.Button(
                                                [html.I(className="fas fa-trash")],
                                                id={"type": "delete-layer", "index": i},
                                                color="danger",
                                                size="sm",
                                                className="btn-sm",
                                            )
                                        ],
                                        width=4,
                                        className="text-end",
                                    ),
                                ]
                            ),
                            html.Hr(className="my-2"),
                            dbc.Row(
                                [
                                    dbc.Col(
                                        [
                                            html.Small(
                                                f"Conductivity: {layer_data.get('conductivity', 0):.1f} m/day",
                                                className="text-muted",
                                            )
                                        ],
                                        width=6,
                                    ),
                                    dbc.Col(
                                        [
                                            html.Small(
                                                f"Porosity: {layer_data.get('porosity', 0):.1f}%",
                                                className="text-muted",
                                            )
                                        ],
                                        width=6,
                                    ),
                                ]
                            ),
                        ],
                        className="p-2",
                    )
                ],
                className="mb-2",
                style={
                    "border-left": f"4px solid {color}",
                    "background-color": f"{color}10",
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

        return layer_cards, summary, layers_data, layers_data

    # Add callback to trigger stratigraphy rendering when hydrogeology tab is active
    @app.callback(
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
                    display_name = layer_display_names.get(layer_type, layer_type)

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
                                                        f"{display_name}",
                                                        className="mb-1 fw-bold",
                                                    ),
                                                    html.P(
                                                        f"Thickness: {thickness:.1f} m",
                                                        className="mb-1 text-muted small",
                                                    ),
                                                ],
                                                width=8,
                                            ),
                                            dbc.Col(
                                                [
                                                    dbc.Button(
                                                        [html.I(className="fas fa-trash")],
                                                        id={"type": "delete-layer", "index": i},
                                                        color="danger",
                                                        size="sm",
                                                        className="btn-sm",
                                                    )
                                                ],
                                                width=4,
                                                className="text-end",
                                            ),
                                        ]
                                    ),
                                    html.Hr(className="my-2"),
                                    dbc.Row(
                                        [
                                            dbc.Col(
                                                [
                                                    html.Small(
                                                        f"Conductivity: {layer_data.get('conductivity', 0):.1f} m/day",
                                                        className="text-muted",
                                                    )
                                                ],
                                                width=6,
                                            ),
                                            dbc.Col(
                                                [
                                                    html.Small(
                                                        f"Porosity: {layer_data.get('porosity', 0):.1f}%",
                                                        className="text-muted",
                                                    )
                                                ],
                                                width=6,
                                            ),
                                        ]
                                    ),
                                ],
                                className="p-2",
                            )
                        ],
                        className="mb-2",
                        style={
                            "border-left": f"4px solid {color}",
                            "background-color": f"{color}10",
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
                    ]
                )
        return dash.no_update, dash.no_update

    # Callback for stratigraphy table management
    @app.callback(
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
    @app.callback(
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
