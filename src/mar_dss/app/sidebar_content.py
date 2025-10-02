"""
Sidebar content for MAR DSS dashboard.
"""

import dash_bootstrap_components as dbc
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from dash import dcc, html


def create_water_levels_content():
    """Create content for Water Levels sidebar tab."""
    # Generate sample data
    dates = pd.date_range(start="2023-01-01", end="2023-12-31", freq="D")
    water_levels = np.random.normal(100, 10, len(dates)) + 5 * np.sin(
        np.arange(len(dates)) * 2 * np.pi / 365
    )

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=dates,
            y=water_levels,
            mode="lines+markers",
            name="Water Level",
            line=dict(color="#1f77b4", width=2),
            marker=dict(size=4),
        )
    )

    fig.update_layout(
        title="Water Level Monitoring",
        xaxis_title="Date",
        yaxis_title="Water Level (m)",
        hovermode="x unified",
        template="plotly_white",
    )

    return html.Div(
        [
            html.H3("Water Level Monitoring"),
            html.P("Real-time water level data and historical trends."),
            dcc.Graph(figure=fig),
        ]
    )


def create_recharge_content():
    """Create content for Recharge Rates sidebar tab."""
    # Generate sample data
    dates = pd.date_range(start="2023-01-01", end="2023-12-31", freq="D")
    recharge_data = np.random.exponential(2, len(dates)) * (
        1 + 0.5 * np.sin(np.arange(len(dates)) * 2 * np.pi / 365)
    )

    fig = go.Figure()
    fig.add_trace(
        go.Bar(
            x=dates,
            y=recharge_data,
            name="Recharge Rate",
            marker_color="#2ca02c",
        )
    )

    fig.update_layout(
        title="Recharge Rate Analysis",
        xaxis_title="Date",
        yaxis_title="Recharge Rate (mm/day)",
        template="plotly_white",
    )

    return html.Div(
        [
            html.H3("Recharge Rate Analysis"),
            html.P("Recharge rate monitoring and analysis tools."),
            dcc.Graph(figure=fig),
        ]
    )


def create_quality_content():
    """Create content for Decision Interpretation sidebar tab."""
    # Generate sample decision interpretation data
    categories = [
        "Water Supply Security",
        "Environmental Impact",
        "Economic Viability",
        "Technical Feasibility",
        "Regulatory Compliance",
    ]
    scores = [85, 72, 90, 78, 88]
    colors = ["#2E8B57", "#FF6347", "#4169E1", "#FFD700", "#9370DB"]

    fig = go.Figure()
    fig.add_trace(
        go.Bar(
            x=categories,
            y=scores,
            marker_color=colors,
            text=scores,
            textposition="auto",
            name="Decision Scores",
        )
    )

    fig.update_layout(
        title="Decision Interpretation Analysis",
        xaxis_title="Evaluation Criteria",
        yaxis_title="Score (%)",
        hovermode="x unified",
        template="plotly_white",
        height=400,
    )

    return html.Div(
        [
            html.H3("Decision Interpretation"),
            html.P("Analysis and interpretation of decision support results."),
            dcc.Graph(figure=fig),
            html.Hr(),
            html.H5("Key Insights:", className="mt-3"),
            html.Ul(
                [
                    html.Li("Water Supply Security: High confidence (85%)"),
                    html.Li("Economic Viability: Excellent potential (90%)"),
                    html.Li("Regulatory Compliance: Strong alignment (88%)"),
                    html.Li("Environmental Impact: Moderate concerns (72%)"),
                    html.Li("Technical Feasibility: Good prospects (78%)"),
                ]
            ),
            html.Hr(),
            html.H5("Recommendations:", className="mt-3"),
            html.P(
                "Based on the analysis, this MAR project shows strong potential with high scores in water supply security, economic viability, and regulatory compliance. Consider addressing environmental impact concerns through additional mitigation measures."
            ),
        ]
    )


def create_export_content():
    """Create content for Data Export sidebar tab."""
    return html.Div(
        [
            html.H3("Data Export"),
            html.P("Export data in various formats."),
            dbc.Card(
                [
                    dbc.CardBody(
                        [
                            html.H5("Export Options"),
                            dbc.Row(
                                [
                                    dbc.Col(
                                        [
                                            dbc.Button(
                                                "Export CSV",
                                                color="primary",
                                                className="mb-2",
                                            ),
                                            dbc.Button(
                                                "Export Excel",
                                                color="success",
                                                className="mb-2",
                                            ),
                                            dbc.Button(
                                                "Export PDF",
                                                color="warning",
                                                className="mb-2",
                                            ),
                                        ],
                                        width=6,
                                    ),
                                    dbc.Col(
                                        [
                                            html.P("Select data range:"),
                                            dbc.Select(
                                                options=[
                                                    {
                                                        "label": "Last 7 days",
                                                        "value": "7days",
                                                    },
                                                    {
                                                        "label": "Last 30 days",
                                                        "value": "30days",
                                                    },
                                                    {
                                                        "label": "Last 3 months",
                                                        "value": "3months",
                                                    },
                                                    {
                                                        "label": "All data",
                                                        "value": "all",
                                                    },
                                                ],
                                                value="30days",
                                            ),
                                        ],
                                        width=6,
                                    ),
                                ]
                            ),
                        ]
                    )
                ]
            ),
        ]
    )


def create_scenarios_content():
    """Create content for Scenarios Comparison sidebar tab."""
    # Generate sample scenarios data
    scenarios = [
        "Baseline",
        "Optimistic",
        "Pessimistic",
        "Climate Change",
        "High Demand",
    ]
    water_supply = [75, 90, 60, 70, 65]
    cost_effectiveness = [80, 95, 65, 75, 70]
    environmental_impact = [70, 85, 55, 60, 75]

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=scenarios,
            y=water_supply,
            mode="lines+markers",
            name="Water Supply Security",
            line=dict(color="#2E8B57", width=3),
            marker=dict(size=8),
        )
    )
    fig.add_trace(
        go.Scatter(
            x=scenarios,
            y=cost_effectiveness,
            mode="lines+markers",
            name="Cost Effectiveness",
            line=dict(color="#4169E1", width=3),
            marker=dict(size=8),
        )
    )
    fig.add_trace(
        go.Scatter(
            x=scenarios,
            y=environmental_impact,
            mode="lines+markers",
            name="Environmental Impact",
            line=dict(color="#FF6347", width=3),
            marker=dict(size=8),
        )
    )

    fig.update_layout(
        title="Scenarios Comparison Analysis",
        xaxis_title="Scenario",
        yaxis_title="Score (%)",
        hovermode="x unified",
        template="plotly_white",
        height=500,
    )

    return html.Div(
        [
            html.H3("Scenarios Comparison"),
            html.P(
                "Compare different MAR project scenarios and their outcomes."
            ),
            dcc.Graph(figure=fig),
            html.Hr(),
            html.H5("Scenario Analysis:", className="mt-3"),
            html.Div(
                [
                    dbc.Row(
                        [
                            dbc.Col(
                                [
                                    html.H6(
                                        "Baseline Scenario", className="fw-bold"
                                    ),
                                    html.P(
                                        "Standard conditions with moderate growth"
                                    ),
                                    html.Ul(
                                        [
                                            html.Li("Water Supply: 75%"),
                                            html.Li("Cost Effectiveness: 80%"),
                                            html.Li("Environmental: 70%"),
                                        ]
                                    ),
                                ],
                                width=6,
                            ),
                            dbc.Col(
                                [
                                    html.H6(
                                        "Optimistic Scenario",
                                        className="fw-bold",
                                    ),
                                    html.P(
                                        "Best-case conditions with high efficiency"
                                    ),
                                    html.Ul(
                                        [
                                            html.Li("Water Supply: 90%"),
                                            html.Li("Cost Effectiveness: 95%"),
                                            html.Li("Environmental: 85%"),
                                        ]
                                    ),
                                ],
                                width=6,
                            ),
                        ]
                    )
                ]
            ),
            html.Hr(),
            html.H5("Recommendations:", className="mt-3"),
            html.P(
                "The Optimistic scenario shows the highest potential across all metrics. Consider implementing efficiency measures to achieve optimistic outcomes while preparing contingency plans for pessimistic conditions."
            ),
        ]
    )


def create_ai_decision_content():
    """Create content for AI Generated Decision sidebar tab."""
    # Generate AI decision analysis
    decision_factors = [
        "Water Availability",
        "Economic Viability",
        "Environmental Impact",
        "Technical Feasibility",
        "Regulatory Compliance",
        "Social Acceptance",
    ]
    ai_scores = [92, 88, 76, 85, 90, 82]
    confidence_levels = [95, 92, 78, 88, 94, 85]

    fig = go.Figure()
    fig.add_trace(
        go.Bar(
            x=decision_factors,
            y=ai_scores,
            name="AI Assessment Score",
            marker_color="#4CAF50",
            text=ai_scores,
            textposition="auto",
        )
    )
    fig.add_trace(
        go.Scatter(
            x=decision_factors,
            y=confidence_levels,
            mode="markers",
            name="Confidence Level",
            marker=dict(size=12, color="#FF9800", symbol="diamond"),
            yaxis="y2",
        )
    )

    fig.update_layout(
        title="AI Generated Decision Analysis",
        xaxis_title="Decision Factors",
        yaxis=dict(title="Assessment Score (%)", side="left"),
        yaxis2=dict(title="Confidence Level (%)", side="right", overlaying="y"),
        hovermode="x unified",
        template="plotly_white",
        height=500,
    )

    return html.Div(
        [
            html.H3("AI Generated Decision"),
            html.P(
                "Artificial Intelligence powered decision recommendations and analysis."
            ),
            dcc.Graph(figure=fig),
            html.Hr(),
            html.H5("AI Recommendation:", className="mt-3"),
            dbc.Alert(
                [
                    html.H6(
                        "RECOMMENDED: Proceed with MAR Project",
                        className="alert-heading",
                    ),
                    html.P(
                        "Based on comprehensive AI analysis, this project shows strong potential with an overall recommendation score of 85.6%"
                    ),
                    html.Hr(),
                    html.P("Confidence Level: 89%", className="mb-0"),
                ],
                color="success",
            ),
            html.H5("Key AI Insights:", className="mt-3"),
            html.Ul(
                [
                    html.Li(
                        "Water Availability: Excellent (92% score, 95% confidence)"
                    ),
                    html.Li(
                        "Economic Viability: Strong (88% score, 92% confidence)"
                    ),
                    html.Li(
                        "Regulatory Compliance: High (90% score, 94% confidence)"
                    ),
                    html.Li(
                        "Environmental Impact: Moderate (76% score, 78% confidence)"
                    ),
                    html.Li(
                        "Technical Feasibility: Good (85% score, 88% confidence)"
                    ),
                    html.Li(
                        "Social Acceptance: Fair (82% score, 85% confidence)"
                    ),
                ]
            ),
            html.Hr(),
            html.H5("AI Recommendations:", className="mt-3"),
            html.P(
                "The AI system recommends proceeding with the MAR project while implementing additional environmental mitigation measures to address the moderate environmental impact score. Focus on community engagement to improve social acceptance."
            ),
        ]
    )
