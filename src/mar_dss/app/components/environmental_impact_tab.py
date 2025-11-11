"""
Environmental Impact tab component - MAR Source Water Suitability Assessment.
Based on chem2.py dashboard.
"""

import dash_bootstrap_components as dbc
from dash import dcc, html, dash_table
import plotly.graph_objects as go
import pandas as pd

# --- Data Structures for Logic and Display ---

# 1. Decision Logic and Scoring (Maps parameter input to score, treatment, and recommendations)
DECISION_LOGIC = {
    "step1_tss": {
        "LOW RISK": {"score": 0, "color": "success", "treatment_key": "S1_LOW", "rec": "None."},
        "MODERATE RISK": {"score": 1, "color": "warning", "treatment_key": "S1_MOD", "rec": "Conduct pilot-scale settling tests, evaluate seasonal variations."},
        "HIGH RISK": {"score": 2, "color": "danger", "treatment_key": "S1_HIGH", "rec": "Jar test studies, evaluate membrane fouling potential, budget for chemical costs."},
    },
    "step2a_doc": {
        "LOW RISK": {"score": 0, "color": "success", "treatment_key": "S2A_LOW", "rec": "None."},
        "MODERATE RISK": {"score": 1, "color": "warning", "treatment_key": "S2A_MOD", "rec": "Conduct biodegradability tests, monitor biofouling, consider oxygenated recharge."},
        "HIGH RISK": {"score": 2, "color": "danger", "treatment_key": "S2A_HIGH", "rec": "Pilot test oxidation effectiveness, evaluate GAC regeneration costs, consider multi-barrier approach."},
    },
    "step2b_ph": {
        "LOW RISK": {"score": 0, "color": "success", "treatment_key": "S2B_LOW", "rec": "None."},
        "MODERATE RISK": {"score": 1, "color": "warning", "treatment_key": "S2B_MOD", "rec": "Geochemical modeling (PHREEQC), pilot injection test, monitor Fe/Mn precipitation."},
        "HIGH RISK": {"score": 3, "color": "danger", "treatment_key": "S2B_HIGH", "rec": "**MANDATORY:** Detailed geochemical assessment, column studies, extended pilot test."},
    },
    "step3_tds": {
        "LOW RISK": {"score": 0, "color": "success", "treatment_key": "S3_LOW", "rec": "None."},
        "MODERATE RISK": {"score": 2, "color": "warning", "treatment_key": "S3_MOD", "rec": "Hydrologic modeling of salinity plume, design buffer zone, implement intensive monitoring. **WARNING:** Long-term salinization risk."},
        "HIGH RISK": {"score": 0, "color": "danger", "treatment_key": "S3_HIGH", "rec": "**AUTOMATIC ESCALATION.** Economic feasibility study REQUIRED, evaluate alternative water sources. **LIKELY OUTCOME:** NOT SUITABLE."},
    },
    "step4_inorganic": {
        "LOW RISK": {"score": 0, "color": "success", "treatment_key": "S4_LOW", "rec": "None."},
        "MODERATE RISK": {"score": 2, "color": "warning", "treatment_key": "S4_MOD", "rec": "Bench-scale treatment studies, pilot testing required, evaluate SAT attenuation potential, waste disposal plan."},
        "HIGH RISK": {"score": 0, "color": "danger", "treatment_key": "S4_HIGH", "rec": "**AUTOMATIC ESCALATION.** Comprehensive treatability study REQUIRED, risk assessment. **LIKELY OUTCOME:** NOT SUITABLE due to cost/complexity."},
    },
    "step5a_ec": {
        "LOW RISK": {"score": 0, "color": "success", "treatment_key": "S5A_LOW", "rec": "None."},
        "MODERATE RISK": {"score": 1, "color": "warning", "treatment_key": "S5A_MOD", "rec": "Soil column attenuation studies, GAC adsorption isotherms, GAC regeneration plan, monitor extraction wells."},
        "HIGH RISK": {"score": 3, "color": "danger", "treatment_key": "S5A_HIGH", "rec": "**Comprehensive treatability study REQUIRED.** PFAS-specific removal testing, multi-year pilot test recommended, budget for spent GAC/PFAS disposal. **WARNING:** Regulatory uncertainty."},
    },
    "step5b_redox": {
        "LOW RISK": {"score": 0, "color": "success", "treatment_key": "S5B_LOW", "rec": "None."},
        "MODERATE RISK": {"score": 2, "color": "warning", "treatment_key": "S5B_MOD", "rec": "**MANDATORY:** Geochemical modeling (PHREEQC/MINTEQ), pilot injection with redox monitoring, monitor Fe, Mn, As."},
        "HIGH RISK": {"score": 4, "color": "danger", "treatment_key": "S5B_HIGH", "rec": "**MANDATORY comprehensive assessment:** 3D reactive transport modeling, extended pilot test, multi-level monitoring wells. **WARNING:** High risk of irreversible aquifer degradation."},
    },
    "step6_pathogens": {
        "LOW RISK": {"score": 0, "color": "success", "treatment_key": "S6_LOW", "rec": "Routine monitoring for indicator organisms recommended."},
        "MODERATE RISK": {"score": 2, "color": "warning", "treatment_key": "S6_MOD", "rec": "Disinfection required. Conduct pathogen monitoring, evaluate disinfection effectiveness, ensure adequate contact time."},
        "HIGH RISK": {"score": 3, "color": "danger", "treatment_key": "S6_HIGH", "rec": "**MANDATORY:** Multi-barrier disinfection approach REQUIRED. Comprehensive pathogen monitoring, extended pilot testing, regulatory compliance verification. **WARNING:** Public health risk if not properly treated."},
    },
}

# 2. Treatment Options Data (Keyed to the logic above)
TREATMENT_OPTIONS = {
    "S1_MOD": [("Settling Basins", "Low to Moderate"), ("Sand Filtration", "Moderate"), ("Multi-media Filtration", "Moderate")],
    "S1_HIGH": [("Coagulation + Sand Filtration", "Moderate to High"), ("Dissolved Air Flotation (DAF)", "High"), ("Membrane Filtration (MF/UF)", "High")],
    "S2A_MOD": [("Biological Filtration (Slow Sand)", "Low to Moderate"), ("Aeration + Bio-filtration", "Moderate"), ("Coagulation + Filtration", "Moderate")],
    "S2A_HIGH": [("Enhanced Coagulation + Filtration", "Moderate to High"), ("Ozonation + Bio-filtration", "High"), ("Granular Activated Carbon (GAC)", "High"), ("Advanced Oxidation (UV/H₂O₂)", "Very High")],
    "S2B_MOD": [("pH Adjustment (Acid/Base Dosing)", "Low"), ("Blending with Native Water", "Low to Moderate")],
    "S2B_HIGH": [("Advanced pH Control System", "Moderate"), ("Comprehensive Geochemical Modeling", "Moderate + High Study")],
    "S3_LOW": [],
    "S3_MOD": [("NO direct treatment typically effective", "Moderate Study Cost")],
    "S3_HIGH": [("Nanofiltration (NF)", "Very High - Prohibitive"), ("Reverse Osmosis (RO)", "Very High - Prohibitive"), ("Electrodialysis", "Very High - Prohibitive")],
    "S4_LOW": [],
    "S4_MOD": [("Biological Denitrification/Ion Exchange/RO (for Nitrate)", "Moderate to Very High"), ("Coagulation/Adsorptive Media/Ion Exchange (for Arsenic)", "Moderate to High"), ("pH Adjustment + Precipitation/Ion Exchange/Membrane (for Metals)", "Low to Very High")],
    "S4_HIGH": [("Multi-stage Treatment Train/Advanced RO System/Combination", "Very High - Prohibitive")],
    "S5A_LOW": [],
    "S5A_MOD": [("Soil Aquifer Treatment (SAT) - Natural Attenuation", "Low to Moderate"), ("Granular Activated Carbon (GAC)", "High"), ("Powdered Activated Carbon (PAC)", "Moderate"), ("Ozonation", "High")],
    "S5A_HIGH": [("GAC + Ion Exchange (for PFAS)", "Very High"), ("Advanced Oxidation (UV/H₂O₂ or UV/O₃)", "Very High"), ("Reverse Osmosis (for PFAS)", "Very High")],
    "S5B_LOW": [],
    "S5B_MOD": [("Pre-aeration/De-aeration/Blending Strategy", "Low to Moderate + Study Costs")],
    "S5B_HIGH": [("Redox Control Pre-treatment", "High + Significant Uncertainty")],
    "S6_LOW": [],
    "S6_MOD": [("UV Disinfection", "Moderate to High"), ("Chlorination", "Low to Moderate"), ("Ozonation", "High"), ("Sand/Media Filtration", "Low to Moderate"), ("Membrane Filtration (MF/UF)", "High")],
    "S6_HIGH": [("Multi-barrier: Pre-treatment + UV + Chlorination", "Very High"), ("Membrane Filtration (MF/UF) + UV Disinfection", "Very High"), ("Advanced Oxidation (UV/H₂O₂ or O₃) + Filtration", "Very High"), ("Reverse Osmosis", "Very High - Prohibitive"), ("Extended SAT (Soil Aquifer Treatment)", "Moderate to High")],
}

# 3. Full Treatment Table for Appendix/Summary
TREATMENT_DF = pd.DataFrame([
    ["Settling Basins", "10-30", "Low", "Low", "High TSS"],
    ["Sand Filtration", "15-50", "Moderate", "Low", "Moderate TSS"],
    ["pH Adjustment", "5-25", "Low", "Moderate", "pH mismatch"],
    ["Aeration", "10-40", "Low-Moderate", "Low-Moderate", "Low DO, VOCs"],
    ["Biological Filtration", "20-80", "Low-Moderate", "Moderate", "DOC, NH₄⁺"],
    ["Coagulation + Filtration", "40-100", "Moderate", "Moderate", "TSS, DOC, turbidity"],
    ["Multi-media Filtration", "25-70", "Moderate", "Moderate", "TSS, fine particles"],
    ["DAF", "60-150", "High", "Moderate", "High TSS, algae"],
    ["Ozonation", "100-250", "High", "High", "DOC, pathogens, oxidation"],
    ["PAC", "80-200", "Moderate", "High", "Organics, taste/odor"],
    ["GAC", "120-300", "High", "Very High", "Organics, PFAS, PPCPs"],
    ["Ion Exchange", "80-250", "Moderate-High", "High", "Nitrate, As, hardness"],
    ["Biological Denitrification", "60-150", "Moderate-High", "Moderate-High", "Nitrate"],
    ["UV/AOP", "150-400", "Very High", "High", "Emerging contaminants"],
    ["Membrane (MF/UF)", "80-200", "High", "High", "Particles, pathogens"],
    ["Nanofiltration", "200-500", "Very High", "Very High", "TDS, hardness, organics"],
    ["Reverse Osmosis", "300-800", "Very High", "Very High", "TDS, salts, most contaminants"],
    ["Electrodialysis", "250-600", "Very High", "Very High", "Salinity, TDS"],
], columns=["Treatment Technology", "Cost Range ($/m³)", "Capital Cost Scale", "O&M Intensity", "Best For"])


# Helper function to create the input cards for each step
def create_step_card(step_id, title, question, options):
    """Create a step card for assessment inputs."""
    return dbc.Card([
        dbc.CardHeader([
            html.H5(title, className="mb-0 text-success")
        ], className="bg-light"),
        dbc.CardBody([
            html.P(question, className="font-weight-bold"),
            dcc.RadioItems(
                id=step_id,
                options=[{'label': opt, 'value': opt} for opt in options],
                value=options[0],  # Default to the lowest risk option
                className="d-flex flex-column",
                labelStyle={'display': 'block', 'margin-bottom': '8px'}
            )
        ])
    ], className="mb-3", style={
        "box-shadow": "0 4px 8px 0 rgba(0,0,0,0.2)",
        "transition": "0.3s",
        "border-left": "5px solid #004d40"
    })


def create_environmental_impact_content():
    """Create the Environmental Impact tab content."""
    return [
        # Main content row
        dbc.Row([
            # Left Column for Inputs (Decision Tree Steps)
            dbc.Col([
                html.H3("Assessment Inputs", className="mb-4 text-primary"),
                
                # Step 1
                create_step_card(
                    "env-step1-input",
                    "STEP 1: PHYSICAL CLOGGING RISK (TSS/Turbidity)",
                    "Is TSS/Turbidity HIGH?",
                    ["LOW RISK", "MODERATE RISK", "HIGH RISK"]
                ),
                
                # Step 2
                dbc.Card([
                    dbc.CardHeader([
                        html.H5("STEP 2: ORGANIC MATTER & GEOCHEMICAL COMPATIBILITY", className="mb-0 text-success")
                    ], className="bg-light"),
                    dbc.CardBody([
                        dbc.Row([
                            dbc.Col([
                                html.P("Question A: Is Dissolved Organic Carbon (DOC/TOC) HIGH?", className="font-weight-bold"),
                                dcc.RadioItems(
                                    id="env-step2a-input",
                                    options=[{'label': opt, 'value': opt} for opt in ["LOW RISK", "MODERATE RISK", "HIGH RISK"]],
                                    value="LOW RISK",
                                    labelStyle={'display': 'block', 'margin-bottom': '8px'}
                                )
                            ], width=12, md=6),
                            dbc.Col([
                                html.P("Question B: Is pH/Alkalinity Significantly Different from Native Groundwater?", className="font-weight-bold"),
                                dcc.RadioItems(
                                    id="env-step2b-input",
                                    options=[{'label': opt, 'value': opt} for opt in ["LOW RISK", "MODERATE RISK", "HIGH RISK"]],
                                    value="LOW RISK",
                                    labelStyle={'display': 'block', 'margin-bottom': '8px'}
                                )
                            ], width=12, md=6)
                        ])
                    ])
                ], className="mb-3", style={
                    "box-shadow": "0 4px 8px 0 rgba(0,0,0,0.2)",
                    "transition": "0.3s",
                    "border-left": "5px solid #004d40"
                }),
                
                # Step 3
                create_step_card(
                    "env-step3-input",
                    "STEP 3: SALINITY RISK (CRITICAL CHECKPOINT)",
                    "Is TDS/Salinity significantly higher than Native Groundwater? (TDS >500-1000 mg/L above native GW)",
                    ["LOW RISK", "MODERATE RISK", "HIGH RISK"]
                ),
                
                # Step 4
                create_step_card(
                    "env-step4-input",
                    "STEP 4: INORGANIC CONTAMINANTS (CRITICAL CHECKPOINT)",
                    "Are key Inorganic Contaminants above Regulatory Limits?",
                    ["LOW RISK", "MODERATE RISK", "HIGH RISK"]
                ),
                
                # Step 5
                dbc.Card([
                    dbc.CardHeader([
                        html.H5("STEP 5: EMERGING CONTAMINANTS & REDOX COMPATIBILITY", className="mb-0 text-success")
                    ], className="bg-light"),
                    dbc.CardBody([
                        dbc.Row([
                            dbc.Col([
                                html.P("Question A: Are Emerging Contaminants Present at Risky Levels?", className="font-weight-bold"),
                                dcc.RadioItems(
                                    id="env-step5a-input",
                                    options=[{'label': opt, 'value': opt} for opt in ["LOW RISK", "MODERATE RISK", "HIGH RISK"]],
                                    value="LOW RISK",
                                    labelStyle={'display': 'block', 'margin-bottom': '8px'}
                                )
                            ], width=12, md=6),
                            dbc.Col([
                                html.P("Question B: Is Source Water Redox State Incompatible with Native Aquifer?", className="font-weight-bold"),
                                dcc.RadioItems(
                                    id="env-step5b-input",
                                    options=[{'label': opt, 'value': opt} for opt in ["LOW RISK", "MODERATE RISK", "HIGH RISK"]],
                                    value="LOW RISK",
                                    labelStyle={'display': 'block', 'margin-bottom': '8px'}
                                )
                            ], width=12, md=6)
                        ])
                    ])
                ], className="mb-3", style={
                    "box-shadow": "0 4px 8px 0 rgba(0,0,0,0.2)",
                    "transition": "0.3s",
                    "border-left": "5px solid #004d40"
                }),
                
                # Step 6
                create_step_card(
                    "env-step6-input",
                    "STEP 6: PATHOGEN RISK (CRITICAL CHECKPOINT)",
                    "Are pathogens present at risky levels? (Consider source type: wastewater > stormwater > surface water > groundwater)",
                    ["LOW RISK", "MODERATE RISK", "HIGH RISK"]
                ),
            ], width=12, lg=8, style={
                "max-height": "calc(100vh - 200px)",
                "overflow-y": "auto",
                "overflow-x": "hidden",
                "padding-right": "10px"
            }),
            
            # Right Column for Outputs (Results, Score, Treatment)
            dbc.Col([
                html.H3("Final Assessment Output", className="mb-4 text-danger"),
                
                # Final Decision Box
                html.Div(id='env-final-decision-output', className="mb-4"),
                
                # Score Tally and Gauge
                html.H4("Risk Score Tally", className="mt-4 mb-3 text-info"),
                dcc.Graph(
                    id='env-score-gauge', 
                    config={'displayModeBar': False, 'responsive': True},
                    style={'height': '250px', 'width': '100%', 'minHeight': '250px'}
                ),
                html.Div(id='env-score-details-output', className="alert alert-light border"),
                
                html.Hr(),
                
                # Treatment Recommendations
                html.H4("🛠️ Required Treatment & Recommendations", className="mt-4 mb-3 text-info"),
                html.Div(id='env-treatment-summary-output', className="mb-4"),
                html.H5("Specific Recommendations by Risk Factor", className="mt-4 text-secondary"),
                html.Ul(id='env-recommendations-list', className="list-group"),
            ], width=12, lg=4, style={
                "position": "sticky",
                "top": "20px",
                "align-self": "start"
            }),
        ]),
        
        html.Hr(),
        
        # Appendix / Detailed Treatment Table
        html.H3("APPENDIX: Treatment Cost Summary Table", className="mt-5 mb-3 text-dark"),
        html.Div(
            dash_table.DataTable(
                id='env-treatment-appendix-table',
                columns=[{"name": i, "id": i} for i in TREATMENT_DF.columns],
                data=TREATMENT_DF.to_dict('records'),
                style_header={
                    'backgroundColor': '#f8f9fa',
                    'fontWeight': 'bold'
                },
                style_cell={
                    'textAlign': 'left',
                    'minWidth': '80px', 'width': '120px', 'maxWidth': '240px',
                    'whiteSpace': 'normal',
                    'border': '1px solid #dee2e6',
                    'fontSize': '13px'
                },
                style_header_conditional=[
                    {'if': {'column_id': 'Treatment Technology'}, 'backgroundColor': '#e3f2fd', 'color': '#0d47a1'},
                    {'if': {'column_id': 'Cost Range ($/m³)'}, 'backgroundColor': '#e8f5e9', 'color': '#1b5e20'},
                    {'if': {'column_id': 'Capital Cost Scale'}, 'backgroundColor': '#fff3e0', 'color': '#e65100'},
                    {'if': {'column_id': "O&M Intensity"}, 'backgroundColor': '#f3e5f5', 'color': '#4a148c'},
                    {'if': {'column_id': 'Best For'}, 'backgroundColor': '#ede7f6', 'color': '#283593'}
                ],
                style_data_conditional=[
                    {'if': {'column_id': 'Treatment Technology'}, 'backgroundColor': '#f5faff'},
                    {'if': {'column_id': 'Cost Range ($/m³)'}, 'backgroundColor': '#f4fbf4'},
                    {'if': {'column_id': 'Capital Cost Scale'}, 'backgroundColor': '#fff8ef'},
                    {'if': {'column_id': "O&M Intensity"}, 'backgroundColor': '#faf4fb'},
                    {'if': {'column_id': 'Best For'}, 'backgroundColor': '#f6f4fb'}
                ],
                export_format='csv'
            ),
            className="mb-4",
            style={
                "maxWidth": "760px",
                "overflowX": "auto"
            }
        )
    ]
