"""
Callbacks for Environmental Impact tab - MAR Source Water Suitability Assessment.
"""

import dash
from dash import Input, Output, html, State, dcc
import plotly.graph_objects as go
import dash_table
import pandas as pd
import dash_bootstrap_components as dbc
from mar_dss.app.components.environmental_impact_tab import (
    DECISION_LOGIC,
    TREATMENT_OPTIONS,
    TREATMENT_COST_MAP,
    VADOSE_REMEDIATION_COSTS,
    COST_SCALE_TO_SCORE,
)
from mar_dss.app.callbacks.ai_environment import get_mar_factors
import mar_dss.app.utils.data_storage as dash_storage


def calculate_cost_score(risks_and_treatments):
    """
    Calculate total costs based on required treatments.
    Separates vadose zone remediation costs from water treatment costs.
    Returns: (water_treatment_cost_per_ft3, vadose_remediation_total_cost, cost_details)
    - water_treatment_cost_per_ft3: estimated water treatment cost per ft³
    - vadose_remediation_total_cost: fixed estimate of $200,000 for vadose zone remediation
      (actual costs can vary from $50K to $10M depending on site conditions)
    - cost_details: list of cost breakdown details with sections
    """
    if not risks_and_treatments:
        return 0, 0, {'water_treatment': [], 'vadose_remediation': []}
    
    water_treatment_cost_per_m3 = 0
    vadose_remediation_cost_per_acreft = 0
    water_treatment_details = []
    vadose_remediation_details = []
    
    # Collect all treatments and their costs
    # For each risk factor, use the most expensive treatment option
    # Then sum across all risk factors (since multiple treatments may be needed)
    for risk_factor, treatments in risks_and_treatments:
        max_cost_for_risk = 0
        best_tech = None
        best_scale = None
        
        for tech_name, cost_scale in treatments:
            # Check if this is a vadose zone remediation treatment
            is_vadose_remediation = tech_name in VADOSE_REMEDIATION_COSTS
            
            if is_vadose_remediation:
                # Get cost from vadose remediation mapping (already in $/acre-ft)
                cost = VADOSE_REMEDIATION_COSTS.get(tech_name, 0)
            elif tech_name in TREATMENT_COST_MAP:
                # Get cost from water treatment mapping (in $/m³)
                cost = TREATMENT_COST_MAP[tech_name]
            else:
                # Try to extract from cost scale
                cost = COST_SCALE_TO_SCORE.get(cost_scale, 0) * 50  # Rough estimate: score * 50 ($/m³)
            
            # Track the most expensive treatment for this risk factor
            if cost > max_cost_for_risk:
                max_cost_for_risk = cost
                best_tech = tech_name
                best_scale = cost_scale
        
        if max_cost_for_risk > 0:
            # Separate vadose zone remediation from water treatment
            is_vadose = best_tech in VADOSE_REMEDIATION_COSTS
            if is_vadose:
                vadose_remediation_cost_per_acreft += max_cost_for_risk
                vadose_remediation_details.append({
                    'risk_factor': risk_factor,
                    'technology': best_tech,
                    'cost_per_acreft': max_cost_for_risk,
                    'cost_scale': best_scale
                })
            else:
                water_treatment_cost_per_m3 += max_cost_for_risk
                water_treatment_details.append({
                    'risk_factor': risk_factor,
                    'technology': best_tech,
                    'cost_per_m3': max_cost_for_risk,
                    'cost_scale': best_scale
                })
    
    # Convert water treatment cost from $/m³ to $/ft³
    # 1 m³ ≈ 35.3147 ft³
    water_treatment_cost_per_ft3 = water_treatment_cost_per_m3 / 35.3147 if water_treatment_cost_per_m3 > 0 else 0
    
    # Update water treatment details to show cost per ft³
    for detail in water_treatment_details:
        if 'cost_per_m3' in detail:
            detail['cost_per_ft3'] = detail['cost_per_m3'] / 35.3147
    
    # Vadose zone remediation is a one-time site cost
    # Use fixed total cost estimate of $200,000
    # Note: Actual costs can vary by orders of magnitude ($50K - $10M) depending on:
    # - Contaminant type and concentration
    # - Site size and depth
    # - Remediation technology required
    # - Regulatory requirements
    vadose_remediation_total_cost = 200000 if vadose_remediation_cost_per_acreft > 0 else 0
    
    # Combine cost details with sections
    cost_details = {
        'water_treatment': water_treatment_details,
        'vadose_remediation': vadose_remediation_details
    }
    
    return round(water_treatment_cost_per_ft3, 2), round(vadose_remediation_total_cost, 2), cost_details


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
            Output('env-cost-gauge', 'figure'),
            Output('env-score-details-output', 'children'),
            Output('env-cost-details-output', 'children'),
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
            Input('env-step6-input', 'value'),
            Input('env-step7-input', 'value')
        ]
    )
    def update_dashboard(*inputs):
        """Update the dashboard based on input selections."""
        # Validate inputs - ensure they're not None
        default_values = ["LOW RISK"] * 8 + ["None"]
        inputs = [inp if inp is not None else default_values[i] for i, inp in enumerate(inputs)]
        
        # Map inputs to logic keys
        input_keys = ["step1_tss", "step2a_doc", "step2b_ph", "step3_tds", "step4_inorganic", "step5a_ec", "step5b_redox", "step6_pathogens", "step7_vadose"]
        
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
            if value not in ["LOW RISK", "None"] and recommendation:
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
                "None": "#d4edda",  # Light green (same as LOW RISK)
                "MODERATE RISK": "#fff3cd",  # Light yellow
                "HIGH RISK": "#f8d7da"  # Light red
            }
            text_color_map = {
                "LOW RISK": "#155724",  # Dark green text
                "None": "#155724",  # Dark green text (same as LOW RISK)
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

        # 4. Calculate Costs
        water_treatment_cost_per_ft3, vadose_remediation_total_cost, cost_details = calculate_cost_score(required_treatments_raw)
        
        # 5. Create Cost Gauge Plot (showing actual cost, not a score)
        try:
            # Fixed range: 0 to 70 $/ft³
            max_range = 70.0
            
            cost_gauge_fig = go.Figure(go.Indicator(
                mode="gauge+number",
                value=water_treatment_cost_per_ft3,
                domain={'x': [0, 1], 'y': [0, 1]},
                title={'text': "Water Treatment Cost ($/ft³)", 'font': {'size': 18}},
                number={'valueformat': '$,.2f', 'suffix': '/ft³'},
                gauge={
                    'axis': {'range': [0, max_range], 'tickwidth': 1, 'tickcolor': "darkblue", 'tickformat': '$,.2f'},
                    'bar': {'color': "darkorange"},
                    'bgcolor': "white",
                    'borderwidth': 2,
                    'bordercolor': "gray",
                    'steps': [
                        {'range': [0, max_range * 0.2], 'color': 'lightgreen'},
                        {'range': [max_range * 0.2, max_range * 0.4], 'color': 'yellow'},
                        {'range': [max_range * 0.4, max_range * 0.6], 'color': 'orange'},
                        {'range': [max_range * 0.6, max_range * 0.8], 'color': 'lightcoral'},
                        {'range': [max_range * 0.8, max_range], 'color': 'red'}],
                    'threshold': {
                        'line': {'color': "red", 'width': 4},
                        'thickness': 0.75,
                        'value': water_treatment_cost_per_ft3}}
            ))
            cost_gauge_fig.update_layout(
                margin=dict(l=10, r=10, t=50, b=10), 
                height=250,
                autosize=True,
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)'
            )
        except Exception as e:
            # Fallback figure if there's an error
            cost_gauge_fig = go.Figure()
            cost_gauge_fig.add_annotation(
                text=f"Error creating cost gauge: {str(e)}",
                xref="paper", yref="paper",
                x=0.5, y=0.5, showarrow=False
            )
            cost_gauge_fig.update_layout(height=250)
        
        # 6. Generate Cost Details Output (with two sections)
        cost_details_html = []
        
        # Section 1: Water Treatment Costs
        water_treatment_details = cost_details.get('water_treatment', [])
        vadose_remediation_details = cost_details.get('vadose_remediation', [])
        
        if water_treatment_details or vadose_remediation_details:
            # Water Treatment Section
            if water_treatment_details:
                cost_details_html.append(html.H6("(1) Water Treatment Costs (per ft³ of source water)", className="font-weight-bold mt-3 mb-2 text-primary"))
                cost_details_html.append(html.P(f"Total Water Treatment Cost: ${water_treatment_cost_per_ft3:.2f}/ft³", className="font-weight-bold mb-2"))
                for detail in water_treatment_details:
                    cost_per_ft3 = detail.get('cost_per_ft3', 0)
                    if cost_per_ft3 > 0:
                        cost_details_html.append(html.Div([
                            html.Span(f"{detail['risk_factor']}: {detail['technology']}", className="font-weight-bold"),
                            html.Span(f" - ${cost_per_ft3:.2f}/ft³", className="float-right badge badge-warning")
                        ], className="d-flex justify-content-between mb-1 p-2 rounded", style={
                            "background-color": "#fff3cd",
                            "border-left": "4px solid #ffc107"
                        }))
            
            # Vadose Zone Remediation Section
            if vadose_remediation_details:
                cost_details_html.append(html.H6("(2) Vadose Zone Remediation Costs (Total Project Cost)", className="font-weight-bold mt-3 mb-2 text-danger"))
                cost_details_html.append(html.P([
                    html.Strong(f"Estimated Total Vadose Zone Remediation Cost: ${vadose_remediation_total_cost:,.0f}"),
                ], className="font-weight-bold mb-2"))
                cost_details_html.append(html.Div([
                    html.P([
                        html.Strong("Note: "),
                        "Vadose zone remediation costs can vary by orders of magnitude depending on contaminant type, "
                        "site size, depth, remediation technology, and regulatory requirements. "
                        "Typical range: $50,000 - $10,000,000. "
                        "The estimate above ($200,000) represents a mid-range scenario. "
                        "Consult with remediation specialists for site-specific cost estimates."
                    ], className="text-muted mb-2", style={"fontSize": "0.9rem", "fontStyle": "italic"})
                ], className="alert alert-warning mb-3"))
                for detail in vadose_remediation_details:
                    cost_per_acreft = detail.get('cost_per_acreft', 0)
                    if cost_per_acreft > 0:
                        cost_details_html.append(html.Div([
                            html.Span(f"{detail['risk_factor']}: {detail['technology']}", className="font-weight-bold"),
                            html.Span(f" - ${cost_per_acreft:,.0f}/acre-ft", className="float-right badge badge-danger")
                        ], className="d-flex justify-content-between mb-1 p-2 rounded", style={
                            "background-color": "#f8d7da",
                            "border-left": "4px solid #dc3545"
                        }))
        else:
            cost_details_html = [
                html.P("No treatment required. Water Treatment Cost: $0.00/ft³", className="text-muted")
            ]
        
        # 7. Generate Treatment Summary Table
        treatment_summary_table = generate_required_treatment_summary(required_treatments_raw)
        
        # 8. Format Recommendations
        if not recommendations_list:
            recommendations_list = [
                html.Li(
                    "All parameters are LOW RISK. No specific recommendations are triggered.", 
                    className="list-group-item list-group-item-success"
                )
            ]
            
        return decision_content, result_style, gauge_fig, cost_gauge_fig, risk_details, cost_details_html, treatment_summary_table, recommendations_list
    
    # Callbacks to save water quality inputs to data storage
    @app.callback(
        Output("env-step1-input", "value"),
        [
            Input("env-step1-input", "value"),
            Input("env-step1-input", "id")
        ],
        prevent_initial_call=False
    )
    def handle_tss_turbidity_risk(value, component_id):
        """Handle TSS/Turbidity risk selection and save to data storage."""
        ctx = dash.callback_context
        
        if not ctx.triggered:
            # Initial load - get saved value or use default, and save it
            tss_risk = dash_storage.get_data("tss_turbidity_risk") or "LOW RISK"
            dash_storage.set_data("tss_turbidity_risk", tss_risk)
            return tss_risk
        
        current_selection = value if value else "LOW RISK"
        dash_storage.set_data("tss_turbidity_risk", current_selection)
        return current_selection
    
    @app.callback(
        Output("env-step2a-input", "value"),
        [
            Input("env-step2a-input", "value"),
            Input("env-step2a-input", "id")
        ],
        prevent_initial_call=False
    )
    def handle_doc_toc_risk(value, component_id):
        """Handle DOC/TOC risk selection and save to data storage."""
        ctx = dash.callback_context
        
        if not ctx.triggered:
            # Initial load - get saved value or use default, and save it
            doc_risk = dash_storage.get_data("doc_toc_risk") or "LOW RISK"
            dash_storage.set_data("doc_toc_risk", doc_risk)
            return doc_risk
        
        current_selection = value if value else "LOW RISK"
        dash_storage.set_data("doc_toc_risk", current_selection)
        return current_selection
    
    @app.callback(
        Output("env-step2b-input", "value"),
        [
            Input("env-step2b-input", "value"),
            Input("env-step2b-input", "id")
        ],
        prevent_initial_call=False
    )
    def handle_ph_alkalinity_risk(value, component_id):
        """Handle pH/Alkalinity risk selection and save to data storage."""
        ctx = dash.callback_context
        
        if not ctx.triggered:
            # Initial load - get saved value or use default, and save it
            ph_risk = dash_storage.get_data("ph_alkalinity_risk") or "LOW RISK"
            dash_storage.set_data("ph_alkalinity_risk", ph_risk)
            return ph_risk
        
        current_selection = value if value else "LOW RISK"
        dash_storage.set_data("ph_alkalinity_risk", current_selection)
        return current_selection
    
    @app.callback(
        Output("env-step3-input", "value"),
        [
            Input("env-step3-input", "value"),
            Input("env-step3-input", "id")
        ],
        prevent_initial_call=False
    )
    def handle_tds_salinity_risk(value, component_id):
        """Handle TDS/Salinity risk selection and save to data storage."""
        ctx = dash.callback_context
        
        if not ctx.triggered:
            # Initial load - get saved value or use default, and save it
            tds_risk = dash_storage.get_data("tds_salinity_risk") or "LOW RISK"
            dash_storage.set_data("tds_salinity_risk", tds_risk)
            return tds_risk
        
        current_selection = value if value else "LOW RISK"
        dash_storage.set_data("tds_salinity_risk", current_selection)
        return current_selection
    
    @app.callback(
        Output("env-step4-input", "value"),
        [
            Input("env-step4-input", "value"),
            Input("env-step4-input", "id")
        ],
        prevent_initial_call=False
    )
    def handle_inorganic_contaminants_risk(value, component_id):
        """Handle Inorganic Contaminants risk selection and save to data storage."""
        ctx = dash.callback_context
        
        if not ctx.triggered:
            # Initial load - get saved value or use default, and save it
            inorganic_risk = dash_storage.get_data("inorganic_contaminants_risk") or "LOW RISK"
            dash_storage.set_data("inorganic_contaminants_risk", inorganic_risk)
            return inorganic_risk
        
        current_selection = value if value else "LOW RISK"
        dash_storage.set_data("inorganic_contaminants_risk", current_selection)
        return current_selection
    
    @app.callback(
        Output("env-step5a-input", "value"),
        [
            Input("env-step5a-input", "value"),
            Input("env-step5a-input", "id")
        ],
        prevent_initial_call=False
    )
    def handle_emerging_contaminants_risk(value, component_id):
        """Handle Emerging Contaminants risk selection and save to data storage."""
        ctx = dash.callback_context
        
        if not ctx.triggered:
            # Initial load - get saved value or use default, and save it
            emerging_risk = dash_storage.get_data("emerging_contaminants_risk") or "LOW RISK"
            dash_storage.set_data("emerging_contaminants_risk", emerging_risk)
            return emerging_risk
        
        current_selection = value if value else "LOW RISK"
        dash_storage.set_data("emerging_contaminants_risk", current_selection)
        return current_selection
    
    @app.callback(
        Output("env-step5b-input", "value"),
        [
            Input("env-step5b-input", "value"),
            Input("env-step5b-input", "id")
        ],
        prevent_initial_call=False
    )
    def handle_redox_compatibility_risk(value, component_id):
        """Handle Redox Compatibility risk selection and save to data storage."""
        ctx = dash.callback_context
        
        if not ctx.triggered:
            # Initial load - get saved value or use default, and save it
            redox_risk = dash_storage.get_data("redox_compatibility_risk") or "LOW RISK"
            dash_storage.set_data("redox_compatibility_risk", redox_risk)
            return redox_risk
        
        current_selection = value if value else "LOW RISK"
        dash_storage.set_data("redox_compatibility_risk", current_selection)
        return current_selection
    
    @app.callback(
        Output("env-step6-input", "value"),
        [
            Input("env-step6-input", "value"),
            Input("env-step6-input", "id")
        ],
        prevent_initial_call=False
    )
    def handle_pathogen_risk(value, component_id):
        """Handle Pathogen risk selection and save to data storage."""
        ctx = dash.callback_context
        
        if not ctx.triggered:
            # Initial load - get saved value or use default, and save it
            pathogen_risk_val = dash_storage.get_data("pathogen_risk") or "LOW RISK"
            dash_storage.set_data("pathogen_risk", pathogen_risk_val)
            return pathogen_risk_val
        
        current_selection = value if value else "LOW RISK"
        dash_storage.set_data("pathogen_risk", current_selection)
        return current_selection
    
    @app.callback(
        Output("env-step7-input", "value"),
        [
            Input("env-step7-input", "value"),
            Input("env-step7-input", "id")
        ],
        prevent_initial_call=False
    )
    def handle_vadose_zone_pollution(value, component_id):
        """Handle Vadose Zone Pollution selection and save to data storage."""
        ctx = dash.callback_context
        
        if not ctx.triggered:
            # Initial load - get saved value or use default, and save it
            vadose_pollution = dash_storage.get_data("vadose_zone_pollution") or "None"
            dash_storage.set_data("vadose_zone_pollution", vadose_pollution)
            return vadose_pollution
        
        current_selection = value if value else "None"
        dash_storage.set_data("vadose_zone_pollution", current_selection)
        return current_selection

    # Callback to load and auto-save Gemini API key
    @app.callback(
        Output('gemini-api-key-input', 'value'),
        [
            Input('gemini-api-key-input', 'value'),
            Input('gemini-api-key-input', 'n_blur'),
            Input('gemini-api-key-input', 'n_submit'),
            Input('gemini-api-key-input', 'id')
        ],
        prevent_initial_call=False
    )
    def handle_gemini_api_key(value, n_blur, n_submit, component_id):
        """Handle Gemini API key input and save to data storage."""
        ctx = dash.callback_context
        
        if not ctx.triggered:
            # Initial load - get saved value or use default
            saved_key = dash_storage.get_data("gemini_api_key") or ""
            dash_storage.set_data("gemini_api_key", saved_key)
            return saved_key
        
        # Get the current value
        current_value = value if value else ""
        
        # Determine which trigger caused the callback
        trigger_prop = ctx.triggered[0]["prop_id"].split(".")[1]
        
        # Save for all triggers except initial load
        if trigger_prop != "id":
            dash_storage.set_data("gemini_api_key", current_value)
        
        return current_value
    
    # Callback to load and auto-save Gemini API file path
    @app.callback(
        Output('gemini-api-file-input', 'value'),
        [
            Input('gemini-api-file-input', 'value'),
            Input('gemini-api-file-input', 'n_blur'),
            Input('gemini-api-file-input', 'n_submit'),
            Input('gemini-api-file-input', 'id')
        ],
        prevent_initial_call=False
    )
    def handle_gemini_api_file(value, n_blur, n_submit, component_id):
        """Handle Gemini API file path input and save to data storage."""
        ctx = dash.callback_context
        
        if not ctx.triggered:
            # Initial load - get saved value or use default
            saved_file = dash_storage.get_data("gemini_api_file") or r"C:\workspace\api\gemini.txt"
            dash_storage.set_data("gemini_api_file", saved_file)
            return saved_file
        
        # Get the current value
        current_value = value if value else r"C:\workspace\api\gemini.txt"
        
        # Determine which trigger caused the callback
        trigger_prop = ctx.triggered[0]["prop_id"].split(".")[1]
        
        # Save for all triggers except initial load
        if trigger_prop != "id":
            dash_storage.set_data("gemini_api_file", current_value)
        
        return current_value
    
    # Callback to save Gemini model and temperature
    @app.callback(
        [
            Output('gemini-model-select', 'value'),
            Output('temperature-slider', 'value')
        ],
        [
            Input('gemini-model-select', 'value'),
            Input('temperature-slider', 'value')
        ],
        prevent_initial_call=False
    )
    def save_gemini_settings(model, temperature):
        """Save Gemini model and temperature settings to data storage."""
        ctx = dash.callback_context
        
        if not ctx.triggered:
            # Initial load - get saved values or use defaults
            saved_model = dash_storage.get_data("gemini_model") or "gemini-2.5-flash"
            saved_temp = float(dash_storage.get_data("gemini_temperature") or 0.5)
            dash_storage.set_data("gemini_model", saved_model)
            dash_storage.set_data("gemini_temperature", saved_temp)
            return saved_model, saved_temp
        
        # Save current values
        if model:
            dash_storage.set_data("gemini_model", model)
        if temperature is not None:
            dash_storage.set_data("gemini_temperature", float(temperature))
        
        # Get current values from storage
        current_model = dash_storage.get_data("gemini_model") or "gemini-2.5-flash"
        current_temp = float(dash_storage.get_data("gemini_temperature") or 0.5)
        return current_model, current_temp
    
    # Callback for MAR Factors Generation (Tab 4.2)
    @app.callback(
        Output('mar-factors-table-container', 'children'),
        [
            Input('generate-mar-factors-btn', 'n_clicks')
        ],
        [
            State('mar-location-input', 'value'),
            State('gemini-model-select', 'value'),
            State('temperature-slider', 'value')
        ],
        prevent_initial_call=True
    )
    def generate_mar_factors_table(n_clicks, location, model, temperature):
        """Generate MAR factors table using AI."""
        if n_clicks == 0 or not location or location.strip() == "":
            return html.Div()
        
        try:
            # Get API key from data storage
            # check if api file exist in C:\workspace\projects\MAR_ESCTP\scripts\mar_dss\src\mar_dss\app
            
            api_key = dash_storage.get_data("gemini_api_key")
            # if not api_key:
            #     return html.Div([
            #         dbc.Alert([
            #             html.H5("API Key Required", className="alert-heading"),
            #             html.P("Please enter and save your Gemini API key in the control panel above before generating MAR factors.", className="mb-0")
            #         ], color="warning")
            #     ])
            # else:
            #     pass
            # Get model and temperature from storage or use provided values
            model = model or dash_storage.get_data("gemini_model") or "gemini-2.5-flash"
            temperature = temperature if temperature is not None else dash_storage.get_data("gemini_temperature") or 0.5
            
            # Call the AI function (this may take a moment)
            df = get_mar_factors(location.strip(), model=model, temperature=temperature)
            
            if df is None or df.empty:
                return html.Div([
                    dbc.Alert([
                        html.H5("No Data Generated", className="alert-heading"),
                        html.P("No factors were generated. Please try again with a different location.", className="mb-0")
                    ], color="warning")
                ])
            
            # Create styled table with colors based on priority (only for Priority column)
            # Define color schemes for priority
            priority_colors = {
                'High': {'bg': '#f8d7da', 'text': '#721c24'},
                'Medium': {'bg': '#fff3cd', 'text': '#856404'},
                'Low': {'bg': '#d4edda', 'text': '#155724'}
            }
            
            # Create conditional styling for Priority column cells only
            style_data_conditional = []
            for idx, row in df.iterrows():
                priority = str(row.get('priority', '')).strip()
                if priority in priority_colors:
                    colors = priority_colors[priority]
                    style_data_conditional.append({
                        'if': {
                            'row_index': idx,
                            'column_id': 'priority'
                        },
                        'backgroundColor': colors['bg'],
                        'color': colors['text'],
                        'fontWeight': 'bold'
                    })
            
            # Add alternating row colors (light blue) for all columns except priority
            # Apply to each non-priority column separately
            for idx in range(len(df)):
                if idx % 2 == 0:  # Even rows get light blue
                    for col in ['category', 'data_point', 'justification']:
                        style_data_conditional.append({
                            'if': {
                                'row_index': idx,
                                'column_id': col
                            },
                            'backgroundColor': '#e3f2fd'
                        })
            
            # Create conditional styling for headers - all green
            style_header_conditional = [
                {
                    'if': {'column_id': col},
                    'backgroundColor': '#28a745',  # Green background
                    'color': 'white',
                    'fontWeight': 'bold'
                }
                for col in df.columns
            ]
            
            # Create the table
            table = dash_table.DataTable(
                id='mar-factors-datatable',
                columns=[
                    {"name": "Category", "id": "category"},
                    {"name": "Data Point/Factor", "id": "data_point"},
                    {"name": "Priority", "id": "priority"},
                    {"name": "Justification", "id": "justification"}
                ],
                data=df.to_dict('records'),
                style_header={
                    'backgroundColor': '#28a745',  # Green background
                    'color': 'white',
                    'fontWeight': 'bold',
                    'textAlign': 'left',
                    'border': '1px solid #dee2e6',
                    'fontSize': '16px'
                },
                style_cell={
                    'textAlign': 'left',
                    'padding': '12px',
                    'fontFamily': 'Arial, sans-serif',
                    'fontSize': '15px',
                    'whiteSpace': 'normal',
                    'height': 'auto',
                    'border': '1px solid #dee2e6'
                },
                style_data={
                    'border': '1px solid #dee2e6'
                },
                style_data_conditional=style_data_conditional,
                style_header_conditional=style_header_conditional,
                page_size=20,
                sort_action="native",
                filter_action="none",
                export_format="csv",
                tooltip_data=[
                    {
                        column: {'value': str(value), 'type': 'markdown'}
                        for column, value in row.items()
                    } for row in df.to_dict('records')
                ],
                tooltip_duration=None
            )
            
            # Wrap table in a card with summary - in its own full-width row
            return dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader([
                            html.H5(f"MAR Factors for {location}", className="mb-0 text-primary"),
                            html.Small(f"Total factors: {len(df)}", className="text-muted")
                        ], className="bg-light"),
                        dbc.CardBody([
                            # Disclaimer
                            dbc.Alert([
                                html.P([
                                    html.Strong("Important Disclaimer: "),
                                    f"The analysis of Managed Aquifer Recharge (MAR) factors specific to {location} was produced using the Google Gemini Large Language Model (LLM). Although this generation incorporates site-specific parameters, we cannot guarantee its accuracy or completeness. The data provided in the matrix below should be used with caution, as it is intended only to offer general guidance regarding MAR's potential environmental, ecological, and cultural considerations."
                                ], className="mb-0")
                            ], color="warning", className="mb-4"),
                            
                            html.Div([
                                html.P([
                                    html.Strong("Categories: "),
                                    html.Span(f"Environmental: {len(df[df['category'] == 'Environmental'])}, ", className="text-info"),
                                    html.Span(f"Ecological: {len(df[df['category'] == 'Ecological'])}, ", className="text-success"),
                                    html.Span(f"Cultural: {len(df[df['category'] == 'Cultural'])}", className="text-warning")
                                ], className="mb-3"),
                                html.P([
                                    html.Strong("Priorities: "),
                                    html.Span(f"High: {len(df[df['priority'].astype(str).str.strip() == 'High'])}, ", className="text-danger"),
                                    html.Span(f"Medium: {len(df[df['priority'].astype(str).str.strip() == 'Medium'])}, ", className="text-warning"),
                                    html.Span(f"Low: {len(df[df['priority'].astype(str).str.strip() == 'Low'])}", className="text-success")
                                ], className="mb-3")
                            ]),
                            html.Div(
                                table, 
                                style={
                                    'overflowX': 'auto',
                                    'width': '100%'
                                }
                            )
                        ])
                    ], className="mt-3")
                ], width=12)
            ])
            
        except Exception as e:
            error_msg = str(e)
            return html.Div([
                dbc.Alert([
                    html.H5("Error generating MAR factors", className="alert-heading"),
                    html.P(f"An error occurred: {error_msg}", className="mb-0")
                ], color="danger")
            ])

    # Callback to display temperature value
    @app.callback(
        Output('temperature-value-display', 'children'),
        [Input('temperature-slider', 'value')]
    )
    def update_temperature_display(temperature):
        """Display the current temperature value."""
        if temperature is not None:
            return html.Span(f"Current value: {temperature:.1f}", className="text-muted")
        return html.Span("Current value: 0.5", className="text-muted")

