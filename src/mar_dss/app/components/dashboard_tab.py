"""
Dashboard tab content for MAR DSS dashboard.
"""

import dash_bootstrap_components as dbc
from dash import html, dcc


def create_dashboard_content():
    """Create content for Feasible MAR Technologies tab."""
    return html.Div(
        [
            html.H3("Feasible MAR Technologies", className="mb-4", id="feasibility-summary-title"),
            
            # Key Metrics Summary
            dbc.Row(
                [
                    dbc.Col(
                        dbc.Alert(
                            [
                                html.H6(id="overall-feasibility-score", children="Overall Feasibility Score: 0%", className="alert-heading mb-0"),
                                html.Small("Based on selected technologies and site conditions", className="text-muted")
                            ],
                            color="info",
                            className="text-center"
                        ),
                        width=6,
                        className="mb-4"
                    ),
                    dbc.Col(
                        dbc.Alert(
                            [
                                html.H6(id="total-project-cost", children="Total Project Cost: $0 - $0", className="alert-heading mb-0"),
                                html.Small("Estimated capital investment range", className="text-muted")
                            ],
                            color="warning",
                            className="text-center"
                        ),
                        width=6,
                        className="mb-4"
                    )
                ]
            ),
            
            # Technology Selection Section - Three Cards Side by Side
            dbc.Row(
                [
                    # Feasible Options Section
                    dbc.Col(
                        dbc.Card(
                            [
                                dbc.CardHeader(
                                    html.H5("✅ Feasible MAR Technologies", className="mb-0 text-success")
                                ),
                    dbc.CardBody(
                        [
                                        html.Div(id="feasible-technologies-container"),
                                        html.Small("Select one feasible technology for your project", className="text-muted"),
                                        html.Div(id="technology-selection-feedback", className="mt-3")
                                    ],
                                    id="feasible-technologies-card-body"
                                )
                            ],
                            className="h-100"
                        ),
                        width=4,
                        className="mb-4"
                    ),
                    
                    # Conditionally Feasible Options Section
                    dbc.Col(
                        dbc.Card(
                            [
                                dbc.CardHeader(
                                    html.H5("⚠️ Conditionally Feasible MAR Technologies", className="mb-0 text-warning")
                                ),
                                dbc.CardBody(
                                    [
                                        html.Div(id="conditionally-feasible-technologies-container"),
                                        html.Small("These technologies may be feasible with certain conditions or modifications", className="text-muted")
                                    ],
                                    id="conditionally-feasible-technologies-card-body"
                                )
                            ],
                            className="h-100"
                        ),
                        width=4,
                        className="mb-4"
                    ),
                    
                    # Infeasible Options Section
                    dbc.Col(
                        dbc.Card(
                            [
                                dbc.CardHeader(
                                    html.H5("❌ Infeasible MAR Technologies", className="mb-0 text-danger")
                                ),
                                dbc.CardBody(
                                    [
                                        html.Div(id="infeasible-technologies-container"),
                                        html.Small("These technologies are considered infeasible for this project", className="text-muted")
                                    ],
                                    id="infeasible-technologies-card-body"
                                )
                            ],
                            className="h-100"
                        ),
                        width=4,
                        className="mb-4"
                    )
                ]
            ),
            
            # Technology Analysis Tabs
            dbc.Tabs(
                [
                    dbc.Tab(
                        label="Feasibility Metrics",
                        tab_id="feasibility-metrics",
                        children=[
                            # Feasibility Metrics Section
                            dbc.Card(
                                [
                                    dbc.CardHeader(
                                        html.H5("📊 Feasibility Metrics", className="mb-0 text-primary")
                                    ),
                                    dbc.CardBody(
                                        [
                                            dbc.Row(
                                                [
                                                    dbc.Col(
                                                        [
                                                            html.H6("Physical Feasibility", className="text-muted"),
                                                            dbc.Progress(
                                                                id="feasibility-metric-physical",
                                                                value=0,
                                                                color="success",
                                                                className="mb-2"
                                                            ),
                                                            html.Small("Geological and hydrological suitability", className="text-muted")
                                                        ],
                                                        width=6,
                                                        className="mb-3"
                                                    ),
                                                    dbc.Col(
                                                        [
                                                            html.H6("Environmental Impact", className="text-muted"),
                                                            dbc.Progress(
                                                                id="feasibility-metric-environmental",
                                                                value=0,
                                                                color="warning",
                                                                className="mb-2"
                                                            ),
                                                            html.Small("Ecological effects and water quality", className="text-muted")
                                                        ],
                                                        width=6,
                                                        className="mb-3"
                                                    )
                                                ]
                                            ),
                                            dbc.Row(
                                                [
                                                    dbc.Col(
                                                        [
                                                            html.H6("Legal Considerations", className="text-muted"),
                                                            dbc.Progress(
                                                                id="feasibility-metric-legal",
                                                                value=0,
                                                                color="info",
                                                                className="mb-2"
                                                            ),
                                                            html.Small("Regulatory compliance and water rights", className="text-muted")
                                                        ],
                                                        width=6,
                                                        className="mb-3"
                                                    ),
                                                    dbc.Col(
                                                        [
                                                            html.H6("Cost Analysis", className="text-muted"),
                                                            dbc.Progress(
                                                                id="feasibility-metric-cost",
                                                                value=0,
                                                                color="danger",
                                                                className="mb-2"
                                                            ),
                                                            html.Small("Financial investment and ROI", className="text-muted")
                                                        ],
                                                        width=6,
                                                        className="mb-3"
                                                    )
                                                ]
                                            ),
                                            dbc.Row(
                                                [
                                                    dbc.Col(
                                                        [
                                                            html.H6("Technical Complexity", className="text-muted"),
                                                            dbc.Progress(
                                                                id="feasibility-metric-technical",
                                                                value=0,
                                                                color="secondary",
                                                                className="mb-2"
                                                            ),
                                                            html.Small("Implementation and maintenance requirements", className="text-muted")
                                                        ],
                                                        width=6,
                                                        className="mb-3"
                                                    ),
                                                    dbc.Col(
                                                        [
                                                            html.H6("Social Acceptance", className="text-muted"),
                                                            dbc.Progress(
                                                                id="feasibility-metric-social",
                                                                value=0,
                                                                color="primary",
                                                                className="mb-2"
                                                            ),
                                                            html.Small("Community support and stakeholder buy-in", className="text-muted")
                                                        ],
                                                        width=6,
                                                        className="mb-3"
                                                    )
                                                ]
                                            ),
                                            
                                            # Summary Section
                                            dbc.Alert(
                                                [
                                                    html.H6(id="feasibility-metrics-overall-score", children="Overall Feasibility Score: 0%", className="alert-heading"),
                                                    html.P(id="feasibility-metrics-summary-text", children="Select a technology to view feasibility metrics.", className="mb-0")
                                                ],
                                                color="info",
                                                className="mt-3"
                                            )
                                        ]
                                    )
                                ],
                                className="mb-4"
                            )
                        ],
                        label_style={
                            "color": "#ffffff", 
                            "fontWeight": "bold",
                            "backgroundColor": "#28a745",
                            "border": "1px solid #28a745"
                        },
                        active_label_style={
                            "color": "#ffffff", 
                            "backgroundColor": "#1e7e34",
                            "border": "1px solid #1e7e34"
                        }
                    ),
                    dbc.Tab(
                        label="Hydrogeological Feasibility",
                        tab_id="hydrogeological-feasibility",
                        children=[
                            # Hydrogeological Feasibility Section
                            dbc.Card(
                                [
                                    dbc.CardHeader(
                                        html.H5("🌊 Hydrogeological Feasibility", className="mb-0 text-warning")
                                    ),
                                    dbc.CardBody(
                                        [
                                            dbc.Row(
                                                [
                                                    dbc.Col(
                                                        [
                                                            html.H6("Initial Investment", className="text-muted"),
                                                            dbc.Progress(
                                                                value=65,
                                                                color="danger",
                                                                className="mb-2"
                                                            ),
                                                            html.Small("Capital costs for infrastructure", className="text-muted"),
                                                            html.P("$2.5M - $4.2M", className="fw-bold text-danger")
                                                        ],
                                                        width=6,
                                                        className="mb-3"
                                                    ),
                                                    dbc.Col(
                                                        [
                                                            html.H6("Operating Costs", className="text-muted"),
                                                            dbc.Progress(
                                                                value=40,
                                                                color="warning",
                                                                className="mb-2"
                                                            ),
                                                            html.Small("Annual maintenance and operations", className="text-muted"),
                                                            html.P("$150K - $300K/year", className="fw-bold text-warning")
                                                        ],
                                                        width=6,
                                                        className="mb-3"
                                                    )
                                                ]
                                            ),
                                            dbc.Row(
                                                [
                                                    dbc.Col(
                                                        [
                                                            html.H6("ROI Timeline", className="text-muted"),
                                                            dbc.Progress(
                                                                value=55,
                                                                color="info",
                                                                className="mb-2"
                                                            ),
                                                            html.Small("Time to break-even point", className="text-muted"),
                                                            html.P("8-12 years", className="fw-bold text-info")
                                                        ],
                                                        width=6,
                                                        className="mb-3"
                                                    ),
                                                    dbc.Col(
                                                        [
                                                            html.H6("Cost per Unit", className="text-muted"),
                                                            dbc.Progress(
                                                                value=70,
                                                                color="success",
                                                                className="mb-2"
                                                            ),
                                                            html.Small("Cost per acre-foot of water", className="text-muted"),
                                                            html.P("$200-400/acre-ft", className="fw-bold text-success")
                                                        ],
                                                        width=6,
                                                        className="mb-3"
                                                    )
                                                ]
                                            ),
                                            
                                            # Cost Breakdown Table
                                            dbc.Card(
                                                [
                                                    dbc.CardHeader(html.H6("Cost Breakdown", className="mb-0")),
                                                    dbc.CardBody(
                                                        [
                                                            html.Table(
                                                                [
                                                                    html.Thead([
                                                                        html.Tr([
                                                                            html.Th("Component"),
                                                                            html.Th("Low Estimate"),
                                                                            html.Th("High Estimate"),
                                                                            html.Th("Percentage")
                                                                        ])
                                                                    ]),
                                                                    html.Tbody([
                                                                        html.Tr([
                                                                            html.Td("Infrastructure"),
                                                                            html.Td("$1.8M"),
                                                                            html.Td("$3.2M"),
                                                                            html.Td("65%")
                                                                        ]),
                                                                        html.Tr([
                                                                            html.Td("Equipment"),
                                                                            html.Td("$500K"),
                                                                            html.Td("$800K"),
                                                                            html.Td("20%")
                                                                        ]),
                                                                        html.Tr([
                                                                            html.Td("Permits & Legal"),
                                                                            html.Td("$200K"),
                                                                            html.Td("$400K"),
                                                                            html.Td("10%")
                                                                        ]),
                                                                        html.Tr([
                                                                            html.Td("Contingency"),
                                                                            html.Td("$100K"),
                                                                            html.Td("$200K"),
                                                                            html.Td("5%")
                                                                        ])
                                                                    ])
                                                                ],
                                                                className="table table-striped"
                                                            )
                                                        ]
                                                    )
                                                ],
                                                className="mt-3"
                                            ),
                                            
                                            # Summary Section
                                            dbc.Alert(
                                                [
                                                    html.H6("Total Project Cost: $2.5M - $4.2M", className="alert-heading"),
                                                    html.P("Cost analysis shows moderate to high initial investment with reasonable operating costs. Consider phased implementation to reduce upfront capital requirements.", className="mb-0")
                                                ],
                                                color="warning",
                                                className="mt-3"
                                            )
                                        ]
                                    )
                                ],
                                className="mb-4"
                            )
                        ],
                        label_style={
                            "color": "#ffffff", 
                            "fontWeight": "bold",
                            "backgroundColor": "#ffc107",
                            "border": "1px solid #ffc107"
                        },
                        active_label_style={
                            "color": "#ffffff", 
                            "backgroundColor": "#e0a800",
                            "border": "1px solid #e0a800"
                        }
                    ),
                    dbc.Tab(
                        label="Decision Matrix",
                        tab_id="decision-matrix",
                        children=[
                            # Decision Matrix Section
                            dbc.Card(
                                [
                                    dbc.CardHeader(
                                        html.H5("⚖️ Decision Matrix", className="mb-0 text-info")
                                    ),
                                    dbc.CardBody(
                                        [
                                            # Criteria Weights
                                            dbc.Row(
                                                [
                                                    dbc.Col(
                                                        [
                                                            html.H6("Criteria Weights", className="text-muted mb-3"),
                                                            html.Div([
                                                                html.Small("Physical Feasibility: 25%", className="d-block mb-1"),
                                                                dbc.Progress(value=25, color="success", className="mb-2")
                                                            ]),
                                                            html.Div([
                                                                html.Small("Cost Effectiveness: 20%", className="d-block mb-1"),
                                                                dbc.Progress(value=20, color="warning", className="mb-2")
                                                            ]),
                                                            html.Div([
                                                                html.Small("Environmental Impact: 20%", className="d-block mb-1"),
                                                                dbc.Progress(value=20, color="info", className="mb-2")
                                                            ]),
                                                            html.Div([
                                                                html.Small("Technical Complexity: 15%", className="d-block mb-1"),
                                                                dbc.Progress(value=15, color="secondary", className="mb-2")
                                                            ]),
                                                            html.Div([
                                                                html.Small("Social Acceptance: 20%", className="d-block mb-1"),
                                                                dbc.Progress(value=20, color="primary", className="mb-2")
                                                            ])
                                                        ],
                                                        width=6,
                                                        className="mb-3"
                                                    ),
                                                    dbc.Col(
                                                        [
                                                            html.H6("Technology Comparison", className="text-muted mb-3"),
                                                            html.Div([
                                                                html.Small("ASR (Aquifer Storage & Recovery)", className="fw-bold"),
                                                                html.Div([
                                                                    html.Span("Score: 8.2/10", className="badge bg-success me-2"),
                                                                    html.Span("Rank: #1", className="badge bg-primary")
                                                                ], className="mt-1")
                                                            ], className="mb-3 p-2 border rounded"),
                                                            html.Div([
                                                                html.Small("Infiltration Basins", className="fw-bold"),
                                                                html.Div([
                                                                    html.Span("Score: 7.5/10", className="badge bg-warning me-2"),
                                                                    html.Span("Rank: #2", className="badge bg-secondary")
                                                                ], className="mt-1")
                                                            ], className="mb-3 p-2 border rounded"),
                                                            html.Div([
                                                                html.Small("Sand Dams", className="fw-bold"),
                                                                html.Div([
                                                                    html.Span("Score: 6.8/10", className="badge bg-info me-2"),
                                                                    html.Span("Rank: #3", className="badge bg-info")
                                                                ], className="mt-1")
                                                            ], className="mb-3 p-2 border rounded")
                                                        ],
                                                        width=6,
                                                        className="mb-3"
                                                    )
                                                ]
                                            ),
                                            
                                            # Decision Matrix Table
                                            dbc.Card(
                                                [
                                                    dbc.CardHeader(html.H6("Multi-Criteria Decision Matrix", className="mb-0")),
                                                    dbc.CardBody(
                                                        [
                                                            html.Table(
                                                                [
                                                                    html.Thead([
                                                                        html.Tr([
                                                                            html.Th("Technology"),
                                                                            html.Th("Physical", style={"width": "15%"}),
                                                                            html.Th("Cost", style={"width": "15%"}),
                                                                            html.Th("Environmental", style={"width": "15%"}),
                                                                            html.Th("Technical", style={"width": "15%"}),
                                                                            html.Th("Social", style={"width": "15%"}),
                                                                            html.Th("Total Score", style={"width": "15%"})
                                                                        ])
                                                                    ]),
                                                                    html.Tbody([
                                                                        html.Tr([
                                                                            html.Td("ASR", className="fw-bold"),
                                                                            html.Td("9", className="text-success"),
                                                                            html.Td("6", className="text-warning"),
                                                                            html.Td("8", className="text-info"),
                                                                            html.Td("7", className="text-secondary"),
                                                                            html.Td("9", className="text-primary"),
                                                                            html.Td("8.2", className="fw-bold text-success")
                                                                        ]),
                                                                        html.Tr([
                                                                            html.Td("Infiltration Basins", className="fw-bold"),
                                                                            html.Td("8", className="text-success"),
                                                                            html.Td("8", className="text-success"),
                                                                            html.Td("7", className="text-info"),
                                                                            html.Td("8", className="text-success"),
                                                                            html.Td("7", className="text-primary"),
                                                                            html.Td("7.5", className="fw-bold text-warning")
                                                                        ]),
                                                                        html.Tr([
                                                                            html.Td("Sand Dams", className="fw-bold"),
                                                                            html.Td("7", className="text-warning"),
                                                                            html.Td("9", className="text-success"),
                                                                            html.Td("6", className="text-warning"),
                                                                            html.Td("6", className="text-warning"),
                                                                            html.Td("8", className="text-primary"),
                                                                            html.Td("6.8", className="fw-bold text-info")
                                                                        ])
                                                                    ])
                                                                ],
                                                                className="table table-striped table-hover"
                                                            )
                                                        ]
                                                    )
                                                ],
                                                className="mt-3"
                                            ),
                                            
                                            # Recommendation Section
                                            dbc.Alert(
                                                [
                                                    html.H6("Recommended Technology: ASR (Aquifer Storage & Recovery)", className="alert-heading"),
                                                    html.P("Based on the multi-criteria decision matrix, ASR technology scores highest with 8.2/10. It excels in physical feasibility and social acceptance while maintaining reasonable cost and environmental impact.", className="mb-0")
                                                ],
                                                color="success",
                                                className="mt-3"
                                            )
                                        ]
                                    )
                                ],
                                className="mb-4"
                            )
                        ],
                        label_style={
                            "color": "#ffffff", 
                            "fontWeight": "bold",
                            "backgroundColor": "#17a2b8",
                            "border": "1px solid #17a2b8"
                        },
                        active_label_style={
                            "color": "#ffffff", 
                            "backgroundColor": "#138496",
                            "border": "1px solid #138496"
                        }
                    ),
                ],
                id="technology-analysis-tabs",
                active_tab="feasibility-metrics",
                className="mb-4"
            ),
            dbc.Tooltip(
                "Roll-up feasibility score from integrated DSS metrics",
                target="overall-feasibility-score",
                placement="top",
            ),
            dbc.Tooltip(
                "Indicative total capital range from selected MAR technologies",
                target="total-project-cost",
                placement="top",
            ),
            dbc.Tooltip(
                "MAR technologies passing soft and hard constraints",
                target="feasible-technologies-card-body",
                placement="top",
            ),
            dbc.Tooltip(
                "Feasibility metrics, comparisons, and sensitivity views",
                target="technology-analysis-tabs",
                placement="top",
            ),
        ]
    )


