"""
Legal Constraints tab component.

Managed Aquifer Recharge (MAR) legal and regulatory feasibility decision tree:
- Project/Jurisdiction screen
- A) Site feasibility
- B) Water source feasibility
- C) Water quality feasibility

The project is feasible only if all three branches are Feasible or Conditionally feasible.
"""

import dash_bootstrap_components as dbc
from dash import dcc, html


def _section_card(header_text, body_children):
    return dbc.Card(
        [
            dbc.CardHeader(header_text, className="fw-bold bg-light"),
            dbc.CardBody(body_children),
        ],
        className="mb-3",
        style={
            "box-shadow": "0 4px 8px 0 rgba(0,0,0,0.1)",
            "transition": "0.3s",
            "border-left": "5px solid #0d6efd",
        },
    )


def _radio(id_, options, value):
    return dcc.RadioItems(
        id=id_,
        options=[{"label": o, "value": o} for o in options],
        value=value,
        className="d-flex flex-column",
        labelStyle={"display": "block", "margin-bottom": "8px"},
    )


def _pill(label, color="secondary"):
    return html.Span(label, className=f"badge bg-{color} ms-2")


def create_basic_regulation_feasibility_content():
    """Create the Basic Regulation Feasibility content (sub-tab 1)."""
    return [
        dbc.Row(
            [
                # Left: Inputs
                dbc.Col(
                    [
                        html.H3("Legal & Regulatory Feasibility Inputs", className="mb-4 text-primary"),
                        dbc.Alert(
                            [
                                html.I(className="fas fa-triangle-exclamation me-2"),
                                html.Strong("Legal disclaimer: "),
                                "This decision aid is for informational purposes only and does not constitute legal advice. ",
                                "Regulatory requirements vary by jurisdiction and project specifics. ",
                                "Additional review may be required to confirm local, state, Tribal, and federal laws, permits, and approvals.",
                            ],
                            color="danger",
                            className="mb-4",
                        ),

                        # 0) Project/Jurisdiction screen
                        _section_card(
                            "0) Project/Jurisdiction Screen",
                            [
                                html.P("(Federal nexus) Does your project has a direct federal connection such that federal environmental laws and reviews are triggered?"),
                                _radio(
                                    "legal-proj-federal-nexus",
                                    ["No", "Yes - NEPA (National Environmental Policy Act) / ESA (Endangered Species Act) / NHPA (National Historic Preservation Act) likely"],
                                    "No",
                                ),
                                html.Hr(),
                                html.P("Tribal or interstate context?"),
                                _radio(
                                    "legal-proj-tribal-interstate",
                                    ["None", "Tribal lands/resources", "Interstate compact", "Both"],
                                    "None",
                                ),
                            ],
                        ),

                        # A) Site feasibility
                        _section_card(
                            "A) Site Feasibility (Location, Land Rights, Environmental Review)",
                            [
                                html.P("A1. Site control and access"),
                                _radio(
                                    "legal-site-control",
                                    ["Have site control", "Can secure site control", "Cannot secure site control (Prohibited)"],
                                    "Have site control",
                                ),
                                html.Hr(),
                                html.P("A2. Land use and local approvals (zoning/conditional use/building/floodplain)"),
                                _radio(
                                    "legal-site-zoning",
                                    ["Allowed", "Conditionally allowed (permit/variance)", "Prohibited (no variance)"],
                                    "Allowed",
                                ),
                                html.Hr(),
                                html.P("A3. Waters/wetlands impacts (CWA (Clean Water Act) §§404/401; RHA (Rivers and Harbors Act) §10)"),
                                _radio(
                                    "legal-site-wetlands",
                                    ["No impacts", "General permit likely", "Individual permit feasible", "Permit unlikely (Prohibited)"],
                                    "No impacts",
                                ),
                                html.Hr(),
                                html.P("A4. Sensitive resources (ESA/cultural/historic/critical areas)"),
                                _radio(
                                    "legal-site-sensitive",
                                    ["None", "Present - mitigable", "Present - unmitigable (Prohibited)"],
                                    "None",
                                ),
                                html.Hr(),
                                html.P("A5. Public lands/federal facilities authorizations"),
                                _radio(
                                    "legal-site-public-lands",
                                    ["Not applicable", "Authorizations obtainable", "Authorizations unobtainable (Prohibited)"],
                                    "Not applicable",
                                ),
                                html.Hr(),
                                html.P("A6. Dam safety/geotechnical constraints"),
                                _radio(
                                    "legal-site-dams",
                                    ["Not applicable", "Approvable with conditions", "Not approvable (Prohibited)"],
                                    "Not applicable",
                                ),
                                html.Hr(),
                                html.P("A7. Subsidence/seismic constraints"),
                                _radio(
                                    "legal-site-seismic",
                                    ["Compliant", "Mitigable", "Noncompliant (Prohibited)"],
                                    "Compliant",
                                ),
                            ],
                        ),

                        # B) Water source feasibility
                        _section_card(
                            "B) Water Source Feasibility (Rights, Compacts, Conveyance)",
                            [
                                html.P("B1. Legal right/entitlement to source (incl. storage for recharge)"),
                                _radio(
                                    "legal-src-right",
                                    ["Valid right/contract", "Obtainable without injury", "No path to a valid right (Prohibited)"],
                                    "Valid right/contract",
                                ),
                                html.Hr(),
                                html.P("B2. Recharge authorization, accounting, and recovery (state MAR (Managed Aquifer Recharge)/ASR (Aquifer Storage and Recovery) framework)"),
                                _radio(
                                    "legal-src-accounting",
                                    ["Authorized", "Authorizable with conditions", "No statutory/administrative pathway (Prohibited)"],
                                    "Authorized",
                                ),
                                html.Hr(),
                                html.P("B3. Interstate compact/delivery compliance"),
                                _radio(
                                    "legal-src-compact",
                                    ["Not applicable", "Compliant", "Noncompliant (Prohibited)"],
                                    "Not applicable",
                                ),
                                html.Hr(),
                                html.P("B4. Source-specific compliance feasible?"),
                                dcc.Dropdown(
                                    id="legal-src-type",
                                    options=[
                                        {"label": "Stormwater/Urban Runoff", "value": "stormwater"},
                                        {"label": "Surface Water", "value": "surface"},
                                        {"label": "Recycled Water", "value": "recycled"},
                                        {"label": "Agricultural Drainage/Return Flows", "value": "ag"},
                                        {"label": "Other/Industrial", "value": "other"},
                                    ],
                                    value="stormwater",
                                    clearable=False,
                                    style={"maxWidth": "420px"},
                                ),
                                _radio(
                                    "legal-src-type-feasible",
                                    ["Feasible", "Feasible with conditions", "Not feasible (Prohibited)"],
                                    "Feasible",
                                ),
                                html.Hr(),
                                html.P("B5. Conveyance/wheeling agreements (ditches/canals/pipelines)"),
                                _radio(
                                    "legal-src-conveyance",
                                    ["Available", "Negotiable", "Unavailable (Prohibited)"],
                                    "Available",
                                ),
                            ],
                        ),

                        # C) Water quality feasibility
                        _section_card(
                            "C) Water Quality Feasibility (UIC, Anti-degradation, Standards)",
                            [
                                html.P("C1. Recharge method"),
                                dcc.Dropdown(
                                    id="legal-qual-method",
                                    options=[
                                        {"label": "Infiltration (basins/galleries)", "value": "infiltration"},
                                        {"label": "Direct Injection (wells)", "value": "injection"},
                                        {"label": "Both / To be determined", "value": "both"},
                                    ],
                                    value="infiltration",
                                    clearable=False,
                                    style={"maxWidth": "420px"},
                                ),
                                html.Br(),
                                html.P("C2. UIC (Underground Injection Control) Class V (SDWA (Safe Drinking Water Act)) or equivalent permit feasibility"),
                                _radio(
                                    "legal-qual-uic",
                                    ["Not applicable", "Feasible", "Not feasible (Prohibited)"],
                                    "Not applicable",
                                ),
                                html.Hr(),
                                html.P("C3. Receiving aquifer a USDW (Underground Source of Drinking Water) or planned potable use?"),
                                _radio(
                                    "legal-qual-usdw",
                                    ["No", "Yes - MCLs/no endangerment apply"],
                                    "No",
                                ),
                                html.Br(),
                                html.P("C4. Ability to meet SDWA (Safe Drinking Water Act) MCLs (Maximum Contaminant Levels)/no-endangerment and state reuse criteria (if applicable)"),
                                _radio(
                                    "legal-qual-mcls",
                                    ["Assured", "Achievable with treatment/monitoring", "Cannot be met (Prohibited)"],
                                    "Assured",
                                ),
                                html.Hr(),
                                html.P("C5. Anti-degradation/TMDL (Total Maximum Daily Load) compliance"),
                                _radio(
                                    "legal-qual-antideg",
                                    ["No lowering", "Lowering justified with mitigation", "Likely with studies", "Not compliant (Prohibited)"],
                                    "No lowering",
                                ),
                                html.Hr(),
                                html.P("C6. Geochemical compatibility (mobilization/precipitation risks)"),
                                _radio(
                                    "legal-qual-compat",
                                    ["Acceptable", "Mitigable with treatment/modeling", "Not acceptable (Prohibited)"],
                                    "Acceptable",
                                ),
                                html.Hr(),
                                html.P("C7. CECs (Constituents of Emerging Concern)/PFAS (Per- and Polyfluoroalkyl Substances) and monitoring orders compliance"),
                                _radio(
                                    "legal-qual-cecs",
                                    ["Compliant", "Compliant with advanced treatment", "Not compliant (Prohibited)"],
                                    "Compliant",
                                ),
                                html.Hr(),
                                html.P("C8. Residuals handling (backwash/brine) permitting"),
                                _radio(
                                    "legal-qual-residuals",
                                    ["Permittable", "Permittable with conditions", "Not permittable (Prohibited)"],
                                    "Permittable",
                                ),
                                html.Hr(),
                                html.P("C9. Well construction & monitoring plan (state standards/UIC)"),
                                _radio(
                                    "legal-qual-wells",
                                    ["Compliant", "Compliant with conditions", "Noncompliant (Prohibited)"],
                                    "Compliant",
                                ),
                            ],
                        ),
                    ],
                    width=12,
                    lg=8,
                    style={
                        "max-height": "calc(100vh - 200px)",
                        "overflow-y": "auto",
                        "overflow-x": "hidden",
                        "padding-right": "10px",
                    },
                ),

                # Right: Outputs
                dbc.Col(
                    [
                        html.H3("Legal/Regulatory Decision", className="mb-4 text-danger"),
                        html.Div(id="legal-final-decision-output", className="mb-4"),

                        html.H4("Regulatory Risk Score", className="mt-4 mb-3 text-info"),
                        dcc.Graph(
                            id="legal-risk-gauge",
                            config={"displayModeBar": False, "responsive": True},
                            style={"height": "250px", "width": "100%", "minHeight": "250px"},
                        ),
                        html.Div(id="legal-risk-details-output", className="alert alert-light border"),

                        html.Hr(),
                        html.H4("Branch Results", className="mt-4 mb-3 text-secondary"),
                        _section_card("A) Site Branch Result", [html.Div(id="legal-branch-site-output")]),
                        _section_card("B) Water Source Branch Result", [html.Div(id="legal-branch-source-output")]),
                        _section_card("C) Water Quality Branch Result", [html.Div(id="legal-branch-quality-output")]),

                        html.Hr(),
                        html.H4("Required Permits & Approvals (Checklist)", className="mt-4 mb-3 text-secondary"),
                        html.Ul(id="legal-required-permits-list", className="list-group"),
                    ],
                    width=12,
                    lg=4,
                    style={"position": "sticky", "top": "20px", "align-self": "start"},
                ),
            ]
        ),
        dbc.Tooltip(
            "Source-water category for applying source-specific regulatory pathways",
            target="legal-src-type",
            placement="top",
        ),
        dbc.Tooltip(
            "Primary MAR delivery mechanism affecting UIC and construction rules",
            target="legal-qual-method",
            placement="top",
        ),
        dbc.Tooltip(
            "Summary regulatory risk index from your feasibility questionnaire",
            target="legal-risk-gauge",
            placement="top",
        ),
    ]


def create_ai_powered_feasibility_content():
    """Create the AI-Powered Feasibility content (sub-tab 2)."""
    return [
        dbc.Card([
            dbc.CardHeader("AI-Powered Regulatory Feasibility Analysis", className="fw-bold bg-info text-white"),
            dbc.CardBody([
                html.H5("AI-Powered Feasibility Assessment", className="mb-4 text-primary"),
                html.P(
                    "This AI-powered tool will analyze your project details and provide comprehensive regulatory feasibility assessment. "
                    "Enter project information below to generate an AI-powered analysis.",
                    className="text-muted mb-4"
                ),
                html.Div([
                    html.P("AI-powered feasibility analysis coming soon...", className="text-center text-muted")
                ])
            ])
        ])
    ]


def create_legal_constraints_content():
    """Create the Legal Constraints tab content with sub-tabs."""
    return [
        dbc.Tabs([
            dbc.Tab(
                label="(1) Basic Regulation Feasibility",
                tab_id="basic-regulation-tab",
                children=create_basic_regulation_feasibility_content()
            ),
            dbc.Tab(
                label="(2) AI-Powered Feasibility",
                tab_id="ai-powered-feasibility-tab",
                children=create_ai_powered_feasibility_content()
            )
        ], id="legal-subtabs", active_tab="basic-regulation-tab")
    ]
