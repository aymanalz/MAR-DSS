"""
Callbacks for the Feasibilities tab.
"""

import dash
from dash import Input, Output, html, dcc
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
import pandas as pd
import mar_dss.app.utils.data_storage as dash_storage
import logging

logger = logging.getLogger(__name__)


def _ensure_dss_results_available(top_tab):
    """Ensure DSS results are available, running analysis if needed."""
    if top_tab == "analysis":
        logger.debug("Analysis tab accessed - ensuring feasibility analysis has run")
        try:
            from mar_dss.app.callbacks.analysis_callbacks import run_feasibility_analysis
            run_feasibility_analysis()
            logger.debug("Feasibility analysis completed")
        except Exception as e:
            logger.error(f"Error running feasibility analysis: {e}", exc_info=True)
    
    # Get DSS results from storage
    dss_results = dash_storage.get_data("dss_results")
    
    # If no DSS results exist after running analysis, try running integrated analysis directly
    if dss_results is None or not hasattr(dss_results, 'results') or not dss_results.results:
        logger.info("No DSS results found after feasibility analysis. Running integrated analysis directly...")
        try:
            from mar_dss.app.callbacks.analysis_callbacks import run_integrated_analysis
            dss_results, _ = run_integrated_analysis()
            logger.info("Integrated analysis completed successfully")
        except Exception as e:
            logger.error(f"Error running integrated analysis: {e}", exc_info=True)
    
    return dss_results


def _get_empty_dashboard_content():
    """Return empty dashboard content when no DSS results are available."""
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


def _categorize_options(results, filters):
    """Categorize options into recommended, conditional, and rejected based on DSS results."""
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
        cost_mapping = dash_storage.get_data("cost_mapping")
        if cost_mapping and option_name in cost_mapping:
            cost_data = cost_mapping[option_name]
            if isinstance(cost_data, dict):
                cost_val = cost_data.get("capital", 0)
            else:
                cost_val = float(cost_data) if cost_data else 0
        elif isinstance(cost, list):
            if len(cost) > 0:
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
    
    return {
        "recommended": recommended,
        "conditional": conditional,
        "rejected": rejected,
        "stats": {
            "total_options": total_options,
            "hard_constraint_fails": hard_constraint_fails,
            "soft_rule_rejects": soft_rule_rejects,
            "after_hard_constraints": after_hard_constraints,
            "after_soft_rules": after_soft_rules,
            "recommended_count": recommended_count
        }
    }


def _build_executive_summary(categorized_data):
    """Build the executive summary HTML content."""
    recommended = categorized_data["recommended"]
    conditional = categorized_data["conditional"]
    rejected = categorized_data["rejected"]
    
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
    
    return executive_summary


def _create_decision_funnel_chart(stats):
    """Create the decision funnel chart."""
    funnel_categories = ["All Options", "After Hard Constraints", "After Soft Rules", "Recommended"]
    funnel_values = [
        stats["total_options"],
        stats["after_hard_constraints"],
        stats["after_soft_rules"],
        stats["recommended_count"]
    ]
    
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
        autosize=False,
        showlegend=False,
        margin=dict(l=150, r=50, t=50, b=50),
        uirevision='constant'
    )
    
    return fig


def _create_funnel_stats(stats):
    """Create summary statistics for the decision funnel."""
    return html.Div(
        [
            html.Div(
                [
                    html.Strong(f"{stats['total_options']}", className="d-block"),
                    html.Small("Options Evaluated", className="text-muted")
                ],
                className="text-center me-3"
            ),
            html.Div(
                [
                    html.Strong(f"{stats['hard_constraint_fails']}", className="d-block text-danger"),
                    html.Small("Hard Constraint Fail", className="text-muted")
                ],
                className="text-center me-3"
            ),
            html.Div(
                [
                    html.Strong(f"{stats['soft_rule_rejects']}", className="d-block text-danger"),
                    html.Small("Soft Rule Reject", className="text-muted")
                ],
                className="text-center me-3"
            ),
            html.Div(
                [
                    html.Strong(f"{stats['recommended_count']}", className="d-block text-success"),
                    html.Small("Acceptable Options", className="text-muted")
                ],
                className="text-center"
            )
        ],
        className="d-flex justify-content-around border-top pt-3"
    )


def _prepare_constraints_data(results, filters):
    """Prepare constraint data for heatmap."""
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
    
    return sorted(all_constraints), constraint_data


def _create_constraints_heatmap(results, filters):
    """Create the constraints heatmap chart and legend."""
    sorted_constraints, constraint_data = _prepare_constraints_data(results, filters)
    option_names = list(results.keys())
    
    if not sorted_constraints or not constraint_data:
        heatmap_fig = go.Figure()
        heatmap_fig.update_layout(
            title="Constraints Heatmap",
            template="plotly_white",
            height=400,
            xaxis_title="No constraints data available",
            yaxis_title=""
        )
        return heatmap_fig, html.Div()
    
    # Prepare data for Plotly heatmap
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
        yaxis=dict(autorange="reversed")
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
    
    return heatmap_fig, legend


def _extract_cost_data():
    """Extract cost data from storage and return mapped values."""
    capital_cost_num = dash_storage.get_data("capital_cost_num")
    maintenance_cost_num = dash_storage.get_data("maintenance_cost_num")
    net_val_dict = dash_storage.get_data("net_val") or {}
    
    if capital_cost_num is None or maintenance_cost_num is None:
        return None, None, None, None
    
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
    
    return option_names, capital_costs, maintenance_costs, npv_values


def _create_cost_chart(option_names, values, title, color):
    """Create a single cost chart (capital, maintenance, or NPV)."""
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=option_names,
        y=values,
        marker_color=color,
        text=[f"${c/1e6:.2f}M" if c >= 1e6 else f"${c/1e3:.0f}K" for c in values],
        textposition="auto",
        name=title
    ))
    fig.update_layout(
        title=title,
        xaxis_title="Options",
        yaxis_title="Cost ($)",
        template="plotly_white",
        height=350,
        autosize=False,
        margin=dict(l=50, r=20, t=50, b=50),
        showlegend=False,
        yaxis=dict(tickformat="$,.0f")
    )
    return fig


def _create_empty_cost_charts():
    """Create empty cost charts when no data is available."""
    empty_capital_fig = go.Figure()
    empty_capital_fig.update_layout(
        title="Capital Cost",
        template="plotly_white",
        height=350,
        xaxis_title="No cost data available. Please run cost analysis first.",
        yaxis_title=""
    )
    
    empty_maintenance_fig = go.Figure()
    empty_maintenance_fig.update_layout(
        title="Annual Maintenance Cost",
        template="plotly_white",
        height=350,
        xaxis_title="No cost data available. Please run cost analysis first.",
        yaxis_title=""
    )
    
    empty_npv_fig = go.Figure()
    empty_npv_fig.update_layout(
        title="Net Present Value (20 years)",
        template="plotly_white",
        height=350,
        xaxis_title="No cost data available. Please run cost analysis first.",
        yaxis_title=""
    )
    
    return empty_capital_fig, empty_maintenance_fig, empty_npv_fig


def _create_cost_comparison_charts():
    """Create the three cost comparison charts."""
    option_names, capital_costs, maintenance_costs, npv_values = _extract_cost_data()
    
    if not option_names:
        return _create_empty_cost_charts()
    
    capital_fig = _create_cost_chart(option_names, capital_costs, "Capital Cost", "#007bff")
    maintenance_fig = _create_cost_chart(option_names, maintenance_costs, "Annual Maintenance Cost", "#28a745")
    npv_fig = _create_cost_chart(option_names, npv_values, "Net Present Value (20 years)", "#ffc107")
    
    return capital_fig, maintenance_fig, npv_fig


def setup_feasibilities_callbacks(app):
    """Set up all callbacks for the Feasibilities tab."""
    
    @app.callback(
        [Output("executive-summary-content", "children"),
         Output("decision-funnel-chart", "figure"),
         Output("decision-funnel-stats", "children"),
         Output("constraints-heatmap-chart", "figure"),
         Output("constraints-heatmap-legend", "children"),
         Output("capital-cost-chart", "figure"),
         Output("maintenance-cost-chart", "figure"),
         Output("npv-cost-chart", "figure")],
        [Input("top-tabs", "active_tab"),
         Input("analysis-tabs", "active_tab"),
         Input("knowledge-graph-store", "data")],
        prevent_initial_call=False
    )
    def update_feasibilities_dashboard(top_tab, active_tab, graph_store):
        """Update Executive Summary and Decision Funnel based on DSS results."""
        # Update when Analysis tab is accessed OR when Feasibilities sub-tab is selected
        # This ensures data loads immediately when Analysis tab opens
        if top_tab != "analysis" and active_tab != "analysis-feasibilities":
            return dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update
        
        # Ensure DSS results are available
        dss_results = _ensure_dss_results_available(top_tab)
        
        # Check if results are available
        if dss_results is None or not hasattr(dss_results, 'results') or not dss_results.results:
            return _get_empty_dashboard_content()
        
        # Extract results and filters
        results = dss_results.results
        filters = getattr(dss_results, 'filters', {})
        
        # Categorize options
        categorized_data = _categorize_options(results, filters)
        
        # Build components
        executive_summary = _build_executive_summary(categorized_data)
        funnel_fig = _create_decision_funnel_chart(categorized_data["stats"])
        funnel_stats = _create_funnel_stats(categorized_data["stats"])
        heatmap_fig, heatmap_legend = _create_constraints_heatmap(results, filters)
        capital_fig, maintenance_fig, npv_fig = _create_cost_comparison_charts()
        
        return (
            html.Div(executive_summary),
            funnel_fig,
            funnel_stats,
            heatmap_fig,
            heatmap_legend,
            capital_fig,
            maintenance_fig,
            npv_fig
        )


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

