"""
Decision Interpretation tab content for MAR DSS dashboard.
"""

import plotly.graph_objects as go
from dash import dcc, html


def create_decision_interpretation_content():
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


