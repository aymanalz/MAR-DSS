"""
Callbacks for Environmental Impact tab - MAR Source Water Suitability Assessment.
"""

from dash import Input, Output, html
import plotly.graph_objects as go
import dash_table
from mar_dss.app.components.environmental_impact_tab import (
    DECISION_LOGIC,
    TREATMENT_OPTIONS,
)


def generate_required_treatment_summary(risks_and_treatments):
    """Generate the treatment summary table."""
    if not risks_and_treatments:
        return html.P("No specific treatment required based on inputs.", className="text-muted")

    df_data = []
    for risk, treatments in risks_and_treatments:
        for tech, cost in treatments:
            df_data.append({
                "Risk Factor": risk,
                "Treatment Technology": tech,
                "Cost Scale": cost,
            })
    
    if not df_data:
        return html.P("No specific treatment required based on inputs.", className="text-muted")

    import pandas as pd
    df = pd.DataFrame(df_data).drop_duplicates()
    
    # Sort by a custom cost scale (heuristic)
    cost_order = {
        "Low": 1, 
        "Low to Moderate": 2, 
        "Moderate": 3, 
        "Moderate to High": 4, 
        "High": 5, 
        "Very High": 6, 
        "Very High - Prohibitive": 7, 
        "Moderate + High Study": 3.5, 
        "Moderate Study Cost": 3
    }
    df['Sort_Order'] = df['Cost Scale'].apply(lambda x: cost_order.get(x, 10))
    df = df.sort_values(by=['Sort_Order', 'Risk Factor']).drop(columns=['Sort_Order'])

    return html.Div(
        dash_table.DataTable(
            id='env-treatment-summary-table',
            columns=[{"name": i, "id": i} for i in df.columns],
            data=df.to_dict('records'),
            style_header={
                'backgroundColor': '#e9ecef',
                'fontWeight': 'bold'
            },
            style_cell={
                'textAlign': 'left',
                'minWidth': '100px', 'width': '100px', 'maxWidth': '300px',
                'whiteSpace': 'normal'
            }
        ),
        className='treatment-table'
    )


def setup_environmental_impact_callbacks(app):
    """Set up callbacks for the Environmental Impact tab."""
    
    @app.callback(
        [
            Output('env-final-decision-output', 'children'),
            Output('env-final-decision-output', 'style'),
            Output('env-score-gauge', 'figure'),
            Output('env-score-details-output', 'children'),
            Output('env-treatment-summary-output', 'children'),
            Output('env-recommendations-list', 'children')
        ],
        [
            Input('env-step1-input', 'value'),
            Input('env-step2a-input', 'value'),
            Input('env-step2b-input', 'value'),
            Input('env-step3-input', 'value'),
            Input('env-step4-input', 'value'),
            Input('env-step5a-input', 'value'),
            Input('env-step5b-input', 'value'),
            Input('env-step6-input', 'value')
        ]
    )
    def update_dashboard(*inputs):
        """Update the dashboard based on input selections."""
        # Validate inputs - ensure they're not None
        default_values = ["LOW RISK"] * 8
        inputs = [inp if inp is not None else default_values[i] for i, inp in enumerate(inputs)]
        
        # Map inputs to logic keys
        input_keys = ["step1_tss", "step2a_doc", "step2b_ph", "step3_tds", "step4_inorganic", "step5a_ec", "step5b_redox", "step6_pathogens"]
        
        total_score = 0
        risk_details = []
        
        # Critical flags tracking
        critical_flags = []
        
        # Collect all required treatments and recommendations
        required_treatments_raw = []
        recommendations_list = []

        # 1. Calculate Score and Collect Details
        for key, value in zip(input_keys, inputs):
            step_logic = DECISION_LOGIC[key]
            score_data = step_logic.get(value, {"score": 0, "color": "dark", "treatment_key": "", "rec": "No data."})
            
            score = score_data['score']
            treatment_key = score_data['treatment_key']
            recommendation = score_data['rec']
            
            # Aggregate treatments
            if treatment_key in TREATMENT_OPTIONS:
                risk_factor_name = key.split('_')[-1].upper()  # e.g., TSS, DOC, PH etc.
                required_treatments_raw.append((risk_factor_name, TREATMENT_OPTIONS[treatment_key]))
            
            # Aggregate recommendations
            if value != "LOW RISK" and recommendation:
                recommendations_list.append(
                    html.Li(
                        f"**{key.split('_')[0].upper()}: {value}** - {recommendation}", 
                        className="list-group-item list-group-item-action list-group-item-" + score_data['color']
                    )
                )

            # Check for Critical Flags
            if key == "step3_tds" and value == "HIGH RISK":
                critical_flags.append("TDS increase >500 mg/L (likely NOT SUITABLE, requires economic study)")
            elif key == "step4_inorganic" and value == "HIGH RISK":
                critical_flags.append("Multiple inorganic contaminants >200% of limits (likely NOT SUITABLE, very high cost/complexity)")
            elif key == "step5b_redox" and value == "HIGH RISK" and score == 4:
                critical_flags.append("Severe redox incompatibility (high As mobilization/Fe-Mn precip risk, likely NOT SUITABLE)")
            
            # Only add to total score if not a critical flag
            if score > 0:
                total_score += score
            
            # Add risk detail for the output list with colored background
            # Map risk level to background color
            bg_color_map = {
                "LOW RISK": "#d4edda",  # Light green
                "MODERATE RISK": "#fff3cd",  # Light yellow
                "HIGH RISK": "#f8d7da"  # Light red
            }
            text_color_map = {
                "LOW RISK": "#155724",  # Dark green text
                "MODERATE RISK": "#856404",  # Dark yellow/brown text
                "HIGH RISK": "#721c24"  # Dark red text
            }
            
            bg_color = bg_color_map.get(value, "#f8f9fa")
            text_color = text_color_map.get(value, "#000000")
            
            risk_details.append(html.Div([
                html.Span(f"Step {key.split('_')[0].replace('step','')}: {value}", className="font-weight-bold"),
                html.Span(f" - Score: {score} pt(s)", className="float-right badge badge-" + score_data['color'])
            ], className="d-flex justify-content-between mb-1 p-2 rounded", style={
                "background-color": bg_color,
                "color": text_color,
                "border-left": f"4px solid {text_color}"
            }))

        # 2. Determine Final Decision
        result_style = {
            "padding": "20px",
            "border-radius": "8px",
            "color": "white",
            "text-align": "center"
        }
        
        # Check Critical Flags first
        if critical_flags or total_score >= 8:
            result_style["background-color"] = "#dc3545"  # Red for not suitable
            
            reasons_for_rejection = [
                html.P("The source water is **NOT SUITABLE** for MAR at this location.", className="lead font-weight-bold")
            ]
            reasons_for_rejection.append(html.P(f"Total Risk Score: {total_score} points (Threshold: 8+)", className="mb-2"))
            
            if critical_flags:
                reasons_for_rejection.append(html.H6("⚠️ Critical Flags Triggered:"))
                reasons_for_rejection.extend([html.Li(flag, className="text-white text-left") for flag in critical_flags])
            
            reasons_for_rejection.append(
                html.P("Recommended Action: **Evaluate alternative sources/locations.**", className="mt-3 font-weight-bold")
            )
            
            decision_content = reasons_for_rejection

        elif 3 <= total_score <= 7:
            result_style["background-color"] = "#ffc107"  # Orange/Yellow for conditionally suitable
            result_style["color"] = "#343a40"  # Dark text for better contrast
            
            decision_content = [
                html.P("The source water is **CONDITIONALLY SUITABLE** for MAR.", className="lead font-weight-bold"),
                html.P(f"Total Risk Score: {total_score} points (Range: 3-7)"),
                html.P("Requires specific treatment and further studies to confirm economic viability and technical feasibility.", className="mt-2"),
                html.P("Action: **Proceed to required treatability/modeling studies.**", className="mt-3 font-weight-bold")
            ]
            
        else:  # total_score <= 2
            result_style["background-color"] = "#28a745"  # Green for suitable
            
            decision_content = [
                html.P("The source water is **SUITABLE** for MAR implementation.", className="lead font-weight-bold"),
                html.P(f"Total Risk Score: {total_score} points (Range: 0-2)"),
                html.P("Minimal to no treatment required. Low implementation cost.", className="mt-2")
            ]

        # 3. Create Gauge Plot
        try:
            gauge_fig = go.Figure(go.Indicator(
                mode="gauge+number",
                value=total_score,
                domain={'x': [0, 1], 'y': [0, 1]},
                title={'text': "Total Risk Score", 'font': {'size': 20}},
                gauge={
                    'axis': {'range': [0, 10], 'tickwidth': 1, 'tickcolor': "darkblue"},
                    'bar': {'color': "darkslategray"},
                    'bgcolor': "white",
                    'borderwidth': 2,
                    'bordercolor': "gray",
                    'steps': [
                        {'range': [0, 2], 'color': 'lightgreen'},
                        {'range': [3, 7], 'color': 'yellow'},
                        {'range': [8, 10], 'color': 'red'}],
                    'threshold': {
                        'line': {'color': "red", 'width': 4},
                        'thickness': 0.75,
                        'value': total_score}}
            ))
            gauge_fig.update_layout(
                margin=dict(l=10, r=10, t=50, b=10), 
                height=250,
                autosize=True,
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)'
            )
        except Exception as e:
            # Fallback figure if there's an error
            gauge_fig = go.Figure()
            gauge_fig.add_annotation(
                text=f"Error creating gauge: {str(e)}",
                xref="paper", yref="paper",
                x=0.5, y=0.5, showarrow=False
            )
            gauge_fig.update_layout(height=250)

        # 4. Generate Treatment Summary Table
        treatment_summary_table = generate_required_treatment_summary(required_treatments_raw)
        
        # 5. Format Recommendations
        if not recommendations_list:
            recommendations_list = [
                html.Li(
                    "All parameters are LOW RISK. No specific recommendations are triggered.", 
                    className="list-group-item list-group-item-success"
                )
            ]
            
        return decision_content, result_style, gauge_fig, risk_details, treatment_summary_table, recommendations_list

