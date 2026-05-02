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
        "MODERATE RISK": {"score": 2, "color": "warning", "treatment_key": "S3_MOD", "rec": "Monitor TDS trends, evaluate blending strategies, consider reverse osmosis if needed."},
        "HIGH RISK": {"score": 4, "color": "danger", "treatment_key": "S3_HIGH", "rec": "**CRITICAL:** Reverse osmosis or advanced desalination required. High capital and O&M costs expected."},
    },
    "step4_inorganic": {
        "LOW RISK": {"score": 0, "color": "success", "treatment_key": "S4_LOW", "rec": "None."},
        "MODERATE RISK": {"score": 2, "color": "warning", "treatment_key": "S4_MOD", "rec": "Enhanced monitoring, consider targeted treatment (e.g., ion exchange, adsorption)."},
        "HIGH RISK": {"score": 5, "color": "danger", "treatment_key": "S4_HIGH", "rec": "**CRITICAL:** Source may be unsuitable without extensive treatment. Regulatory compliance mandatory."},
    },
    "step5a_ec": {
        "LOW RISK": {"score": 0, "color": "success", "treatment_key": "S5A_LOW", "rec": "None."},
        "MODERATE RISK": {"score": 1, "color": "warning", "treatment_key": "S5A_MOD", "rec": "Enhanced monitoring, consider GAC or advanced oxidation processes."},
        "HIGH RISK": {"score": 3, "color": "danger", "treatment_key": "S5A_HIGH", "rec": "Advanced treatment required (GAC, AOP, membrane filtration). High costs and complexity."},
    },
    "step5b_redox": {
        "LOW RISK": {"score": 0, "color": "success", "treatment_key": "S5B_LOW", "rec": "None."},
        "MODERATE RISK": {"score": 1, "color": "warning", "treatment_key": "S5B_MOD", "rec": "Geochemical modeling, monitor Fe/Mn/As mobilization, consider aeration."},
        "HIGH RISK": {"score": 3, "color": "danger", "treatment_key": "S5B_HIGH", "rec": "**MANDATORY:** Detailed redox assessment, pilot injection, consider pre-treatment to adjust redox state."},
    },
    "step6_pathogens": {
        "LOW RISK": {"score": 0, "color": "success", "treatment_key": "S6_LOW", "rec": "None."},
        "MODERATE RISK": {"score": 2, "color": "warning", "treatment_key": "S6_MOD", "rec": "Disinfection required (chlorination, UV, ozonation). Monitor residual and byproducts."},
        "HIGH RISK": {"score": 5, "color": "danger", "treatment_key": "S6_HIGH", "rec": "**CRITICAL:** Multi-barrier disinfection mandatory (filtration + disinfection). Source may be unsuitable for direct recharge."},
    },
    "step7_vadose": {
        "None": {"score": 0, "color": "success", "treatment_key": "S7_NONE", "rec": "None."},
        "Yes, biodegradable Pollution": {"score": 1, "color": "warning", "treatment_key": "S7_BIO", "rec": "Enhanced monitoring, consider biodegradation enhancement."},
        "Yes, highly toxic contaminants in the vadose zone (e.g., heavy metals, volatile organic compounds, radioactive materials)": {"score": 3, "color": "danger", "treatment_key": "S7_TOXIC", "rec": "**CRITICAL:** Source may be unsuitable. Extensive remediation and treatment required."},
    },
}

# 2. Treatment Technology Database
TREATMENT_DF = pd.DataFrame({
    "Treatment Technology": [
        "Sedimentation/Clarification",
        "Media Filtration (Sand/Anthracite)",
        "Membrane Filtration (MF/UF)",
        "Granular Activated Carbon (GAC)",
        "Ion Exchange",
        "Reverse Osmosis (RO)",
        "Advanced Oxidation (AOP)",
        "Disinfection (Chlorination/UV/Ozone)",
        "Aeration/Oxidation",
    ],
    "Cost Range ($/m³)": [
        "$0.05-0.15",
        "$0.10-0.30",
        "$0.20-0.60",
        "$0.30-0.80",
        "$0.40-1.20",
        "$0.80-2.50",
        "$0.50-1.50",
        "$0.10-0.40",
        "$0.15-0.35",
    ],
    "Capital Cost Scale": [
        "Low",
        "Low-Medium",
        "Medium-High",
        "Medium",
        "Medium-High",
        "Very High",
        "High",
        "Low-Medium",
        "Low-Medium",
    ],
    "O&M Intensity": [
        "Low",
        "Low-Medium",
        "Medium",
        "Medium-High",
        "Medium",
        "High",
        "Medium-High",
        "Low",
        "Low-Medium",
    ],
    "Best For": [
        "TSS/Turbidity removal",
        "Particle removal, polishing",
        "Fine particle, pathogen removal",
        "Organic matter, emerging contaminants",
        "Ion removal (nitrate, metals)",
        "TDS/salinity reduction",
        "Emerging contaminants, organics",
        "Pathogen inactivation",
        "Redox adjustment, Fe/Mn removal",
    ],
})

# 3. Treatment Mapping (from decision logic to treatment technologies)
TREATMENT_MAPPING = {
    "S1_LOW": [],
    "S1_MOD": ["Sedimentation/Clarification"],
    "S1_HIGH": ["Sedimentation/Clarification", "Media Filtration (Sand/Anthracite)", "Membrane Filtration (MF/UF)"],
    "S2A_LOW": [],
    "S2A_MOD": ["Granular Activated Carbon (GAC)"],
    "S2A_HIGH": ["Granular Activated Carbon (GAC)", "Advanced Oxidation (AOP)"],
    "S2B_LOW": [],
    "S2B_MOD": ["Aeration/Oxidation"],
    "S2B_HIGH": ["Aeration/Oxidation", "Reverse Osmosis (RO)"],
    "S3_LOW": [],
    "S3_MOD": ["Reverse Osmosis (RO)"],
    "S3_HIGH": ["Reverse Osmosis (RO)"],
    "S4_LOW": [],
    "S4_MOD": ["Ion Exchange", "Media Filtration (Sand/Anthracite)"],
    "S4_HIGH": ["Ion Exchange", "Reverse Osmosis (RO)", "Media Filtration (Sand/Anthracite)"],
    "S5A_LOW": [],
    "S5A_MOD": ["Granular Activated Carbon (GAC)"],
    "S5A_HIGH": ["Granular Activated Carbon (GAC)", "Advanced Oxidation (AOP)", "Membrane Filtration (MF/UF)"],
    "S5B_LOW": [],
    "S5B_MOD": ["Aeration/Oxidation"],
    "S5B_HIGH": ["Aeration/Oxidation", "Reverse Osmosis (RO)"],
    "S6_LOW": [],
    "S6_MOD": ["Disinfection (Chlorination/UV/Ozone)", "Membrane Filtration (MF/UF)"],
    "S6_HIGH": ["Membrane Filtration (MF/UF)", "Disinfection (Chlorination/UV/Ozone)", "Advanced Oxidation (AOP)"],
    "S7_NONE": [],
    "S7_BIO": ["Aeration/Oxidation"],
    "S7_TOXIC": ["Reverse Osmosis (RO)", "Advanced Oxidation (AOP)", "Granular Activated Carbon (GAC)"],
}

# 4. Treatment Options (maps treatment keys to list of (tech_name, cost_scale) tuples)
# Based on TREATMENT_MAPPING and TREATMENT_DF cost scales
TREATMENT_OPTIONS = {
    "S1_LOW": [],
    "S1_MOD": [("Sedimentation/Clarification", "Low")],
    "S1_HIGH": [
        ("Sedimentation/Clarification", "Low"),
        ("Media Filtration (Sand/Anthracite)", "Low-Medium"),
        ("Membrane Filtration (MF/UF)", "Medium-High")
    ],
    "S2A_LOW": [],
    "S2A_MOD": [("Granular Activated Carbon (GAC)", "Medium")],
    "S2A_HIGH": [
        ("Granular Activated Carbon (GAC)", "Medium"),
        ("Advanced Oxidation (AOP)", "High")
    ],
    "S2B_LOW": [],
    "S2B_MOD": [("Aeration/Oxidation", "Low-Medium")],
    "S2B_HIGH": [
        ("Aeration/Oxidation", "Low-Medium"),
        ("Reverse Osmosis (RO)", "Very High")
    ],
    "S3_LOW": [],
    "S3_MOD": [("Reverse Osmosis (RO)", "Very High")],
    "S3_HIGH": [("Reverse Osmosis (RO)", "Very High")],
    "S4_LOW": [],
    "S4_MOD": [
        ("Ion Exchange", "Medium-High"),
        ("Media Filtration (Sand/Anthracite)", "Low-Medium")
    ],
    "S4_HIGH": [
        ("Ion Exchange", "Medium-High"),
        ("Reverse Osmosis (RO)", "Very High"),
        ("Media Filtration (Sand/Anthracite)", "Low-Medium")
    ],
    "S5A_LOW": [],
    "S5A_MOD": [("Granular Activated Carbon (GAC)", "Medium")],
    "S5A_HIGH": [
        ("Granular Activated Carbon (GAC)", "Medium"),
        ("Advanced Oxidation (AOP)", "High"),
        ("Membrane Filtration (MF/UF)", "Medium-High")
    ],
    "S5B_LOW": [],
    "S5B_MOD": [("Aeration/Oxidation", "Low-Medium")],
    "S5B_HIGH": [
        ("Aeration/Oxidation", "Low-Medium"),
        ("Reverse Osmosis (RO)", "Very High")
    ],
    "S6_LOW": [],
    "S6_MOD": [
        ("Disinfection (Chlorination/UV/Ozone)", "Low-Medium"),
        ("Membrane Filtration (MF/UF)", "Medium-High")
    ],
    "S6_HIGH": [
        ("Membrane Filtration (MF/UF)", "Medium-High"),
        ("Disinfection (Chlorination/UV/Ozone)", "Low-Medium"),
        ("Advanced Oxidation (AOP)", "High")
    ],
    "S7_NONE": [],
    "S7_BIO": [("Aeration/Oxidation", "Low-Medium")],
    "S7_TOXIC": [
        ("Reverse Osmosis (RO)", "Very High"),
        ("Advanced Oxidation (AOP)", "High"),
        ("Granular Activated Carbon (GAC)", "Medium")
    ],
}

# 5. Treatment Cost Map (costs in $/m³, using mid-range values from TREATMENT_DF)
TREATMENT_COST_MAP = {
    "Sedimentation/Clarification": 0.10,  # $0.05-0.15 -> 0.10
    "Media Filtration (Sand/Anthracite)": 0.20,  # $0.10-0.30 -> 0.20
    "Membrane Filtration (MF/UF)": 0.40,  # $0.20-0.60 -> 0.40
    "Granular Activated Carbon (GAC)": 0.55,  # $0.30-0.80 -> 0.55
    "Ion Exchange": 0.80,  # $0.40-1.20 -> 0.80
    "Reverse Osmosis (RO)": 1.65,  # $0.80-2.50 -> 1.65
    "Advanced Oxidation (AOP)": 1.00,  # $0.50-1.50 -> 1.00
    "Disinfection (Chlorination/UV/Ozone)": 0.25,  # $0.10-0.40 -> 0.25
    "Aeration/Oxidation": 0.25,  # $0.15-0.35 -> 0.25
}

# 6. Vadose Zone Remediation Costs (in $/acre-ft)
VADOSE_REMEDIATION_COSTS = {
    "Vadose Zone Remediation (Biodegradable)": 50,  # Low end estimate
    "Vadose Zone Remediation (Toxic Contaminants)": 500,  # High end estimate
}

# 7. Cost Scale to Score Mapping (for fallback cost estimation)
COST_SCALE_TO_SCORE = {
    "Low": 1,
    "Low-Medium": 2,
    "Moderate": 3,
    "Medium": 3,
    "Medium-High": 4,
    "High": 5,
    "Very High": 6,
    "Very High - Prohibitive": 7,
    "Moderate Study Cost": 3,
    "Moderate + High Study": 4,
}


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
    
    # Get water quality parameters from data storage
    physical_parameters = dash_storage.get_data("physical_parameters") or []
    chemical_parameters = dash_storage.get_data("chemical_parameters") or []
    biological_indicators = dash_storage.get_data("biological_indicators") or []
    emerging_contaminants = dash_storage.get_data("emerging_contaminants") or []
    
    return [
        # Water Quality Card at the top - Compact
        dbc.Row(
            [
                dbc.Col(
                    [
                        dbc.Card(
                            [
                                dbc.CardHeader(
                                    "Water Quality Parameters",
                                    className="fw-bold bg-primary text-white py-2",
                                    style={"fontSize": "0.9rem"}
                                ),
                                dbc.CardBody(
                                    [
                                        dbc.Row(
                                            [
                                                dbc.Col(
                                                    [
                                                        html.H6(
                                                            "Physical Parameters",
                                                            className="fw-bold mb-2 small",
                                                            style={"fontSize": "0.85rem"}
                                                        ),
                                                        dbc.Checklist(
                                                            id="physical-parameters",
                                                            options=[
                                                                {"label": "Temperature", "value": "temperature"},
                                                                {"label": "Turbidity", "value": "turbidity"},
                                                                {"label": "Total Suspended Solids", "value": "tss"},
                                                            ],
                                                            value=physical_parameters,
                                                            inline=False,
                                                            className="small"
                                                        ),
                                                    ],
                                                    width=3,
                                                ),
                                                dbc.Col(
                                                    [
                                                        html.H6(
                                                            "Chemical Parameters",
                                                            className="fw-bold mb-2 small",
                                                            style={"fontSize": "0.85rem"}
                                                        ),
                                                        dbc.Checklist(
                                                            id="chemical-parameters",
                                                            options=[
                                                                {"label": "Salinity/TDS", "value": "salinity_tds"},
                                                                {"label": "Major Ions", "value": "major_ions"},
                                                                {"label": "Nitrate", "value": "nitrate"},
                                                                {"label": "Phosphate", "value": "phosphate"},
                                                                {"label": "Trace Metals", "value": "trace_metals"},
                                                            ],
                                                            value=chemical_parameters,
                                                            inline=False,
                                                            className="small"
                                                        ),
                                                    ],
                                                    width=3,
                                                ),
                                                dbc.Col(
                                                    [
                                                        html.H6(
                                                            "Biological Indicators",
                                                            className="fw-bold mb-2 small",
                                                            style={"fontSize": "0.85rem"}
                                                        ),
                                                        dbc.Checklist(
                                                            id="biological-indicators",
                                                            options=[
                                                                {"label": "E. coli", "value": "e_coli"},
                                                                {"label": "Viruses", "value": "viruses"},
                                                                {"label": "Protozoa", "value": "protozoa"},
                                                            ],
                                                            value=biological_indicators,
                                                            inline=False,
                                                            className="small"
                                                        ),
                                                    ],
                                                    width=3,
                                                ),
                                                dbc.Col(
                                                    [
                                                        html.H6(
                                                            "Emerging Contaminants",
                                                            className="fw-bold mb-2 small",
                                                            style={"fontSize": "0.85rem"}
                                                        ),
                                                        dbc.Checklist(
                                                            id="emerging-contaminants",
                                                            options=[
                                                                {"label": "PFAS", "value": "pfas"},
                                                                {"label": "Pesticides", "value": "pesticides"},
                                                            ],
                                                            value=emerging_contaminants,
                                                            inline=False,
                                                            className="small"
                                                        ),
                                                    ],
                                                    width=3,
                                                ),
                                            ]
                                        )
                                    ],
                                    style={"padding": "0.75rem"}
                                ),
                            ],
                            className="mb-2"
                        )
                    ],
                    width=12,
                )
            ]
        ),
        # Main content row - Compact layout with 4 cards in grid
        dbc.Row([
            # Left Column for Inputs (Decision Tree Steps) - Grid layout
            dbc.Col([
                html.H5("Assessment Steps", className="mb-3 text-primary", style={"fontSize": "1.1rem"}),
                
                # Four cards in a 2x2 grid
                dbc.Row([
                    # GROUP 1: CLOGGING & FOULING RISKS
                    dbc.Col([
                    dbc.Card([
                        dbc.CardHeader([
                                html.H6("1. Clogging & Fouling Risks", className="mb-0 text-white fw-bold", style={"fontSize": "0.95rem"})
                            ], className="bg-primary py-2"),
                        dbc.CardBody([
                                # Step 1: Physical Clogging Risk (TSS/Turbidity)
                                html.Div([
                                    html.P("STEP 1: Physical Clogging (TSS/Turbidity)", className="fw-bold text-primary mb-2 small", style={"fontSize": "0.85rem"}),
                                    html.P("Is TSS/Turbidity HIGH?", className="text-muted mb-2 small", style={"fontSize": "0.8rem"}),
                            dcc.RadioItems(
                                id="env-step1-input",
                                options=[
                                    {'label': "LOW RISK (TSS <10 mg/L, Turbidity <5 NTU)", 'value': "LOW RISK"},
                                    {'label': "MODERATE RISK (TSS 10-20 mg/L, Turbidity 5-10 NTU)", 'value': "MODERATE RISK"},
                                    {'label': "HIGH RISK (TSS >20 mg/L, Turbidity >10 NTU)", 'value': "HIGH RISK"},
                                ],
                                value=tss_turbidity_risk,
                                        className="d-flex flex-column small",
                                        labelStyle={'display': 'block', 'margin-bottom': '4px', 'fontSize': '0.75rem'}
                                    )
                                ], className="mb-3"),
                    
                    # Step 2A: DOC/TOC (Organic Matter Fouling)
                                html.Div([
                                    html.P("STEP 2A: Organic Matter Fouling (DOC/TOC)", className="fw-bold text-primary mb-2 small", style={"fontSize": "0.85rem"}),
                                    html.P("Is Dissolved Organic Carbon (DOC/TOC) HIGH?", className="text-muted mb-2 small", style={"fontSize": "0.8rem"}),
                            dcc.RadioItems(
                                id="env-step2a-input",
                                options=[
                                    {'label': "LOW RISK (DOC <5 mg/L)", 'value': "LOW RISK"},
                                    {'label': "MODERATE RISK (DOC 5-10 mg/L)", 'value': "MODERATE RISK"},
                                    {'label': "HIGH RISK (DOC >10 mg/L)", 'value': "HIGH RISK"},
                                ],
                                value=doc_toc_risk,
                                        className="d-flex flex-column small",
                                        labelStyle={'display': 'block', 'margin-bottom': '4px', 'fontSize': '0.75rem'}
                                    )
                                ])
                            ], style={"padding": "0.75rem"})
                        ], className="mb-3 h-100", style={
                            "border-left": "4px solid #007bff"
                        })
                    ], width=12, md=6, lg=6),
                    
                    # GROUP 2: CHEMICAL COMPATIBILITY
                    dbc.Col([
                    dbc.Card([
                        dbc.CardHeader([
                                html.H6("2. Chemical Compatibility", className="mb-0 text-white fw-bold", style={"fontSize": "0.95rem"})
                            ], className="bg-success py-2"),
                        dbc.CardBody([
                                # Step 2B: pH/Alkalinity
                                html.Div([
                                    html.P("STEP 2B: pH/Alkalinity Compatibility", className="fw-bold text-primary mb-2 small", style={"fontSize": "0.85rem"}),
                                    html.P("Is pH/Alkalinity Significantly Different from Native Groundwater?", className="text-muted mb-2 small", style={"fontSize": "0.8rem"}),
                            dcc.RadioItems(
                                id="env-step2b-input",
                                options=[
                                    {'label': "LOW RISK (pH difference <0.5 units, similar alkalinity)", 'value': "LOW RISK"},
                                    {'label': "MODERATE RISK (pH difference 0.5-1.0 units)", 'value': "MODERATE RISK"},
                                    {'label': "HIGH RISK (pH difference >1.0 unit, large alkalinity mismatch)", 'value': "HIGH RISK"},
                                ],
                                value=ph_alkalinity_risk,
                                        className="d-flex flex-column small",
                                        labelStyle={'display': 'block', 'margin-bottom': '4px', 'fontSize': '0.75rem'}
                                    )
                                ], className="mb-3"),
                    
                    # Step 3: Salinity Risk (TDS/Salinity)
                                html.Div([
                                    html.P("STEP 3: Salinity Risk (CRITICAL)", className="fw-bold text-primary mb-2 small", style={"fontSize": "0.85rem"}),
                                    html.P("Is TDS/Salinity significantly higher than Native Groundwater?", className="text-muted mb-2 small", style={"fontSize": "0.8rem"}),
                            dcc.RadioItems(
                                id="env-step3-input",
                                options=[
                                    {'label': "LOW RISK (TDS increase <250 mg/L)", 'value': "LOW RISK"},
                                    {'label': "MODERATE RISK (TDS increase 250-500 mg/L)", 'value': "MODERATE RISK"},
                                    {'label': "HIGH RISK (TDS increase >500 mg/L)", 'value': "HIGH RISK"},
                                ],
                                value=tds_salinity_risk,
                                        className="d-flex flex-column small",
                                        labelStyle={'display': 'block', 'margin-bottom': '4px', 'fontSize': '0.75rem'}
                                    )
                                ], className="mb-3"),
                    
                    # Step 5B: Redox Compatibility
                                html.Div([
                                    html.P("STEP 5B: Redox Compatibility", className="fw-bold text-primary mb-2 small", style={"fontSize": "0.85rem"}),
                                    html.P("Is Source Water Redox State Incompatible with Native Aquifer?", className="text-muted mb-2 small", style={"fontSize": "0.8rem"}),
                            dcc.RadioItems(
                                id="env-step5b-input",
                                options=[
                                    {'label': "LOW RISK (Similar redox conditions, compatible chemistry)", 'value': "LOW RISK"},
                                    {'label': "MODERATE RISK (Some redox incompatibility, manageable precipitation/mobilization)", 'value': "MODERATE RISK"},
                                    {'label': "HIGH RISK (Significant redox incompatibility, risk of Fe/Mn precipitation or As mobilization)", 'value': "HIGH RISK"},
                                ],
                                value=redox_compatibility_risk,
                                        className="d-flex flex-column small",
                                        labelStyle={'display': 'block', 'margin-bottom': '4px', 'fontSize': '0.75rem'}
                                    )
                                ])
                            ], style={"padding": "0.75rem"})
                        ], className="mb-3 h-100", style={
                            "border-left": "4px solid #28a745"
                        })
                    ], width=12, md=6, lg=6),
                ], className="mb-3"),
                
                dbc.Row([
                    # GROUP 3: WATER-QUALITY COMPLIANCE
                    dbc.Col([
                    dbc.Card([
                        dbc.CardHeader([
                                html.H6("3. Water-Quality Compliance", className="mb-0 text-white fw-bold", style={"fontSize": "0.95rem"})
                            ], className="bg-danger py-2"),
                        dbc.CardBody([
                                # Step 4: Inorganic Contaminants
                                html.Div([
                                    html.P("STEP 4: Inorganic Contaminants (CRITICAL)", className="fw-bold text-primary mb-2 small", style={"fontSize": "0.85rem"}),
                                    html.P("Are key Inorganic Contaminants above Regulatory Limits?", className="text-muted mb-1 small", style={"fontSize": "0.8rem"}),
                                    html.P("(Arsenic >10 µg/L, Nitrate >50 mg/L, Heavy Metals, Fluoride >1.5 mg/L, Selenium, Boron)", className="text-muted mb-2 small", style={"fontSize": "0.7rem"}),
                            dcc.RadioItems(
                                id="env-step4-input",
                                options=[
                                    {'label': "LOW RISK (<50% of standard)", 'value': "LOW RISK"},
                                    {'label': "MODERATE RISK (50-100% of limit)", 'value': "MODERATE RISK"},
                                    {'label': "HIGH RISK (≥100% of limit)", 'value': "HIGH RISK"},
                                ],
                                value=inorganic_contaminants_risk,
                                        className="d-flex flex-column small",
                                        labelStyle={'display': 'block', 'margin-bottom': '4px', 'fontSize': '0.75rem'}
                                    )
                                ], className="mb-3"),
                    
                    # Step 5A: Emerging Contaminants
                                html.Div([
                                    html.P("STEP 5A: Emerging Contaminants", className="fw-bold text-primary mb-2 small", style={"fontSize": "0.85rem"}),
                                    html.P("Are Emerging Contaminants Present at Risky Levels?", className="text-muted mb-1 small", style={"fontSize": "0.8rem"}),
                                    html.P("(PFAS >10-70 ng/L, Pharmaceuticals, EDCs, Pesticides, Microplastics)", className="text-muted mb-2 small", style={"fontSize": "0.7rem"}),
                            dcc.RadioItems(
                                id="env-step5a-input",
                                options=[
                                    {'label': "LOW RISK (Not detected or trace levels well below health-based values)", 'value': "LOW RISK"},
                                    {'label': "MODERATE RISK (Detected at low levels, <2x health-based guidance)", 'value': "MODERATE RISK"},
                                    {'label': "HIGH RISK (Multiple compounds >health guidance OR PFAS >100 ng/L)", 'value': "HIGH RISK"},
                                ],
                                value=emerging_contaminants_risk,
                                        className="d-flex flex-column small",
                                        labelStyle={'display': 'block', 'margin-bottom': '4px', 'fontSize': '0.75rem'}
                                    )
                                ], className="mb-3"),
                    
                    # Step 6: Pathogen Risk
                                html.Div([
                                    html.P("STEP 6: Pathogen Risk (CRITICAL)", className="fw-bold text-primary mb-2 small", style={"fontSize": "0.85rem"}),
                                    html.P("Are pathogens present at risky levels?", className="text-muted mb-1 small", style={"fontSize": "0.8rem"}),
                                    html.P("(Consider source type: wastewater > stormwater > surface water > groundwater)", className="text-muted mb-2 small", style={"fontSize": "0.7rem"}),
                            dcc.RadioItems(
                                id="env-step6-input",
                                options=[
                                    {'label': "LOW RISK", 'value': "LOW RISK"},
                                    {'label': "MODERATE RISK", 'value': "MODERATE RISK"},
                                    {'label': "HIGH RISK", 'value': "HIGH RISK"},
                                ],
                                value=pathogen_risk,
                                        className="d-flex flex-column small",
                                        labelStyle={'display': 'block', 'margin-bottom': '4px', 'fontSize': '0.75rem'}
                                    )
                                ])
                            ], style={"padding": "0.75rem"})
                        ], className="mb-3 h-100", style={
                            "border-left": "4px solid #dc3545"
                        })
                    ], width=12, md=6, lg=6),
                    
                    # GROUP 4: NEED FOR REMEDIATION
                    dbc.Col([
                    dbc.Card([
                        dbc.CardHeader([
                                html.H6("4. Need for Remediation", className="mb-0 text-white fw-bold", style={"fontSize": "0.95rem"})
                            ], className="bg-secondary py-2"),
                        dbc.CardBody([
                                # Step 7: Vadose Zone Pollution
                                html.Div([
                                    html.P("STEP 7: Vadose Zone Pollution", className="fw-bold text-primary mb-2 small", style={"fontSize": "0.85rem"}),
                                    html.P("Indicates presence of pollution in the vadose zone.", className="text-muted mb-2 small", style={"fontSize": "0.8rem"}),
                            dcc.RadioItems(
                                id="env-step7-input",
                                options=[
                                    {'label': "None", 'value': "None"},
                                    {'label': "Yes, biodegradable Pollution", 'value': "Yes, biodegradable Pollution"},
                                            {'label': "Yes, highly toxic contaminants (e.g., heavy metals, VOCs, radioactive materials)", 'value': "Yes, highly toxic contaminants in the vadose zone (e.g., heavy metals, volatile organic compounds, radioactive materials)"},
                                ],
                                value=vadose_zone_pollution,
                                        className="d-flex flex-column small",
                                        labelStyle={'display': 'block', 'margin-bottom': '4px', 'fontSize': '0.75rem'}
                                    )
                                ])
                            ], style={"padding": "0.75rem"})
                        ], className="mb-3 h-100", style={
                            "border-left": "4px solid #6f42c1"
                        })
                    ], width=12, md=6, lg=6),
                ], className="mb-3"),
                
                html.Hr(className="my-2"),
                # Appendix / Detailed Treatment Table - Compact
                html.H6("Treatment Cost Summary Table", className="mt-2 mb-2 text-dark", style={"fontSize": "0.95rem"}),
                html.Div(
                    dash_table.DataTable(
                        id='env-treatment-appendix-table',
                        columns=[{"name": i, "id": i} for i in TREATMENT_DF.columns],
                        data=TREATMENT_DF.to_dict('records'),
                        style_header={
                            'backgroundColor': '#f8f9fa',
                            'fontWeight': 'bold',
                            'fontSize': '11px'
                        },
                        style_cell={
                            'textAlign': 'left',
                            'minWidth': '70px', 'width': '100px', 'maxWidth': '200px',
                            'whiteSpace': 'normal',
                            'border': '1px solid #dee2e6',
                            'fontSize': '11px',
                            'padding': '5px'
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
                    className="mb-2",
                    style={
                        "maxWidth": "100%",
                        "overflowX": "auto"
                    }
                )
            ], width=12, lg=7, style={
                "padding-right": "10px"
            }),
            
            # Right Column for Outputs (Results, Score, Treatment) - Compact
            dbc.Col([
                # Score Tally and Cost Gauge (Side by Side) - Compact
                html.H6("Risk Score & Treatment Cost", className="mb-2 text-info", style={"fontSize": "0.95rem"}),
                dbc.Row([
                    dbc.Col([
                        html.P("Risk Score", className="text-center mb-1 small fw-bold", style={"fontSize": "0.85rem"}),
                        dcc.Graph(
                            id='env-score-gauge', 
                            config={'displayModeBar': False, 'responsive': True},
                            style={'height': '200px', 'width': '100%', 'minHeight': '200px'}
                        ),
                    ], width=6),
                    dbc.Col([
                        html.P("Treatment Cost", className="text-center mb-1 small fw-bold", style={"fontSize": "0.85rem"}),
                        dcc.Graph(
                            id='env-cost-gauge', 
                            config={'displayModeBar': False, 'responsive': True},
                            style={'height': '200px', 'width': '100%', 'minHeight': '200px'}
                        ),
                    ], width=6),
                ], className="mb-2"),
                
                html.H6("Final Assessment", className="mb-2 text-danger", style={"fontSize": "0.95rem"}),
                
                # Final Decision Box
                html.Div(id='env-final-decision-output', className="mb-2"),
                
                # Risk Score Details
                html.H6("Risk Score Details", className="mt-2 mb-1 text-info small", style={"fontSize": "0.85rem"}),
                html.Div(id='env-score-details-output', className="alert alert-light border mb-2 small", style={"padding": "0.5rem", "fontSize": "0.8rem"}),
                
                # Cost Details
                html.H6("Cost Details", className="mt-2 mb-1 text-info small", style={"fontSize": "0.85rem"}),
                html.Div(id='env-cost-details-output', className="alert alert-light border mb-2 small", style={"padding": "0.5rem", "fontSize": "0.8rem"}),
                
                html.Hr(className="my-2"),
                
                # Treatment Recommendations
                html.H6("Required Treatment & Recommendations", className="mt-2 mb-2 text-info", style={"fontSize": "0.95rem"}),
                html.Div(id='env-treatment-summary-output', className="mb-2"),
                html.H6("Recommendations by Risk Factor", className="mt-2 mb-1 text-secondary small", style={"fontSize": "0.85rem"}),
                html.Ul(id='env-recommendations-list', className="list-group small", style={"fontSize": "0.8rem"}),
            ], width=12, lg=5, style={
                "position": "sticky",
                "top": "20px",
                "align-self": "start"
            }),
        ]),
        dbc.Tooltip(
            "Water-quality parameters to track for suitability scoring",
            target="physical-parameters",
            placement="top",
        ),
        dbc.Tooltip(
            "Constituent groups used in chemical compatibility and compliance steps",
            target="chemical-parameters",
            placement="top",
        ),
        dbc.Tooltip(
            "Pathogen indicators considered in microbial risk scoring",
            target="biological-indicators",
            placement="top",
        ),
        dbc.Tooltip(
            "PFAS, pesticides, and similar constituents of emerging concern",
            target="emerging-contaminants",
            placement="top",
        ),
        dbc.Tooltip(
            "Physical clogging risk from suspended solids and turbidity",
            target="env-step1-input",
            placement="top",
        ),
        dbc.Tooltip(
            "Organic fouling potential from dissolved organic carbon",
            target="env-step2a-input",
            placement="top",
        ),
        dbc.Tooltip(
            "pH and alkalinity mismatch with native groundwater",
            target="env-step2b-input",
            placement="top",
        ),
        dbc.Tooltip(
            "Salinity / TDS mismatch relative to native groundwater",
            target="env-step3-input",
            placement="top",
        ),
        dbc.Tooltip(
            "Redox-driven precipitation or mobilization concerns",
            target="env-step5b-input",
            placement="top",
        ),
        dbc.Tooltip(
            "Regulatory exceedances for major inorganic contaminants",
            target="env-step4-input",
            placement="top",
        ),
        dbc.Tooltip(
            "PFAS, pharmaceuticals, and other emerging contaminants",
            target="env-step5a-input",
            placement="top",
        ),
        dbc.Tooltip(
            "Microbial pathogen risk tier for the selected source type",
            target="env-step6-input",
            placement="top",
        ),
        dbc.Tooltip(
            "Vadose zone contamination that could affect recharge safety",
            target="env-step7-input",
            placement="top",
        ),
        dbc.Tooltip(
            "Reference treatment technologies and indicative unit costs",
            target="env-treatment-appendix-table",
            placement="top",
        ),
        dbc.Tooltip(
            "Composite suitability score from the decision tree",
            target="env-score-gauge",
            placement="top",
        ),
        dbc.Tooltip(
            "Order-of-magnitude treatment cost index from selected technologies",
            target="env-cost-gauge",
            placement="top",
        ),
    ]


def create_environmental_considerations_content():
    """Create the Environmental Considerations content (sub-tab 4.2)."""
    # Get existing API key and file path from data storage if available
    gemini_api_key = dash_storage.get_data("gemini_api_key") or ""
    gemini_api_file = dash_storage.get_data("gemini_api_file") or r"C:\workspace\api\gemini.txt"
    
    return [
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("Environmental Considerations", className="fw-bold bg-primary text-white"),
                    dbc.CardBody([
                        html.H5("AI-Generated MAR Factors Analysis", className="mb-4 text-primary"),
                        
                        # Gemini AI Control Panel
                        dbc.Card([
                            dbc.CardHeader([
                                html.H6("Gemini AI Configuration", className="mb-0 text-white fw-bold")
                            ], className="bg-secondary py-2"),
                            dbc.CardBody([
                                dbc.Row([
                                    dbc.Col([
                                        dbc.Label("Gemini API Key:", className="fw-bold mb-2"),
                                        dbc.Input(
                                            id="gemini-api-key-input",
                                            type="password",
                                            value=gemini_api_key,
                                            placeholder="Enter your Gemini API key",
                                            className="mb-2"
                                        ),
                                        html.Small(
                                            "Your API key is stored locally and used only for generating MAR factors. "
                                            "Get your API key from: https://aistudio.google.com/apikey",
                                            className="text-muted"
                                        ),
                                    ], width=12),
                                ], className="mb-3"),
                                dbc.Row([
                                    dbc.Col([
                                        dbc.Label("API Key File Path (Optional):", className="fw-bold mb-2"),
                                        dbc.Input(
                                            id="gemini-api-file-input",
                                            type="text",
                                            value=gemini_api_file,
                                            placeholder=r"C:\workspace\api\gemini.txt",
                                            className="mb-2"
                                        ),
                                        html.Small(
                                            "Path to a file containing your Gemini API key (used as fallback if API key is not entered directly).",
                                            className="text-muted"
                                        ),
                                    ], width=12),
                                ], className="mb-3"),
                                dbc.Row([
                                    dbc.Col([
                                        dbc.Label("Gemini Model Version:", className="fw-bold mb-2"),
                                        dcc.Dropdown(
                                            id="gemini-model-select",
                                            options=[
                                                {"label": "gemini-2.5-flash", "value": "gemini-2.5-flash"},
                                                {"label": "gemini-1.5-flash", "value": "gemini-1.5-flash"},
                                                {"label": "gemini-1.5-pro", "value": "gemini-1.5-pro"},
                                                {"label": "gemini-pro", "value": "gemini-pro"},
                                            ],
                                            value=dash_storage.get_data("gemini_model") or "gemini-2.5-flash",
                                            placeholder="Select Gemini model",
                                            className="mb-2"
                                        ),
                                    ], width=12, md=6),
                                    dbc.Col([
                                        dbc.Label("Temperature:", className="fw-bold mb-2"),
                                        dcc.Slider(
                                            id="temperature-slider",
                                            min=0.0,
                                            max=2.0,
                                            step=0.1,
                                            value=float(dash_storage.get_data("gemini_temperature") or 0.5),
                                            marks={
                                                0.0: {'label': '0.0', 'style': {'fontSize': '12px'}},
                                                0.5: {'label': '0.5', 'style': {'fontSize': '12px'}},
                                                1.0: {'label': '1.0', 'style': {'fontSize': '12px'}},
                                                1.5: {'label': '1.5', 'style': {'fontSize': '12px'}},
                                                2.0: {'label': '2.0', 'style': {'fontSize': '12px'}}
                                            },
                                            tooltip={"placement": "bottom", "always_visible": True}
                                        ),
                                        html.Div(id="temperature-value-display", className="mt-2"),
                                    ], width=12, md=6),
                                ], className="mb-3"),
                            ], className="p-3")
                        ], className="mb-4 border"),
                        
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
                                        title="Call Gemini with the location to build an environmental factors checklist",
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
                            ], width=12, md=6),
                        ]),
                        
                        # Output section
                        html.Div(id="mar-factors-table-container", className="mt-4"),
                        dbc.Tooltip(
                            "Google Gemini API key (stored locally for this session)",
                            target="gemini-api-key-input",
                            placement="top",
                        ),
                        dbc.Tooltip(
                            "Optional text file on disk containing the API key",
                            target="gemini-api-file-input",
                            placement="top",
                        ),
                        dbc.Tooltip(
                            "Gemini model used for environmental factor generation",
                            target="gemini-model-select",
                            placement="top",
                        ),
                        dbc.Tooltip(
                            "Sampling temperature: lower is more deterministic; higher is more varied",
                            target="temperature-slider",
                            placement="top",
                        ),
                        dbc.Tooltip(
                            "Plain-language place name sent to the AI (e.g., city, state)",
                            target="mar-location-input",
                            placement="top",
                        ),
                    ])
                ])
            ], width=12)
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
                label="4.2 Environmental Considerations",
                tab_id="environmental-considerations-tab",
                children=create_environmental_considerations_content()
            )
        ], id="environmental-subtabs", active_tab="water-quality-tab")
    ]
