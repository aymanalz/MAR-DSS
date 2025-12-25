"""
Content generation for Hydrogeologic Feasibility tab.
"""

import dash_bootstrap_components as dbc
from dash import html, dcc
import mar_dss.app.utils.data_storage as dash_storage
from mar_dss.app.callbacks.analysis_callbacks import get_session_graph, get_graph_inputs
from mar_dss.app.utils.hydrogeologic_feasibility import (
    calculate_hydrogeological_feasibility_score,
    create_feasibility_gauge,
    create_monthly_gw_depth_chart,
    create_component_scores_chart,
    create_stratigraphy_profile
)


def create_leaf_node_card(node_id, node_data, score_data):
    """Create a prominent card for a leaf (decision) node."""
    value = node_data.get('value')
    score = node_data.get('score')
    name = node_data.get('name', node_id)
    # Capitalize first letter of each word in the name
    if name:
        name = ' '.join(word.capitalize() for word in name.split())
    
    # Handle None values
    if value is None:
        color = "secondary"
        status_text = "N/A"
        value_display = "N/A"
        score_display = 0  # Set to 0 for progress bar
        score_text = "N/A"
    # Determine color based on value/score
    elif isinstance(value, bool):
        color = "success" if value else "danger"
        status_text = "✅ Feasible" if value else "❌ Not Feasible"
        score_display = score if score is not None else 0
        score_text = f"{score:.1f}%" if score is not None else "N/A"
    elif isinstance(value, (int, float)):
        score_display = score if score is not None else 0
        score_text = f"{score:.1f}%" if score is not None else "N/A"
        if score is not None:
            if score >= 80:
                color = "success"
                status_text = "✅ Highly Feasible"
            elif score >= 60:
                color = "info"
                status_text = "⚠️ Feasible"
            elif score >= 40:
                color = "warning"
                status_text = "⚠️ Conditionally Feasible"
            else:
                color = "danger"
                status_text = "❌ Infeasible"
        else:
            color = "secondary"
            status_text = "N/A"
    else:  # categorical
        score_display = score if score is not None else 0
        score_text = f"{score:.1f}%" if score is not None else "N/A"
        if score is not None:
            if score >= 80:
                color = "success"
            elif score >= 60:
                color = "info"
            elif score >= 40:
                color = "warning"
            else:
                color = "danger"
        else:
            color = "secondary"
        status_text = str(value) if value else "N/A"
    
    # Format value display (only if value is not None and wasn't already set)
    if value is None:
        value_display = "N/A"
    elif 'value_display' not in locals():
        if isinstance(value, float):
            if node_id in ['rechargability', 'confined_rechargability']:
                value_display = f"{value:.1f}%"
            elif node_id == 'annual_recharge_volume':
                value_display = f"{value:,.0f} ft³/year"
            elif node_id == 'k_min_vadose':
                value_display = f"{value:.3f} ft/day"
            else:
                value_display = f"{value:.2f}"
        elif isinstance(value, bool):
            value_display = "Yes" if value else "No"
        else:
            value_display = str(value) if value else "N/A"
    
    return dbc.Card(
        [
            dbc.CardHeader([
                html.H6(name, className="mb-0"),
                dbc.Badge("DECISION NODE", color="primary", className="ms-2")
            ]),
            dbc.CardBody([
                html.H4(value_display, className="text-center mb-2"),
                html.P(status_text, className="text-center mb-2"),
                dbc.Progress(value=score_display, color=color, className="mb-2"),
                html.Small(f"Score: {score_text}", className="text-muted d-block text-center")
            ])
        ],
        color=color,
        outline=True,
        className="mb-3 border-3"
    )


def create_hydrogeologic_feasibility_content_dynamic():
    """Create dynamic content for Hydrogeologic Feasibility tab."""
    try:
        # Get graph and evaluate
        graph = get_session_graph()
        if graph is None:
            return create_loading_content("Unable to load decision graph.")
        
        inputs = get_graph_inputs()
        graph.evaluate(inputs)
        graph.plotly()
        node_values = graph.get_node_values()
        
        # Get aquifer type
        aq_type = inputs.get('aq_type', '').lower() if inputs else ''
        is_unconfined = aq_type == 'unconfined'
        is_confined = aq_type == 'confined'
        
        # Calculate feasibility score
        score_data = calculate_hydrogeological_feasibility_score(graph, node_values)
        final_score = score_data.get('final_score', 0)
        breakdown = score_data.get('breakdown', {})
        leaf_nodes = breakdown.get('leaf_nodes', {})
        computational_nodes = breakdown.get('computational_nodes', {})
        
        # Create gauge chart
        gauge_fig, status, status_color = create_feasibility_gauge(final_score)
        
        # Get monthly GW depth
        monthly_gw_depth = inputs.get('monthly_gw_depth', [20]*12)
        if isinstance(monthly_gw_depth, (list, tuple)) and len(monthly_gw_depth) != 12:
            monthly_gw_depth = list(monthly_gw_depth) + [20] * (12 - len(monthly_gw_depth))
        elif not isinstance(monthly_gw_depth, (list, tuple)):
            monthly_gw_depth = [20] * 12
        
        op_gw_depth = node_values.get('op_gw_depth')
        
        # Get stratigraphy data
        stratigraphy_data = dash_storage.get_data("stratigraphy_data")
        
        # Filter leaf nodes by aquifer type
        relevant_leaf_nodes = {}
        for node_id, node_data in leaf_nodes.items():
            # Filter based on aquifer type
            if node_id == 'rechargability' and not is_unconfined:
                continue
            if node_id == 'confined_rechargability' and not is_confined:
                continue
            if node_id in ['leakage_significance', 'excessive_deep_aquifer'] and not is_confined:
                continue
            if node_id in ['gs_slope_significance', 'vadose_high_toxicity_present'] and not is_unconfined:
                continue
            relevant_leaf_nodes[node_id] = node_data
        
        # Format aquifer type for display
        aq_type_display = aq_type.capitalize() if aq_type else "Not Specified"
        
        # Build content
        content = [
            html.H3("Hydrogeologic Feasibility", className="mb-4"),
            dbc.Row([
                dbc.Col([
                    html.P(
                        "Assess the feasibility of MAR implementation based on hydrogeologic conditions.",
                        className="mb-2"
                    ),
                    html.P([
                        html.Strong("Aquifer Type: "),
                        html.Span(aq_type_display, className="text-primary")
                    ], className="mb-0")
                ], width=12)
            ], className="mb-4"),
            
            # Section 1: Overall Feasibility Score
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader(html.H5("Overall Feasibility Score", className="mb-0")),
                        dbc.CardBody([
                            dcc.Graph(figure=gauge_fig, config={'displayModeBar': False}),
                            dbc.Alert(
                                [
                                    html.H6(f"Status: {status}", className="mb-0"),
                                    html.Small(f"Final Score: {final_score:.1f}%", className="text-muted")
                                ],
                                color=status_color,
                                className="mt-2"
                            )
                        ])
                    ])
                ], width=12, className="mb-4")
            ]),
            
            # Section 2: Key Decision Nodes (Leaf Nodes)
            dbc.Row([
                dbc.Col([
                    html.H5("Key Decision Nodes", className="mb-3"),
                    html.P("Final assessment metrics that determine feasibility.", className="text-muted mb-3")
                ], width=12)
            ]),
        ]
        
        # Add leaf node cards if available
        if relevant_leaf_nodes:
            # Sort to put annual_recharge_volume first, then rechargability/confined_rechargability second
            def sort_key(x):
                node_id = x[0]
                if node_id == 'annual_recharge_volume':
                    return (0, 0)
                elif node_id in ['rechargability', 'confined_rechargability']:
                    return (1, 0)
                else:
                    return (2, node_id)
            
            sorted_leaf_nodes = sorted(
                relevant_leaf_nodes.items(),
                key=sort_key
            )
            col_width = 4 if len(relevant_leaf_nodes) > 2 else (6 if len(relevant_leaf_nodes) > 1 else 12)
            leaf_node_cols = [
                dbc.Col([
                    create_leaf_node_card(node_id, node_data, score_data)
                ], width=col_width)
                for node_id, node_data in sorted_leaf_nodes
            ]
            content.append(
                dbc.Row(leaf_node_cols, className="mb-4")
            )
        else:
            content.append(
                dbc.Alert(
                    "No decision nodes available. Please configure aquifer settings first.",
                    color="warning",
                    className="mb-4"
                )
            )
        
        # Continue with remaining sections
        content.extend([
            # Section 3: Component Scores Breakdown
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader(html.H5("Component Scores Breakdown", className="mb-0")),
                        dbc.CardBody([
                            dcc.Graph(
                                figure=create_component_scores_chart(breakdown),
                                config={'displayModeBar': True}
                            )
                        ])
                    ])
                ], width=12, className="mb-4")
            ]),
        ])
        
        # Section 6: Supporting Metrics (Collapsible)
        # Build computational metrics content
        if computational_nodes:
            computational_content = [
                html.Div([
                    html.H6(
                        ' '.join(word.capitalize() for word in (node_data.get('name', node_id) or node_id).split()),
                        className="mb-2"
                    ),
                    html.P(f"Value: {node_data.get('value') if node_data.get('value') is not None else 'N/A'}", className="mb-1"),
                    html.P(f"Score: {node_data.get('score', 0):.1f}%", className="mb-1"),
                    html.P(f"Weight: {node_data.get('weight', 0):.1f}", className="mb-0 text-muted")
                ], className="mb-3")
                for node_id, node_data in sorted(computational_nodes.items(), 
                                                 key=lambda x: x[1].get('score', 0) if x[1].get('score') is not None else 0, reverse=True)
            ]
        else:
            computational_content = [
                html.P("No computational metrics available.", className="text-muted")
            ]
        
        content.append(
            dbc.Row([
                dbc.Col([
                    dbc.Accordion([
                        dbc.AccordionItem(
                            computational_content,
                            title=f"Supporting Computational Metrics ({len(computational_nodes)} nodes)", 
                            item_id="computational-metrics"
                        )
                    ], start_collapsed=True, always_open=False)
                ], width=12, className="mb-4")
            ])
        )
        
        return content
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return create_error_content(str(e))


def create_loading_content(message="Loading feasibility assessment..."):
    """Create loading content."""
    return [
        html.H3("Hydrogeologic Feasibility", className="mb-4"),
        dbc.Alert(message, color="info")
    ]


def create_error_content(error_message):
    """Create error content."""
    return [
        html.H3("Hydrogeologic Feasibility", className="mb-4"),
        dbc.Alert(
            [
                html.H5("Error Loading Feasibility Assessment", className="alert-heading"),
                html.P(f"An error occurred: {error_message}", className="mb-0")
            ],
            color="danger"
        )
    ]

