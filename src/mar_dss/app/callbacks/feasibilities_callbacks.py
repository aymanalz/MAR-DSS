"""
Callbacks for the Feasibilities tab.
"""

import dash
from dash import Input, Output, html, dcc
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
import pandas as pd
import mar_dss.app.utils.data_storage as dash_storage


def setup_feasibilities_callbacks(app):
    """Set up all callbacks for the Feasibilities tab."""
    
    @app.callback(
        Output("analysis-feasibilities-content", "children"),
        [Input("analysis-tabs", "active_tab")],
        prevent_initial_call=True
    )
    def load_feasibilities_content(active_tab):
        """Load feasibilities content when the tab is accessed."""
        if active_tab == "analysis-feasibilities":
            try:
                from mar_dss.app.components.feasibilities_tab import create_feasibilities_content
            except ImportError:
                from ..components.feasibilities_tab import create_feasibilities_content
            return create_feasibilities_content()
        return "Loading..."
    
    @app.callback(
        [Output("executive-summary-content", "children"),
         Output("decision-funnel-chart", "figure"),
         Output("decision-funnel-stats", "children"),
         Output("constraints-heatmap-chart", "figure"),
         Output("constraints-heatmap-legend", "children"),
         Output("capital-cost-chart", "figure"),
         Output("maintenance-cost-chart", "figure"),
         Output("npv-cost-chart", "figure")],
        [Input("analysis-tabs", "active_tab"),
         Input("knowledge-graph-store", "data")],
        prevent_initial_call=False
    )
    def update_feasibilities_dashboard(active_tab, graph_store):
        """Update Executive Summary and Decision Funnel based on DSS results."""
        # Only update if we're on the feasibilities tab
        if active_tab != "analysis-feasibilities":
            return dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update
        
        # Get DSS results from storage
        dss_results = dash_storage.get_data("dss_results")
        
        if dss_results is None or not hasattr(dss_results, 'results') or not dss_results.results:
            # No results available
            no_data_msg = html.Div(
                [
                    html.P(
                        "No DSS evaluation results available. Please run the feasibility analysis first.",
                        className="text-muted text-center p-4"
                    )
                ]
            )
            empty_fig = go.Figure()
            empty_fig.update_layout(
                title="Decision Funnel",
                xaxis_title="Number of Options",
                yaxis_title="",
                template="plotly_white",
                height=400
            )
            empty_stats = html.Div()
            empty_heatmap_fig = go.Figure()
            empty_heatmap_fig.update_layout(
                title="Constraints Heatmap",
                template="plotly_white",
                height=400
            )
            empty_heatmap_legend = html.Div()
            empty_capital_fig = go.Figure()
            empty_capital_fig.update_layout(
                title="Capital Cost",
                template="plotly_white",
                height=350
            )
            empty_maintenance_fig = go.Figure()
            empty_maintenance_fig.update_layout(
                title="Maintenance Cost",
                template="plotly_white",
                height=350
            )
            empty_npv_fig = go.Figure()
            empty_npv_fig.update_layout(
                title="NPV (20 years)",
                template="plotly_white",
                height=350
            )
            return no_data_msg, empty_fig, empty_stats, empty_heatmap_fig, empty_heatmap_legend, empty_capital_fig, empty_maintenance_fig, empty_npv_fig
        
        results = dss_results.results
        filters = getattr(dss_results, 'filters', {})
        
        # Categorize options
        recommended = []
        conditional = []
        rejected = []
        
        # Count statistics for funnel
        total_options = len(results)
        hard_constraint_fails = 0
        soft_rule_rejects = 0
        after_hard_constraints = 0
        after_soft_rules = 0
        recommended_count = 0
        
        for option_name, result in results.items():
            status = result.get("status", "Unknown")
            cost = result.get("cost", [])
            benefit_score = result.get("benefit_score", 0.0) * 100  # Convert to percentage
            warnings = result.get("warnings", [])
            mitigations = result.get("mitigations", [])
            
            # Format cost - get base cost from option if available
            # Try to get from cost mapping first
            cost_mapping = dash_storage.get_data("cost_mapping")
            if cost_mapping and option_name in cost_mapping:
                cost_data = cost_mapping[option_name]
                if isinstance(cost_data, dict):
                    cost_val = cost_data.get("capital", 0)
                else:
                    cost_val = float(cost_data) if cost_data else 0
            elif isinstance(cost, list):
                if len(cost) > 0:
                    # Sum up cost penalties if it's a list
                    try:
                        cost_val = sum(float(c) for c in cost if isinstance(c, (int, float, str)))
                    except (ValueError, TypeError):
                        cost_val = 0
                else:
                    cost_val = 0
            else:
                cost_val = float(cost) if cost else 0
            
            cost_str = f"${cost_val/1e6:.1f}M" if cost_val >= 1e6 else f"${cost_val/1e3:.0f}K" if cost_val > 0 else "N/A"
            
            # Check filters to count hard constraint fails
            passed_hard = True
            passed_soft = True
            
            if option_name in filters:
                filter_data = filters[option_name]
                hard_constraints = filter_data.get('hard', [])
                soft_constraints = filter_data.get('soft', [])
                
                # Check hard constraint failures
                failed_hard = [hc for hc in hard_constraints if not hc.get("pass", True)]
                if failed_hard:
                    hard_constraint_fails += 1
                    passed_hard = False
                    rejected.append({
                        "name": option_name,
                        "reason": f"Hard constraint: {', '.join([hc.get('name', 'Unknown') for hc in failed_hard])}"
                    })
                else:
                    after_hard_constraints += 1
                
                # Check soft rule rejects (level 4 or hard soft constraints with level >= 2)
                rejected_soft_list = []
                for sc in soft_constraints:
                    response = sc.get("response", 0)
                    is_hard = sc.get("hard", True)
                    if response == 4 or (is_hard and response >= 2):
                        rejected_soft_list.append(sc.get('name', 'Unknown'))
                
                if rejected_soft_list:
                    soft_rule_rejects += 1
                    passed_soft = False
                    if passed_hard:  # Only add to rejected if it passed hard constraints
                        rejected.append({
                            "name": option_name,
                            "reason": f"Soft rule reject: {', '.join(rejected_soft_list)}"
                        })
                elif passed_hard:
                    after_soft_rules += 1
            else:
                # No filters available, assume passed if status is not Rejected
                if status != "Rejected":
                    after_hard_constraints += 1
                    after_soft_rules += 1
            
            # Only categorize if it passed both hard and soft constraints
            if not passed_hard or not passed_soft:
                continue
            
            # Categorize by status
            if status == "Recommended":
                recommended.append({
                    "name": option_name,
                    "cost": cost_str,
                    "benefit": f"{benefit_score:.0f}",
                    "description": "Meets all feasibility criteria"
                })
                recommended_count += 1
            elif status == "Conditionally Recommended":
                conditional.append({
                    "name": option_name,
                    "cost": cost_str,
                    "benefit": f"{benefit_score:.0f}",
                    "requirements": ", ".join(mitigations) if mitigations else "Additional review required"
                })
            elif status == "Recommended with Warnings":
                recommended.append({
                    "name": option_name,
                    "cost": cost_str,
                    "benefit": f"{benefit_score:.0f}",
                    "description": f"Warnings: {', '.join(warnings)}" if warnings else "Meets criteria with warnings"
                })
                recommended_count += 1
            else:  # Rejected
                rejected.append({
                    "name": option_name,
                    "reason": f"Status: {status}"
                })
        
        # Build Executive Summary content
        executive_summary = []
        
        # Recommended section
        if recommended:
            executive_summary.append(
                html.Div(
                    [
                        html.H5("Recommended", className="text-success fw-bold mb-3"),
                        *[
                            html.Div(
                                [
                                    html.Strong(f"{opt['name']}:", className="d-block"),
                                    html.Span(f"Cost: {opt['cost']} | Benefit: {opt['benefit']}", className="d-block text-muted"),
                                    html.Small(opt.get('description', ''), className="d-block text-muted mt-1")
                                ],
                                className="mb-3 p-2",
                                style={"borderLeft": "3px solid #28a745", "backgroundColor": "#f8f9fa"}
                            )
                            for opt in recommended
                        ]
                    ],
                    className="mb-4"
                )
            )
        
        # Conditional section
        if conditional:
            executive_summary.append(
                html.Div(
                    [
                        html.H5("Conditional", className="text-warning fw-bold mb-3"),
                        *[
                            html.Div(
                                [
                                    html.Strong(f"{opt['name']}:", className="d-block"),
                                    html.Span(f"Cost: {opt['cost']} | Benefit: {opt['benefit']}", className="d-block text-muted"),
                                    html.Small(f"Requirements: {opt['requirements']}", className="d-block text-muted mt-1")
                                ],
                                className="mb-3 p-2",
                                style={"borderLeft": "3px solid #ffc107", "backgroundColor": "#f8f9fa"}
                            )
                            for opt in conditional
                        ]
                    ],
                    className="mb-4"
                )
            )
        
        # Rejected section
        if rejected:
            executive_summary.append(
                html.Div(
                    [
                        html.H5("Rejected", className="text-danger fw-bold mb-3"),
                        *[
                            html.Div(
                                [
                                    html.Strong(f"{opt['name']}:", className="d-block"),
                                    html.Small(f"Reason: {opt['reason']}", className="d-block text-muted mt-1")
                                ],
                                className="mb-3 p-2",
                                style={"borderLeft": "3px solid #dc3545", "backgroundColor": "#f8f9fa"}
                            )
                            for opt in rejected
                        ]
                    ]
                )
            )
        
        if not executive_summary:
            executive_summary = [
                html.P("No options evaluated yet.", className="text-muted text-center p-4")
            ]
        
        # Create Decision Funnel chart
        funnel_categories = ["All Options", "After Hard Constraints", "After Soft Rules", "Recommended"]
        funnel_values = [
            total_options,
            after_hard_constraints,
            after_soft_rules,
            recommended_count
        ]
        
        # Colors for each stage
        colors = ["#6c757d", "#007bff", "#28a745", "#28a745"]
        
        fig = go.Figure()
        fig.add_trace(
            go.Bar(
                x=funnel_values,
                y=funnel_categories,
                orientation='h',
                marker_color=colors,
                text=[str(v) for v in funnel_values],
                textposition='auto',
            )
        )
        fig.update_layout(
            title="Decision Funnel",
            xaxis_title="Number of Options",
            yaxis_title="",
            template="plotly_white",
            height=300,
            autosize=False,  # Prevent automatic resizing
            showlegend=False,
            margin=dict(l=150, r=50, t=50, b=50),
            uirevision='constant'  # Prevent UI from resetting on updates
        )
        
        # Create summary statistics
        stats = html.Div(
            [
                html.Div(
                    [
                        html.Strong(f"{total_options}", className="d-block"),
                        html.Small("Options Evaluated", className="text-muted")
                    ],
                    className="text-center me-3"
                ),
                html.Div(
                    [
                        html.Strong(f"{hard_constraint_fails}", className="d-block text-danger"),
                        html.Small("Hard Constraint Fail", className="text-muted")
                    ],
                    className="text-center me-3"
                ),
                html.Div(
                    [
                        html.Strong(f"{soft_rule_rejects}", className="d-block text-danger"),
                        html.Small("Soft Rule Reject", className="text-muted")
                    ],
                    className="text-center me-3"
                ),
                html.Div(
                    [
                        html.Strong(f"{recommended_count}", className="d-block text-success"),
                        html.Small("Acceptable Options", className="text-muted")
                    ],
                    className="text-center"
                )
            ],
            className="d-flex justify-content-around border-top pt-3"
        )
        
        # Create Constraints Heatmap using Plotly
        # Collect all unique constraints across all options
        all_constraints = set()
        constraint_data = {}  # {option_name: {constraint_name: response_level}}
        
        for option_name in results.keys():
            constraint_data[option_name] = {}
            if option_name in filters:
                filter_data = filters[option_name]
                hard_constraints = filter_data.get('hard', [])
                soft_constraints = filter_data.get('soft', [])
                
                # Process hard constraints (convert pass/fail to response level)
                for hc in hard_constraints:
                    constraint_name = hc.get('name', 'Unknown')
                    all_constraints.add(constraint_name)
                    # Hard constraint: 0 if pass, 4 if fail
                    response_level = 0 if hc.get('pass', True) else 4
                    constraint_data[option_name][constraint_name] = response_level
                
                # Process soft constraints (use response level directly)
                for sc in soft_constraints:
                    constraint_name = sc.get('name', 'Unknown')
                    all_constraints.add(constraint_name)
                    response_level = sc.get('response', 0)
                    # If this constraint already exists (from hard), keep the higher severity
                    if constraint_name in constraint_data[option_name]:
                        constraint_data[option_name][constraint_name] = max(
                            constraint_data[option_name][constraint_name],
                            response_level
                        )
                    else:
                        constraint_data[option_name][constraint_name] = response_level
        
        # Sort constraints for consistent display
        sorted_constraints = sorted(all_constraints)
        option_names = list(results.keys())
        
        if sorted_constraints and constraint_data:
            # Prepare data for Plotly heatmap
            # Create matrix: rows = options, columns = constraints
            z_data = []
            text_data = []
            
            for option_name in option_names:
                row = []
                text_row = []
                for constraint_name in sorted_constraints:
                    response_level = constraint_data[option_name].get(constraint_name, 0)
                    row.append(response_level)
                    text_row.append(str(response_level))
                z_data.append(row)
                text_data.append(text_row)
            
            # Create Plotly heatmap
            heatmap_fig = go.Figure(data=go.Heatmap(
                z=z_data,
                x=sorted_constraints,
                y=option_names,
                text=text_data,
                texttemplate='%{text}',
                textfont={"size": 14, "color": "white"},
                colorscale=[
                    [0, "#28a745"],    # Dark Green for 0
                    [0.2, "#90ee90"],  # Light Green for 1
                    [0.4, "#ffc107"],  # Yellow/Gold for 2
                    [0.6, "#fd7e14"],  # Orange for 3
                    [1.0, "#dc3545"]   # Red for 4
                ],
                zmin=0,
                zmax=4,
                showscale=True,
                colorbar=dict(
                    title=dict(text="Response Level"),
                    tickmode="array",
                    tickvals=[0, 1, 2, 3, 4],
                    ticktext=["0", "1", "2", "3", "4"]
                ),
                hovertemplate='<b>%{y}</b><br>%{x}<br>Response Level: %{z}<extra></extra>'
            ))
            
            heatmap_fig.update_layout(
                title="Constraints Heatmap",
                xaxis_title="Constraints",
                yaxis_title="Options",
                template="plotly_white",
                height=400,
                autosize=False,
                margin=dict(l=100, r=50, t=50, b=50),
                xaxis=dict(side="bottom"),
                yaxis=dict(autorange="reversed")  # Reverse y-axis so first option is at top
            )
            
            # Create legend
            legend = html.Div(
                [
                    html.Div(
                        [
                            html.Span(
                                "",
                                style={
                                    "display": "inline-block",
                                    "width": "25px",
                                    "height": "25px",
                                    "backgroundColor": _get_response_color(0),
                                    "marginRight": "8px",
                                    "border": "1px solid #ccc",
                                    "verticalAlign": "middle"
                                }
                            ),
                            html.Small("0: Acceptable", className="me-4"),
                            html.Span(
                                "",
                                style={
                                    "display": "inline-block",
                                    "width": "25px",
                                    "height": "25px",
                                    "backgroundColor": _get_response_color(1),
                                    "marginRight": "8px",
                                    "border": "1px solid #ccc",
                                    "verticalAlign": "middle"
                                }
                            ),
                            html.Small("1: Cost Penalty", className="me-4"),
                            html.Span(
                                "",
                                style={
                                    "display": "inline-block",
                                    "width": "25px",
                                    "height": "25px",
                                    "backgroundColor": _get_response_color(2),
                                    "marginRight": "8px",
                                    "border": "1px solid #ccc",
                                    "verticalAlign": "middle"
                                }
                            ),
                            html.Small("2: Warning", className="me-4"),
                            html.Span(
                                "",
                                style={
                                    "display": "inline-block",
                                    "width": "25px",
                                    "height": "25px",
                                    "backgroundColor": _get_response_color(3),
                                    "marginRight": "8px",
                                    "border": "1px solid #ccc",
                                    "verticalAlign": "middle"
                                }
                            ),
                            html.Small("3: Mitigation", className="me-4"),
                            html.Span(
                                "",
                                style={
                                    "display": "inline-block",
                                    "width": "25px",
                                    "height": "25px",
                                    "backgroundColor": _get_response_color(4),
                                    "marginRight": "8px",
                                    "border": "1px solid #ccc",
                                    "verticalAlign": "middle"
                                }
                            ),
                            html.Small("4: Reject")
                        ],
                        className="d-flex align-items-center justify-content-center flex-wrap"
                    )
                ]
            )
        else:
            heatmap_fig = go.Figure()
            heatmap_fig.update_layout(
                title="Constraints Heatmap",
                template="plotly_white",
                height=400,
                xaxis_title="No constraints data available",
                yaxis_title=""
            )
            legend = html.Div()
        
        # Create Cost Comparison Chart
        # Get cost data from storage
        capital_cost_num = dash_storage.get_data("capital_cost_num")
        maintenance_cost_num = dash_storage.get_data("maintenance_cost_num")
        net_val_dict = dash_storage.get_data("net_val") or {}
        
        if capital_cost_num is not None and maintenance_cost_num is not None:
            # Map cost column names to option names
            cost_column_mapping = {
                "Spreading Pond Cost ($)": "Surface Recharge",
                "Injection Wells Cost ($)": "Injection Well",
                "Dry Wells Cost ($)": "Dry Well"
            }
            
            maintenance_column_mapping = {
                "Spreading Pond Maintenance Cost ($)": "Surface Recharge",
                "Injection Wells Maintenance Cost ($)": "Injection Well",
                "Dry Wells Maintenance Cost ($)": "Dry Well"
            }
            
            npv_column_mapping = {
                "Spreading Pond Net Present Value ($)": "Surface Recharge",
                "Injection Wells Net Present Value ($)": "Injection Well",
                "Dry Wells Net Present Value ($)": "Dry Well"
            }
            
            # Extract data for each option
            option_names = []
            capital_costs = []
            maintenance_costs = []
            npv_values = []
            
            for col_name, option_name in cost_column_mapping.items():
                if col_name in capital_cost_num.index:
                    option_names.append(option_name)
                    capital_costs.append(float(capital_cost_num[col_name]) if pd.notna(capital_cost_num[col_name]) else 0)
                    
                    # Get maintenance cost
                    maint_col = col_name.replace("Cost ($)", "Maintenance Cost ($)")
                    if maint_col in maintenance_cost_num.index:
                        maintenance_costs.append(float(maintenance_cost_num[maint_col]) if pd.notna(maintenance_cost_num[maint_col]) else 0)
                    else:
                        maintenance_costs.append(0)
                    
                    # Get NPV
                    npv_col = col_name.replace("Cost ($)", "Net Present Value ($)")
                    if npv_col in net_val_dict:
                        npv_values.append(float(net_val_dict[npv_col]) if pd.notna(net_val_dict[npv_col]) else 0)
                    else:
                        npv_values.append(0)
            
            if option_names:
                # Create three separate bar charts
                
                # Capital Cost Chart
                capital_fig = go.Figure()
                capital_fig.add_trace(go.Bar(
                    x=option_names,
                    y=capital_costs,
                    marker_color="#007bff",
                    text=[f"${c/1e6:.2f}M" if c >= 1e6 else f"${c/1e3:.0f}K" for c in capital_costs],
                    textposition="auto",
                    name="Capital Cost"
                ))
                capital_fig.update_layout(
                    title="Capital Cost",
                    xaxis_title="Options",
                    yaxis_title="Cost ($)",
                    template="plotly_white",
                    height=350,
                    autosize=False,
                    margin=dict(l=50, r=20, t=50, b=50),
                    showlegend=False,
                    yaxis=dict(tickformat="$,.0f")
                )
                
                # Maintenance Cost Chart
                maintenance_fig = go.Figure()
                maintenance_fig.add_trace(go.Bar(
                    x=option_names,
                    y=maintenance_costs,
                    marker_color="#28a745",
                    text=[f"${c/1e6:.2f}M" if c >= 1e6 else f"${c/1e3:.0f}K" for c in maintenance_costs],
                    textposition="auto",
                    name="Annual Maintenance Cost"
                ))
                maintenance_fig.update_layout(
                    title="Annual Maintenance Cost",
                    xaxis_title="Options",
                    yaxis_title="Cost ($)",
                    template="plotly_white",
                    height=350,
                    autosize=False,
                    margin=dict(l=50, r=20, t=50, b=50),
                    showlegend=False,
                    yaxis=dict(tickformat="$,.0f")
                )
                
                # NPV Chart
                npv_fig = go.Figure()
                npv_fig.add_trace(go.Bar(
                    x=option_names,
                    y=npv_values,
                    marker_color="#ffc107",
                    text=[f"${c/1e6:.2f}M" if c >= 1e6 else f"${c/1e3:.0f}K" for c in npv_values],
                    textposition="auto",
                    name="NPV (20 years)"
                ))
                npv_fig.update_layout(
                    title="Net Present Value (20 years)",
                    xaxis_title="Options",
                    yaxis_title="Cost ($)",
                    template="plotly_white",
                    height=350,
                    autosize=False,
                    margin=dict(l=50, r=20, t=50, b=50),
                    showlegend=False,
                    yaxis=dict(tickformat="$,.0f")
                )
            else:
                capital_fig = go.Figure()
                capital_fig.update_layout(
                    title="Capital Cost",
                    template="plotly_white",
                    height=350,
                    xaxis_title="No cost data available",
                    yaxis_title=""
                )
                maintenance_fig = go.Figure()
                maintenance_fig.update_layout(
                    title="Annual Maintenance Cost",
                    template="plotly_white",
                    height=350,
                    xaxis_title="No cost data available",
                    yaxis_title=""
                )
                npv_fig = go.Figure()
                npv_fig.update_layout(
                    title="Net Present Value (20 years)",
                    template="plotly_white",
                    height=350,
                    xaxis_title="No cost data available",
                    yaxis_title=""
                )
        else:
            capital_fig = go.Figure()
            capital_fig.update_layout(
                title="Capital Cost",
                template="plotly_white",
                height=350,
                xaxis_title="No cost data available. Please run cost analysis first.",
                yaxis_title=""
            )
            maintenance_fig = go.Figure()
            maintenance_fig.update_layout(
                title="Annual Maintenance Cost",
                template="plotly_white",
                height=350,
                xaxis_title="No cost data available. Please run cost analysis first.",
                yaxis_title=""
            )
            npv_fig = go.Figure()
            npv_fig.update_layout(
                title="Net Present Value (20 years)",
                template="plotly_white",
                height=350,
                xaxis_title="No cost data available. Please run cost analysis first.",
                yaxis_title=""
            )
        
        return html.Div(executive_summary), fig, stats, heatmap_fig, legend, capital_fig, maintenance_fig, npv_fig


def _get_response_color(level):
    """Get color for response level (0-4)."""
    color_map = {
        0: "#28a745",  # Dark Green
        1: "#90ee90",  # Light Green
        2: "#ffc107",  # Yellow/Gold
        3: "#fd7e14",  # Orange
        4: "#dc3545"   # Red
    }
    return color_map.get(level, "#ffffff")

