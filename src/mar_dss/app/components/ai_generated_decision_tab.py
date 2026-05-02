"""
AI Generated Decision tab content for MAR DSS dashboard.
"""

import dash_bootstrap_components as dbc
import plotly.graph_objects as go
from dash import dcc, html


def create_ai_generated_decision_content():
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
            dcc.Graph(id="ai-generated-decision-chart", figure=fig),
            dbc.Tooltip(
                "Sample AI-style scoring chart (placeholder narrative dashboard)",
                target="ai-generated-decision-chart",
                placement="top",
            ),
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
                        "Social Acceptance: Fair (82% score, 85% confidence)")
                    ,
                ]
            ),
            html.Hr(),
            html.H5("AI Recommendations:", className="mt-3"),
            html.P(
                "The AI system recommends proceeding with the MAR project while implementing additional environmental mitigation measures to address the moderate environmental impact score. Focus on community engagement to improve social acceptance."
            ),
        ]
    )


