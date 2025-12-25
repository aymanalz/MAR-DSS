"""
Decision Interpretation tab content for MAR DSS dashboard.
"""

import plotly.graph_objects as go
from dash import dcc, html
import dash_bootstrap_components as dbc
import mar_dss.app.utils.data_storage as dash_storage


def _get_status_color(status):
    """Get color for status."""
    status_colors = {
        "Recommended": "success",
        "Recommended with Warnings": "warning",
        "Conditionally Recommended": "info",
        "Rejected": "danger",
    }
    return status_colors.get(status, "secondary")


def _format_cost(cost):
    """Format cost for display."""
    if isinstance(cost, list):
        if len(cost) == 0:
            return "To be calculated"
        return f"{len(cost)} cost items"
    elif isinstance(cost, (int, float)):
        return f"${cost:,.0f}"
    return str(cost)


def _create_option_interpretation(option_name, result, filters=None):
    """Create detailed interpretation content for a selected option."""
    status = result.get("status", "Unknown")
    benefit_score = result.get("benefit_score", 0.0) * 100
    cost = result.get("cost", [])
    warnings = result.get("warnings", [])
    mitigations = result.get("mitigations", [])
    
    status_badge = dbc.Badge(
        status,
        color=_get_status_color(status),
        className="me-2 mb-3",
    )
    
    # Get filter details if available
    hard_constraints = []
    soft_constraints = []
    benefits_list = []
    if filters and option_name in filters:
        filter_data = filters[option_name]
        hard_constraints = filter_data.get('hard', [])
        soft_constraints = filter_data.get('soft', [])
        benefits_list = filter_data.get('benefits', [])
    
    # Build interpretation content
    content = [
        html.H4(f"{option_name}", className="mb-3"),
        html.Div([status_badge], className="mb-3"),
        
        # Summary metrics
        dbc.Row(
            [
                dbc.Col(
                    dbc.Card(
                        [
                            dbc.CardBody(
                                [
                                    html.H5(f"{benefit_score:.1f}%", className="text-primary"),
                                    html.P("Benefit Score", className="mb-0 text-muted"),
                                ]
                            )
                        ],
                        className="text-center",
                    ),
                    width=4,
                ),
                dbc.Col(
                    dbc.Card(
                        [
                            dbc.CardBody(
                                [
                                    html.H5(f"{len(warnings)}", className="text-warning"),
                                    html.P("Warnings", className="mb-0 text-muted"),
                                ]
                            )
                        ],
                        className="text-center",
                    ),
                    width=4,
                ),
                dbc.Col(
                    dbc.Card(
                        [
                            dbc.CardBody(
                                [
                                    html.H5(f"{len(mitigations)}", className="text-info"),
                                    html.P("Mitigations", className="mb-0 text-muted"),
                                ]
                            )
                        ],
                        className="text-center",
                    ),
                    width=4,
                ),
            ],
            className="mb-4",
        ),
        
        # Status interpretation
        html.H5("Status Interpretation", className="mt-4"),
        html.P(
            _get_status_interpretation(status, warnings, mitigations),
            className="mb-3",
        ),
    ]
    
    # Cost information
    content.append(html.H5("Cost Information", className="mt-4"))
    if isinstance(cost, list):
        if len(cost) > 0:
            cost_items = html.Ul(
                [html.Li(item if isinstance(item, str) else str(item)) for item in cost],
                className="mb-3",
            )
            content.append(cost_items)
        else:
            content.append(html.P("Cost items to be calculated.", className="text-muted mb-3"))
    else:
        content.append(html.P(f"Total Cost: {_format_cost(cost)}", className="mb-3"))
    
    # Warnings
    if warnings:
        content.append(html.H5("Warnings", className="mt-4"))
        warning_items = html.Ul(
            [html.Li(warning, className="text-warning") for warning in warnings],
            className="mb-3",
        )
        content.append(warning_items)
    
    # Mitigations
    if mitigations:
        content.append(html.H5("Required Mitigations", className="mt-4"))
        mitigation_items = html.Ul(
            [html.Li(mitigation, className="text-info") for mitigation in mitigations],
            className="mb-3",
        )
        content.append(mitigation_items)
    
    # Soft constraints details
    if soft_constraints:
        content.append(html.H5("Soft Constraints Evaluation", className="mt-4"))
        constraint_rows = []
        for sc in soft_constraints:
            constraint_name = sc.get("name", "Unknown")
            response = sc.get("response", 0)
            penalty = sc.get("penalty", [])
            is_hard = sc.get("hard", False)
            
            response_labels = {
                0: "Acceptable",
                1: "Acceptable with additional Cost",
                2: "Warning",
                3: "Mitigation",
                4: "Reject",
            }
            response_label = response_labels.get(response, "Unknown")
            
            constraint_rows.append(
                html.Tr(
                    [
                        html.Td(constraint_name),
                        html.Td(response_label),
                        html.Td("Yes" if is_hard else "No"),
                        html.Td(
                            html.Ul([html.Li(p if isinstance(p, str) else str(p)) for p in penalty])
                            if isinstance(penalty, list) and len(penalty) > 0
                            else "None"
                        ),
                    ]
                )
            )
        
        content.append(
            dbc.Table(
                [
                    html.Thead(
                        html.Tr(
                            [
                                html.Th("Constraint"),
                                html.Th("Response Level"),
                                html.Th("Hard Constraint"),
                                html.Th("Penalty/Cost"),
                            ]
                        )
                    ),
                    html.Tbody(constraint_rows),
                ],
                bordered=True,
                hover=True,
                responsive=True,
                className="mb-3",
            )
        )
    
    # Benefits breakdown
    if benefits_list:
        content.append(html.H5("Benefits Breakdown", className="mt-4"))
        benefit_rows = []
        for benefit in benefits_list:
            benefit_name = benefit.get("name", "Unknown")
            value = benefit.get("value", 0.0) * 100
            weight = benefit.get("weight", 0.0) * 100
            contribution = value * weight / 100 if weight > 0 else 0
            
            benefit_rows.append(
                html.Tr(
                    [
                        html.Td(benefit_name),
                        html.Td(f"{value:.1f}%"),
                        html.Td(f"{weight:.1f}%"),
                        html.Td(f"{contribution:.2f}%"),
                    ]
                )
            )
        
        content.append(
            dbc.Table(
                [
                    html.Thead(
                        html.Tr(
                            [
                                html.Th("Benefit Metric"),
                                html.Th("Value"),
                                html.Th("Weight"),
                                html.Th("Contribution"),
                            ]
                        )
                    ),
                    html.Tbody(benefit_rows),
                ],
                bordered=True,
                hover=True,
                responsive=True,
                className="mb-3",
            )
        )
    
    return html.Div(content)


def _get_status_interpretation(status, warnings, mitigations):
    """Get interpretation text for a status."""
    if status == "Recommended":
        return "This option is fully recommended for implementation. No warnings or mitigations are required. It meets all hard constraints and has acceptable soft constraint responses."
    elif status == "Recommended with Warnings":
        return f"This option is recommended but has {len(warnings)} warning(s) that should be monitored. The warnings indicate potential concerns that may require attention during implementation or operation."
    elif status == "Conditionally Recommended":
        return f"This option is conditionally recommended and requires {len(mitigations)} mitigation measure(s) before proceeding. These mitigations must be addressed to ensure successful implementation."
    elif status == "Rejected":
        return "This option has been rejected based on the evaluation. It either fails hard constraints or has critical soft constraint violations that cannot be mitigated."
    else:
        return "Status interpretation not available."


def create_decision_interpretation_content():
    """Create content for Decision Interpretation sidebar tab."""
    # Get DSS results from storage
    dss_results = dash_storage.get_data("dss_results")
    
    if dss_results is None or not hasattr(dss_results, 'results') or not dss_results.results:
        return html.Div(
            [
                html.H3("Decision Interpretation"),
                dbc.Alert(
                    "No evaluation results available. Please run the feasibility analysis first.",
                    color="info",
                    className="mt-3",
                ),
            ]
        )
    
    results = dss_results.results
    filters = getattr(dss_results, 'filters', {})
    
    # Prepare data for visualization
    option_names = list(results.keys())
    statuses = [result.get("status", "Unknown") for result in results.values()]
    benefit_scores = [result.get("benefit_score", 0.0) * 100 for result in results.values()]
    
    # Status distribution
    status_counts = {}
    for status in statuses:
        status_counts[status] = status_counts.get(status, 0) + 1
    
    # Create status distribution chart
    status_fig = go.Figure()
    status_fig.add_trace(
        go.Bar(
            x=list(status_counts.keys()),
            y=list(status_counts.values()),
            marker_color=["#28a745", "#ffc107", "#17a2b8", "#dc3545"],  # green, yellow, blue, red
            text=list(status_counts.values()),
            textposition="auto",
        )
    )
    status_fig.update_layout(
        title="Decision Status Distribution",
        xaxis_title="Status",
        yaxis_title="Number of Options",
        template="plotly_white",
        height=300,
    )
    
    # Create benefit score comparison chart
    benefit_fig = go.Figure()
    colors = []
    for status in statuses:
        if status == "Recommended":
            colors.append("#28a745")
        elif status == "Recommended with Warnings":
            colors.append("#ffc107")
        elif status == "Conditionally Recommended":
            colors.append("#17a2b8")
        else:
            colors.append("#dc3545")
    
    benefit_fig.add_trace(
        go.Bar(
            x=option_names,
            y=benefit_scores,
            marker_color=colors,
            text=[f"{score:.1f}%" for score in benefit_scores],
            textposition="auto",
        )
    )
    benefit_fig.update_layout(
        title="Benefit Score by MAR Option",
        xaxis_title="MAR Technology Option",
        yaxis_title="Benefit Score (%)",
        template="plotly_white",
        height=400,
        xaxis_tickangle=-45,
    )
    
    # Create detailed results table
    table_rows = []
    for option_name, result in results.items():
        status = result.get("status", "Unknown")
        benefit_score = result.get("benefit_score", 0.0) * 100
        cost = result.get("cost", [])
        warnings = result.get("warnings", [])
        mitigations = result.get("mitigations", [])
        
        status_badge = dbc.Badge(
            status,
            color=_get_status_color(status),
            className="me-2",
        )
        
        table_rows.append(
            html.Tr(
                [
                    html.Td(option_name),
                    html.Td(status_badge),
                    html.Td(f"{benefit_score:.1f}%"),
                    html.Td(_format_cost(cost)),
                    html.Td(len(warnings)),
                    html.Td(len(mitigations)),
                ]
            )
        )
    
    # Summary insights
    recommended_count = sum(1 for s in statuses if s == "Recommended")
    warnings_count = sum(1 for s in statuses if s == "Recommended with Warnings")
    conditional_count = sum(1 for s in statuses if s == "Conditionally Recommended")
    rejected_count = sum(1 for s in statuses if s == "Rejected")
    
    total_warnings = sum(len(r.get("warnings", [])) for r in results.values())
    total_mitigations = sum(len(r.get("mitigations", [])) for r in results.values())
    
    avg_benefit = sum(benefit_scores) / len(benefit_scores) if benefit_scores else 0
    
    option_names = list(results.keys())
    
    return html.Div(
        [
            html.H3("Decision Interpretation"),
            html.P(
                "Comprehensive analysis and interpretation of MAR technology evaluation results.",
                className="text-muted",
            ),
            html.Hr(),
            
            # Dropdown for option selection
            html.Div(
                [
                    html.Label("Select MAR Technology Option:", className="form-label fw-bold mb-2"),
                    dcc.Dropdown(
                        id="decision-interpretation-option-selector",
                        options=[{"label": name, "value": name} for name in option_names],
                        value=option_names[0] if option_names else None,
                        placeholder="Select an option to view detailed interpretation...",
                        className="mb-4",
                    ),
                ],
                className="mb-4",
            ),
            
            # Interpretation content area
            html.Div(id="decision-interpretation-details", className="mb-4"),
            
            html.Hr(),
            
            # Summary Cards
            dbc.Row(
                [
                    dbc.Col(
                        dbc.Card(
                            [
                                dbc.CardBody(
                                    [
                                        html.H4(f"{recommended_count}", className="text-success"),
                                        html.P("Recommended", className="mb-0"),
                                    ]
                                )
                            ],
                            className="text-center",
                        ),
                        width=3,
                    ),
                    dbc.Col(
                        dbc.Card(
                            [
                                dbc.CardBody(
                                    [
                                        html.H4(f"{warnings_count}", className="text-warning"),
                                        html.P("With Warnings", className="mb-0"),
                                    ]
                                )
                            ],
                            className="text-center",
                        ),
                        width=3,
                    ),
                    dbc.Col(
                        dbc.Card(
                            [
                                dbc.CardBody(
                                    [
                                        html.H4(f"{conditional_count}", className="text-info"),
                                        html.P("Conditionally Recommended", className="mb-0"),
                                    ]
                                )
                            ],
                            className="text-center",
                        ),
                        width=3,
                    ),
                    dbc.Col(
                        dbc.Card(
                            [
                                dbc.CardBody(
                                    [
                                        html.H4(f"{rejected_count}", className="text-danger"),
                                        html.P("Rejected", className="mb-0"),
                                    ]
                                )
                            ],
                            className="text-center",
                        ),
                        width=3,
                    ),
                ],
                className="mb-4",
            ),
            
            # Charts
            dbc.Row(
                [
                    dbc.Col(dcc.Graph(figure=status_fig), width=6),
                    dbc.Col(dcc.Graph(figure=benefit_fig), width=6),
                ],
                className="mb-4",
            ),
            
            # Detailed Results Table
            html.H5("Detailed Results", className="mt-4"),
            dbc.Table(
                [
                    html.Thead(
                        html.Tr(
                            [
                                html.Th("Option"),
                                html.Th("Status"),
                                html.Th("Benefit Score"),
                                html.Th("Cost"),
                                html.Th("Warnings"),
                                html.Th("Mitigations"),
                            ]
                        )
                    ),
                    html.Tbody(table_rows),
                ],
                bordered=True,
                hover=True,
                responsive=True,
                className="mb-4",
            ),
            
            # Key Insights
            html.H5("Key Insights", className="mt-4"),
            html.Ul(
                [
                    html.Li(f"Average benefit score across all options: {avg_benefit:.1f}%"),
                    html.Li(f"Total warnings identified: {total_warnings}"),
                    html.Li(f"Total mitigations required: {total_mitigations}"),
                    html.Li(
                        f"Best performing option: {max(results.items(), key=lambda x: x[1].get('benefit_score', 0))[0]} "
                        f"({max(benefit_scores):.1f}% benefit score)"
                        if benefit_scores else "N/A"
                    ),
                ],
                className="mb-4",
            ),
            
            # Recommendations
            html.H5("Recommendations", className="mt-4"),
            html.Div(
                [
                    html.P(
                        "Based on the evaluation results:",
                        className="mb-2",
                    ),
                    html.Ul(
                        [
                            html.Li(
                                "Review options with 'Recommended' status for immediate implementation consideration."
                            ),
                            html.Li(
                                "Options with warnings may require additional monitoring or minor adjustments."
                            ),
                            html.Li(
                                "Conditionally recommended options need mitigation measures before proceeding."
                            ),
                            html.Li(
                                "Rejected options should be reconsidered only if site conditions change significantly."
                            ),
                        ]
                    ),
                ]
            ),
        ]
    )


