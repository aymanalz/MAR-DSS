"""
Environmental Impact tab component - MAR Source Water Suitability Assessment.
Based on chem2.py dashboard.
"""

import dash_bootstrap_components as dbc
from dash import dcc, html, dash_table
import plotly.graph_objects as go
import pandas as pd
import mar_dss.app.utils.data_storage as dash_storage

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
    "step7_vadose": {
        "None": {"score": 0, "color": "success", "treatment_key": "S7_NONE", "rec": "No vadose zone pollution detected. No additional treatment required."},
        "Yes, biodegradable Pollution": {"score": 1, "color": "warning", "treatment_key": "S7_BIO", "rec": "Biodegradable pollution in vadose zone detected. Monitor natural attenuation, consider enhanced bioremediation if needed, implement vadose zone monitoring program."},
        "Yes, highly toxic contaminants in the vadose zone (e.g., heavy metals, volatile organic compounds, radioactive materials)": {"score": 2, "color": "danger", "treatment_key": "S7_TOXIC", "rec": "**CRITICAL:** Highly toxic contaminants in vadose zone detected. Comprehensive site assessment REQUIRED, evaluate source control measures, consider vadose zone remediation, implement intensive monitoring. **WARNING:** Risk of contaminant migration to aquifer."},
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
    "S7_NONE": [],
    "S7_BIO": [("Enhanced Bioremediation (if needed)", "Moderate"), ("Vadose Zone Monitoring Program", "Low to Moderate"), ("Natural Attenuation Monitoring", "Low")],
    "S7_TOXIC": [("Source Control Measures", "Moderate to High"), ("Vadose Zone Remediation (Soil Vapor Extraction, Bioremediation, Chemical Oxidation)", "Very High"), ("Intensive Vadose Zone Monitoring", "Moderate"), ("Containment Barriers (if needed)", "High"), ("Comprehensive Site Assessment", "Moderate + High Study")],
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

# 4. Cost Mapping for Treatment Technologies (maps technology names to average cost per m³)
# Uses mid-point of cost ranges from TREATMENT_DF, or estimates for technologies not in the table
TREATMENT_COST_MAP = {
    "Settling Basins": 20,  # 10-30 avg
    "Sand Filtration": 32.5,  # 15-50 avg
    "pH Adjustment": 15,  # 5-25 avg
    "Aeration": 25,  # 10-40 avg
    "Biological Filtration": 50,  # 20-80 avg
    "Biological Filtration (Slow Sand)": 50,
    "Coagulation + Filtration": 70,  # 40-100 avg
    "Coagulation + Sand Filtration": 70,
    "Enhanced Coagulation + Filtration": 85,
    "Multi-media Filtration": 47.5,  # 25-70 avg
    "Dissolved Air Flotation (DAF)": 105,  # 60-150 avg
    "Ozonation": 175,  # 100-250 avg
    "Ozonation + Bio-filtration": 200,
    "Powdered Activated Carbon (PAC)": 140,  # 80-200 avg
    "PAC": 140,
    "Granular Activated Carbon (GAC)": 210,  # 120-300 avg
    "GAC": 210,
    "GAC + Ion Exchange (for PFAS)": 300,
    "Ion Exchange": 165,  # 80-250 avg
    "Biological Denitrification": 105,  # 60-150 avg
    "Biological Denitrification/Ion Exchange/RO (for Nitrate)": 400,
    "Coagulation/Adsorptive Media/Ion Exchange (for Arsenic)": 200,
    "pH Adjustment + Precipitation/Ion Exchange/Membrane (for Metals)": 350,
    "UV Disinfection": 200,
    "UV/AOP": 275,  # 150-400 avg
    "Advanced Oxidation (UV/H₂O₂)": 275,
    "Advanced Oxidation (UV/H₂O₂ or UV/O₃)": 300,
    "Membrane Filtration (MF/UF)": 140,  # 80-200 avg
    "Membrane (MF/UF)": 140,
    "Membrane Filtration (MF/UF) + UV Disinfection": 340,
    "Multi-barrier: Pre-treatment + UV + Chlorination": 350,
    "Advanced Oxidation (UV/H₂O₂ or O₃) + Filtration": 400,
    "Nanofiltration (NF)": 350,  # 200-500 avg
    "Reverse Osmosis (RO)": 550,  # 300-800 avg
    "Reverse Osmosis": 550,
    "Reverse Osmosis (for PFAS)": 550,
    "Electrodialysis": 425,  # 250-600 avg
    "Multi-stage Treatment Train/Advanced RO System/Combination": 700,
    "Chlorination": 20,
    "Sand/Media Filtration": 32.5,
    "Extended SAT (Soil Aquifer Treatment)": 100,
    "Soil Aquifer Treatment (SAT) - Natural Attenuation": 30,
    "Pre-aeration/De-aeration/Blending Strategy": 25,
    "Redox Control Pre-treatment": 200,
    "Blending with Native Water": 10,
    "Advanced pH Control System": 50,
    "Comprehensive Geochemical Modeling": 0,  # Study cost, not treatment
    "Comprehensive Site Assessment": 0,  # Study cost
    "Enhanced Bioremediation (if needed)": 150,
    "Vadose Zone Monitoring Program": 30,
    "Natural Attenuation Monitoring": 15,
    "NO direct treatment typically effective": 0,  # Study only
    # Note: Vadose zone remediation costs are in VADOSE_REMEDIATION_COSTS, not here
}

# 6. Vadose Zone Remediation Costs (in $/acre-ft for remediation)
# These are separate from water treatment costs and represent site remediation expenses
VADOSE_REMEDIATION_COSTS = {
    "Source Control Measures": 50,  # $/acre-ft
    "Vadose Zone Remediation (Soil Vapor Extraction, Bioremediation, Chemical Oxidation)": 2000,  # $/acre-ft (high cost for comprehensive remediation)
    "Intensive Vadose Zone Monitoring": 20,  # $/acre-ft
    "Containment Barriers (if needed)": 500,  # $/acre-ft
    "Comprehensive Site Assessment": 0,  # Study cost, not per volume
}

# 5. Cost Scale to Score Mapping (converts cost scale descriptions to numeric scores)
COST_SCALE_TO_SCORE = {
    "Low": 1,
    "Low to Moderate": 2,
    "Moderate": 3,
    "Moderate to High": 4,
    "High": 5,
    "Very High": 6,
    "Very High - Prohibitive": 7,
    "Moderate + High Study": 3.5,
    "Moderate Study Cost": 2,
    "Low to Moderate + Study Costs": 2.5,
    "High + Significant Uncertainty": 5.5,
}


# Helper function to create the input cards for each step
def create_step_card(step_id, title, question, options):
    """Create a step card for assessment inputs."""
    return dbc.Card([
        dbc.CardHeader([
            html.H5(title, className="mb-0 text-success")
        ], className="bg-light"),
        dbc.CardBody([
            html.P(question, className="font-weight-bold text-primary", style={"fontSize": "1.15rem"}),
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


def create_water_quality_content():
    """Create the Water Quality and Geochemistry content (sub-tab 4.1)."""
    # Get existing values from data storage if available
    tss_turbidity_risk = dash_storage.get_data("tss_turbidity_risk") or "LOW RISK"
    doc_toc_risk = dash_storage.get_data("doc_toc_risk") or "LOW RISK"
    ph_alkalinity_risk = dash_storage.get_data("ph_alkalinity_risk") or "LOW RISK"
    tds_salinity_risk = dash_storage.get_data("tds_salinity_risk") or "LOW RISK"
    inorganic_contaminants_risk = dash_storage.get_data("inorganic_contaminants_risk") or "LOW RISK"
    emerging_contaminants_risk = dash_storage.get_data("emerging_contaminants_risk") or "LOW RISK"
    redox_compatibility_risk = dash_storage.get_data("redox_compatibility_risk") or "LOW RISK"
    pathogen_risk = dash_storage.get_data("pathogen_risk") or "LOW RISK"
    vadose_zone_pollution = dash_storage.get_data("vadose_zone_pollution") or "None"
    
    return [
        # Main content row
        dbc.Row([
            # Left Column for Inputs (Decision Tree Steps)
            dbc.Col([
                html.H3("Assessment Inputs", className="mb-4 text-primary"),
                
                # ========== GROUP 1: CLOGGING & FOULING RISKS ==========
                html.Div([
                    html.H4("1. Clogging & Fouling Risks", className="mb-3 mt-4 text-primary", style={
                        "border-bottom": "3px solid #007bff",
                        "padding-bottom": "10px"
                    }),
                    
                    # Step 1: Physical Clogging Risk (TSS/Turbidity)
                    dbc.Card([
                        dbc.CardHeader([
                            html.H5("STEP 1: PHYSICAL CLOGGING RISK (TSS/Turbidity)", className="mb-0 text-success")
                        ], className="bg-light"),
                        dbc.CardBody([
                            html.P("Is TSS/Turbidity HIGH?", className="font-weight-bold text-primary", style={"fontSize": "1.15rem"}),
                            dcc.RadioItems(
                                id="env-step1-input",
                                options=[
                                    {'label': "LOW RISK (TSS <10 mg/L, Turbidity <5 NTU)", 'value': "LOW RISK"},
                                    {'label': "MODERATE RISK (TSS 10-20 mg/L, Turbidity 5-10 NTU)", 'value': "MODERATE RISK"},
                                    {'label': "HIGH RISK (TSS >20 mg/L, Turbidity >10 NTU)", 'value': "HIGH RISK"},
                                ],
                                value=tss_turbidity_risk,
                                className="d-flex flex-column",
                                labelStyle={'display': 'block', 'margin-bottom': '8px'}
                            )
                        ])
                    ], className="mb-3", style={
                        "box-shadow": "0 4px 8px 0 rgba(0,0,0,0.2)",
                        "transition": "0.3s",
                        "border-left": "5px solid #007bff"
                    }),
                    
                    # Step 2A: DOC/TOC (Organic Matter Fouling)
                    dbc.Card([
                        dbc.CardHeader([
                            html.H5("STEP 2A: ORGANIC MATTER FOULING RISK (DOC/TOC)", className="mb-0 text-success")
                        ], className="bg-light"),
                        dbc.CardBody([
                            html.P("Is Dissolved Organic Carbon (DOC/TOC) HIGH?", className="font-weight-bold text-primary", style={"fontSize": "1.15rem"}),
                            dcc.RadioItems(
                                id="env-step2a-input",
                                options=[
                                    {'label': "LOW RISK (DOC <5 mg/L)", 'value': "LOW RISK"},
                                    {'label': "MODERATE RISK (DOC 5-10 mg/L)", 'value': "MODERATE RISK"},
                                    {'label': "HIGH RISK (DOC >10 mg/L)", 'value': "HIGH RISK"},
                                ],
                                value=doc_toc_risk,
                                className="d-flex flex-column",
                                labelStyle={'display': 'block', 'margin-bottom': '8px'}
                            )
                        ])
                    ], className="mb-3", style={
                        "box-shadow": "0 4px 8px 0 rgba(0,0,0,0.2)",
                        "transition": "0.3s",
                        "border-left": "5px solid #007bff"
                    }),
                ]),
                
                # ========== GROUP 2: CHEMICAL COMPATIBILITY ==========
                html.Div([
                    html.H4("2. Chemical Compatibility", className="mb-3 mt-4 text-primary", style={
                        "border-bottom": "3px solid #28a745",
                        "padding-bottom": "10px"
                    }),
                    
                    # Step 2B: pH/Alkalinity
                    dbc.Card([
                        dbc.CardHeader([
                            html.H5("STEP 2B: pH/ALKALINITY COMPATIBILITY", className="mb-0 text-success")
                        ], className="bg-light"),
                        dbc.CardBody([
                            html.P("Is pH/Alkalinity Significantly Different from Native Groundwater?", className="font-weight-bold text-primary", style={"fontSize": "1.15rem"}),
                            dcc.RadioItems(
                                id="env-step2b-input",
                                options=[
                                    {'label': "LOW RISK (pH difference <0.5 units, similar alkalinity)", 'value': "LOW RISK"},
                                    {'label': "MODERATE RISK (pH difference 0.5-1.0 units)", 'value': "MODERATE RISK"},
                                    {'label': "HIGH RISK (pH difference >1.0 unit, large alkalinity mismatch)", 'value': "HIGH RISK"},
                                ],
                                value=ph_alkalinity_risk,
                                className="d-flex flex-column",
                                labelStyle={'display': 'block', 'margin-bottom': '8px'}
                            )
                        ])
                    ], className="mb-3", style={
                        "box-shadow": "0 4px 8px 0 rgba(0,0,0,0.2)",
                        "transition": "0.3s",
                        "border-left": "5px solid #28a745"
                    }),
                    
                    # Step 3: Salinity Risk (TDS/Salinity)
                    dbc.Card([
                        dbc.CardHeader([
                            html.H5("STEP 3: SALINITY RISK (CRITICAL CHECKPOINT)", className="mb-0 text-success")
                        ], className="bg-light"),
                        dbc.CardBody([
                            html.P("Is TDS/Salinity significantly higher than Native Groundwater?", className="font-weight-bold text-primary", style={"fontSize": "1.15rem"}),
                            dcc.RadioItems(
                                id="env-step3-input",
                                options=[
                                    {'label': "LOW RISK (TDS increase <250 mg/L)", 'value': "LOW RISK"},
                                    {'label': "MODERATE RISK (TDS increase 250-500 mg/L)", 'value': "MODERATE RISK"},
                                    {'label': "HIGH RISK (TDS increase >500 mg/L)", 'value': "HIGH RISK"},
                                ],
                                value=tds_salinity_risk,
                                className="d-flex flex-column",
                                labelStyle={'display': 'block', 'margin-bottom': '8px'}
                            )
                        ])
                    ], className="mb-3", style={
                        "box-shadow": "0 4px 8px 0 rgba(0,0,0,0.2)",
                        "transition": "0.3s",
                        "border-left": "5px solid #28a745"
                    }),
                    
                    # Step 5B: Redox Compatibility
                    dbc.Card([
                        dbc.CardHeader([
                            html.H5("STEP 5B: REDOX COMPATIBILITY", className="mb-0 text-success")
                        ], className="bg-light"),
                        dbc.CardBody([
                            html.P("Is Source Water Redox State Incompatible with Native Aquifer?", className="font-weight-bold text-primary", style={"fontSize": "1.15rem"}),
                            dcc.RadioItems(
                                id="env-step5b-input",
                                options=[
                                    {'label': "LOW RISK (Similar redox conditions, compatible chemistry)", 'value': "LOW RISK"},
                                    {'label': "MODERATE RISK (Some redox incompatibility, manageable precipitation/mobilization)", 'value': "MODERATE RISK"},
                                    {'label': "HIGH RISK (Significant redox incompatibility, risk of Fe/Mn precipitation or As mobilization)", 'value': "HIGH RISK"},
                                ],
                                value=redox_compatibility_risk,
                                className="d-flex flex-column",
                                labelStyle={'display': 'block', 'margin-bottom': '8px'}
                            )
                        ])
                    ], className="mb-3", style={
                        "box-shadow": "0 4px 8px 0 rgba(0,0,0,0.2)",
                        "transition": "0.3s",
                        "border-left": "5px solid #28a745"
                    }),
                ]),
                
                # ========== GROUP 3: WATER-QUALITY COMPLIANCE ==========
                html.Div([
                    html.H4("3. Water-Quality Compliance", className="mb-3 mt-4 text-primary", style={
                        "border-bottom": "3px solid #dc3545",
                        "padding-bottom": "10px"
                    }),
                    
                    # Step 4: Inorganic Contaminants
                    dbc.Card([
                        dbc.CardHeader([
                            html.H5("STEP 4: INORGANIC CONTAMINANTS (CRITICAL CHECKPOINT)", className="mb-0 text-success")
                        ], className="bg-light"),
                        dbc.CardBody([
                            html.P("Are key Inorganic Contaminants above Regulatory Limits? (Arsenic (>10 µg/L), Nitrate (>50 mg/L as NO₃⁻), Heavy Metals: Pb, Cd, Cr, Hg (above drinking water limits), Fluoride (>1.5 mg/L), Selenium, Boron)", className="font-weight-bold text-primary", style={"fontSize": "1.15rem"}),
                            dcc.RadioItems(
                                id="env-step4-input",
                                options=[
                                    {'label': "LOW RISK (<50% of standard)", 'value': "LOW RISK"},
                                    {'label': "MODERATE RISK (50-100% of limit)", 'value': "MODERATE RISK"},
                                    {'label': "HIGH RISK (≥100% of limit)", 'value': "HIGH RISK"},
                                ],
                                value=inorganic_contaminants_risk,
                                className="d-flex flex-column",
                                labelStyle={'display': 'block', 'margin-bottom': '8px'}
                            )
                        ])
                    ], className="mb-3", style={
                        "box-shadow": "0 4px 8px 0 rgba(0,0,0,0.2)",
                        "transition": "0.3s",
                        "border-left": "5px solid #dc3545"
                    }),
                    
                    # Step 5A: Emerging Contaminants
                    dbc.Card([
                        dbc.CardHeader([
                            html.H5("STEP 5A: EMERGING CONTAMINANTS", className="mb-0 text-success")
                        ], className="bg-light"),
                        dbc.CardBody([
                            html.P("Are Emerging Contaminants Present at Risky Levels? (PFAS (>10-70 ng/L), Pharmaceuticals/Personal Care Products, Endocrine Disrupting Compounds, Pesticides/Herbicides (>regulatory limits), Microplastics)", className="font-weight-bold text-primary", style={"fontSize": "1.15rem"}),
                            dcc.RadioItems(
                                id="env-step5a-input",
                                options=[
                                    {'label': "LOW RISK (Not detected or trace levels well below health-based values)", 'value': "LOW RISK"},
                                    {'label': "MODERATE RISK (Detected at low levels, <2x health-based guidance)", 'value': "MODERATE RISK"},
                                    {'label': "HIGH RISK (Multiple compounds >health guidance OR PFAS >100 ng/L)", 'value': "HIGH RISK"},
                                ],
                                value=emerging_contaminants_risk,
                                className="d-flex flex-column",
                                labelStyle={'display': 'block', 'margin-bottom': '8px'}
                            )
                        ])
                    ], className="mb-3", style={
                        "box-shadow": "0 4px 8px 0 rgba(0,0,0,0.2)",
                        "transition": "0.3s",
                        "border-left": "5px solid #dc3545"
                    }),
                    
                    # Step 6: Pathogen Risk
                    dbc.Card([
                        dbc.CardHeader([
                            html.H5("STEP 6: PATHOGEN RISK (CRITICAL CHECKPOINT)", className="mb-0 text-success")
                        ], className="bg-light"),
                        dbc.CardBody([
                            html.P("Are pathogens present at risky levels? (Consider source type: wastewater > stormwater > surface water > groundwater)", className="font-weight-bold text-primary", style={"fontSize": "1.15rem"}),
                            dcc.RadioItems(
                                id="env-step6-input",
                                options=[
                                    {'label': "LOW RISK", 'value': "LOW RISK"},
                                    {'label': "MODERATE RISK", 'value': "MODERATE RISK"},
                                    {'label': "HIGH RISK", 'value': "HIGH RISK"},
                                ],
                                value=pathogen_risk,
                                className="d-flex flex-column",
                                labelStyle={'display': 'block', 'margin-bottom': '8px'}
                            )
                        ])
                    ], className="mb-3", style={
                        "box-shadow": "0 4px 8px 0 rgba(0,0,0,0.2)",
                        "transition": "0.3s",
                        "border-left": "5px solid #dc3545"
                    }),
                    
                    # Step 7: Vadose Zone Pollution
                    dbc.Card([
                        dbc.CardHeader([
                            html.H5("STEP 7: VADOSE ZONE POLLUTION", className="mb-0 text-success")
                        ], className="bg-light"),
                        dbc.CardBody([
                            html.P("Indicates presence of pollution in the vadose zone.", className="font-weight-bold text-primary", style={"fontSize": "1.15rem"}),
                            dcc.RadioItems(
                                id="env-step7-input",
                                options=[
                                    {'label': "None", 'value': "None"},
                                    {'label': "Yes, biodegradable Pollution", 'value': "Yes, biodegradable Pollution"},
                                    {'label': "Yes, highly toxic contaminants in the vadose zone (e.g., heavy metals, volatile organic compounds, radioactive materials)", 'value': "Yes, highly toxic contaminants in the vadose zone (e.g., heavy metals, volatile organic compounds, radioactive materials)"},
                                ],
                                value=vadose_zone_pollution,
                                className="d-flex flex-column",
                                labelStyle={'display': 'block', 'margin-bottom': '8px'}
                            )
                        ])
                    ], className="mb-3", style={
                        "box-shadow": "0 4px 8px 0 rgba(0,0,0,0.2)",
                        "transition": "0.3s",
                        "border-left": "5px solid #dc3545"
                    }),
                ]),
                
                html.Hr(),
                # Appendix / Detailed Treatment Table (moved under input cards)
                html.H3("APPENDIX: Treatment Cost Summary Table", className="mt-3 mb-3 text-dark"),
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
                
                # Score Tally and Cost Gauge (Side by Side)
                html.H4("Risk Score & Treatment Cost", className="mt-4 mb-3 text-info"),
                dbc.Row([
                    dbc.Col([
                        html.H5("Risk Score", className="text-center mb-2", style={"fontSize": "1rem"}),
                        dcc.Graph(
                            id='env-score-gauge', 
                            config={'displayModeBar': False, 'responsive': True},
                            style={'height': '250px', 'width': '100%', 'minHeight': '250px'}
                        ),
                    ], width=6),
                    dbc.Col([
                        html.H5("Water Treatment Cost", className="text-center mb-2", style={"fontSize": "1rem"}),
                        dcc.Graph(
                            id='env-cost-gauge', 
                            config={'displayModeBar': False, 'responsive': True},
                            style={'height': '250px', 'width': '100%', 'minHeight': '250px'}
                        ),
                    ], width=6),
                ], className="mb-3"),
                
                # Risk Score Details
                html.H5("Risk Score Details", className="mt-3 mb-2 text-info", style={"fontSize": "1.1rem"}),
                html.Div(id='env-score-details-output', className="alert alert-light border mb-3"),
                
                # Cost Details
                html.H5("Cost Details", className="mt-3 mb-2 text-info", style={"fontSize": "1.1rem"}),
                html.Div(id='env-cost-details-output', className="alert alert-light border mb-3"),
                
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
        
        # Removed bottom appendix; moved under Assessment Inputs column
    ]


def create_environmental_considerations_content():
    """Create the Environmental Considerations content (sub-tab 4.2)."""
    return [
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("Environmental Considerations", className="fw-bold bg-primary text-white"),
                    dbc.CardBody([
                        html.H5("AI-Generated MAR Factors Analysis", className="mb-4 text-primary"),
                        
                        # Text and button on same row
                        dbc.Row([
                            dbc.Col([
                                html.P(
                                    "Enter a location to generate a comprehensive list of environmental, ecological, and cultural factors "
                                    "that must be considered for a Managed Aquifer Recharge (MAR) project at that location.",
                                    className="text-muted mb-0"
                                ),
                            ], width=12, md=8),
                            dbc.Col([
                                html.Div([
                                    dbc.Button(
                                        [
                                            html.Div([
                                                html.I(className="fas fa-brain mb-1", style={"display": "block", "fontSize": "3.6rem", "color": "#9c27b0"}),
                                                html.Span("Generate MAR Factors", style={"fontSize": "0.65rem", "display": "block"})
                                            ], style={"display": "flex", "flexDirection": "column", "alignItems": "center", "justifyContent": "center"})
                                        ],
                                        id="generate-mar-factors-btn",
                                        color="success",
                                        className="w-100",
                                        n_clicks=0,
                                        style={
                                            "aspectRatio": "1",
                                            "height": "auto",
                                            "minHeight": "36px",
                                            "maxWidth": "120px",
                                            "display": "flex",
                                            "alignItems": "center",
                                            "justifyContent": "center",
                                            "padding": "5px",
                                            "margin": "0 auto"
                                        }
                                    )
                                ], className="mb-3")
                            ], width=12, md=4, style={"display": "flex", "alignItems": "center", "justifyContent": "center"})
                        ], className="mb-4"),
                        
                        # Input section
                        dbc.Row([
                            dbc.Col([
                                dbc.Label("Location:", className="fw-bold"),
                                dbc.Input(
                                    id="mar-location-input",
                                    type="text",
                                    value="China Lake, CA",
                                    placeholder="Enter location (e.g., City, State or City, Country)",
                                    className="mb-3"
                                ),
                            ], width=12)
                        ]),
                        
                        # Results table with loading indicator
                        dcc.Loading(
                            id="mar-factors-loading",
                            type="default",
                            children=html.Div(id="mar-factors-table-container", className="mt-4")
                        )
                    ])
                ])
            ], width=12, md=6),
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("AI model settings", className="fw-bold bg-info text-white"),
                    dbc.CardBody([
                        html.Div([
                            html.P([
                                html.Strong("(1) "),
                                "To use the Gemini AI model, an API key is required. Go to ",
                                html.A("Google AI Studio", href="https://aistudio.google.com/", target="_blank", className="text-primary"),
                                " and click \"Create API Key\" to generate one."
                            ], className="mb-3"),
                            dcc.Upload(
                                id="api-key-upload",
                                children=html.Div([
                                    html.A("Upload API Key File", className="btn btn-outline-primary btn-sm")
                                ]),
                                style={
                                    "width": "100%",
                                    "height": "40px",
                                    "lineHeight": "40px",
                                    "borderWidth": "1px",
                                    "borderStyle": "dashed",
                                    "borderRadius": "5px",
                                    "textAlign": "center",
                                    "marginBottom": "20px"
                                },
                                multiple=False
                            ),
                            html.P([
                                html.Strong("(2) "),
                                "Choose Gemini Model"
                            ], className="mb-2"),
                            dcc.Dropdown(
                                id="gemini-model-dropdown",
                                options=[
                                    {"label": "gemini-2.5-pro", "value": "gemini-2.5-pro"},
                                    {"label": "gemini-2.5-flash", "value": "gemini-2.5-flash"}
                                ],
                                value="gemini-2.5-flash",
                                clearable=False,
                                style={"marginBottom": "20px"}
                            ),
                            html.P([
                                html.Strong("(3) "),
                                "Temperature: Controls randomness."
                            ], className="mb-2"),
                            dcc.Slider(
                                id="temperature-slider",
                                min=0,
                                max=1,
                                step=0.1,
                                value=0.5,
                                marks={
                                    0: "0",
                                    0.5: "0.5",
                                    1: "1"
                                },
                                tooltip={"placement": "bottom", "always_visible": True}
                            ),
                            html.Div(id="temperature-value-display", className="mt-2 mb-3", style={"fontSize": "0.9rem", "color": "#6c757d"})
                        ])
                    ])
                ])
            ], width=12, md=6)
        ])
    ]


def create_environmental_impact_content():
    """Create the Environmental Impact tab content with sub-tabs."""
    return [
        dbc.Tabs([
            dbc.Tab(
                label="4.1 Water Quality and Geochemistry",
                tab_id="water-quality-tab",
                children=create_water_quality_content()
            ),
            dbc.Tab(
                label="(4.2) AI-Powered Feasibility",
                tab_id="environmental-considerations-tab",
                children=create_environmental_considerations_content()
            )
        ], id="environmental-subtabs", active_tab="water-quality-tab")
    ]
