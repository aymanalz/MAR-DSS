"""
Callbacks for Legal Constraints tab - MAR legal/regulatory feasibility.
"""

from dash import Input, Output, html
import plotly.graph_objects as go
import mar_dss.app.utils.data_storage as data_storage


def _classify_branch(statuses):
    """Classify a branch result from a list of statuses: 'ok' | 'cond' | 'fatal'."""
    if any(s == "fatal" for s in statuses):
        return "Not feasible", "danger"
    if any(s == "cond" for s in statuses):
        return "Conditionally feasible", "warning"
    return "Feasible", "success"


def _status_from_choice(choice, fatal_mark="Prohibited", cond_mark="with"):
    """
    Map a textual choice to status:
    - if contains fatal_mark => 'fatal'
    - elif contains cond_mark or common conditional words => 'cond'
    - else => 'ok'
    """
    text = (choice or "").lower()
    if fatal_mark.lower() in text or "unobtainable" in text or "noncompliant" in text or "not feasible" in text or "not approvable" in text or "unmitigable" in text or "no path" in text or "unavailable" in text:
        return "fatal"
    if "condition" in text or cond_mark in text or "authorizable" in text or "negotiable" in text or "likely" in text or "achievable" in text or "mitigable" in text:
        return "cond"
    return "ok"


def _required_permits(federal_nexus, wetlands, public_lands, method, uic_choice, residuals_choice, compact, src_right, accounting):
    """Heuristically build a permit/approval checklist from inputs."""
    req = []

    # Federal nexus → NEPA/ESA/NHPA/CZMA (if coastal)
    if (federal_nexus or "").startswith("Yes"):
        req.append("NEPA (National Environmental Policy Act) - if federal nexus")
        req.append("ESA (Endangered Species Act) Section 7 consultation - if listed species/critical habitat")
        req.append("NHPA (National Historic Preservation Act) Section 106 - cultural/historic resources")

    # Wetlands/Waters impacts
    if wetlands in ["General permit likely", "Individual permit feasible", "Permit unlikely (Prohibited)"]:
        req.append("CWA (Clean Water Act) §§404/401 - USACE (U.S. Army Corps of Engineers) permit + state certification")

    # Public lands/federal facilities
    if public_lands in ["Authorizations obtainable", "Authorizations unobtainable (Prohibited)"]:
        req.append("ROW/Special-Use Authorization - BLM (Bureau of Land Management) / USFS (U.S. Forest Service) / BOR (Bureau of Reclamation) / NPS (National Park Service)")

    # Injection wells
    if method in ["injection", "both"] or uic_choice in ["Feasible", "Not feasible (Prohibited)"]:
        req.append("SDWA (Safe Drinking Water Act) UIC (Underground Injection Control) Class V (state/EPA)")

    # Residuals handling often → NPDES/pretreatment/land disposal
    if residuals_choice in ["Permittable", "Permittable with conditions", "Not permittable (Prohibited)"]:
        req.append("CWA (Clean Water Act) §402 NPDES (National Pollutant Discharge Elimination System) / Pretreatment / Land disposal authorization")

    # Interstate compact
    if compact in ["Compliant", "Noncompliant (Prohibited)"]:
        req.append("Interstate compact delivery/accounting compliance (as applicable)")

    # State-level water rights & MAR accounting
    if src_right in ["Valid right/contract", "Obtainable without injury", "No path to a valid right (Prohibited)"]:
        req.append("State water right/contract and storage/recharge authorization for MAR (Managed Aquifer Recharge)")
    if accounting in ["Authorized", "Authorizable with conditions", "No statutory/administrative pathway (Prohibited)"]:
        req.append("State MAR (Managed Aquifer Recharge)/ASR (Aquifer Storage and Recovery) accounting and recovery approval")

    # Deduplicate preserving order
    seen = set()
    out = []
    for item in req:
        if item not in seen:
            out.append(item)
            seen.add(item)
    return out


def setup_legal_constraints_callbacks(app):
    """Set up callbacks for the Legal Constraints tab."""

    @app.callback(
        [
            Output("legal-final-decision-output", "children"),
            Output("legal-final-decision-output", "style"),
            Output("legal-risk-gauge", "figure"),
            Output("legal-risk-details-output", "children"),
            Output("legal-branch-site-output", "children"),
            Output("legal-branch-source-output", "children"),
            Output("legal-branch-quality-output", "children"),
            Output("legal-required-permits-list", "children"),
        ],
        [
            # Project/Jurisdiction
            Input("legal-proj-federal-nexus", "value"),
            Input("legal-proj-tribal-interstate", "value"),
            # A) Site
            Input("legal-site-control", "value"),
            Input("legal-site-zoning", "value"),
            Input("legal-site-wetlands", "value"),
            Input("legal-site-sensitive", "value"),
            Input("legal-site-public-lands", "value"),
            Input("legal-site-dams", "value"),
            Input("legal-site-seismic", "value"),
            # B) Source
            Input("legal-src-right", "value"),
            Input("legal-src-accounting", "value"),
            Input("legal-src-compact", "value"),
            Input("legal-src-type", "value"),
            Input("legal-src-type-feasible", "value"),
            Input("legal-src-conveyance", "value"),
            # C) Quality
            Input("legal-qual-method", "value"),
            Input("legal-qual-uic", "value"),
            Input("legal-qual-usdw", "value"),
            Input("legal-qual-mcls", "value"),
            Input("legal-qual-antideg", "value"),
            Input("legal-qual-compat", "value"),
            Input("legal-qual-cecs", "value"),
            Input("legal-qual-residuals", "value"),
            Input("legal-qual-wells", "value"),
        ],
    )
    def evaluate_legal_feasibility(
        federal_nexus,
        tribal_interstate,
        a_control,
        a_zoning,
        a_wetlands,
        a_sensitive,
        a_public,
        a_dams,
        a_seismic,
        b_right,
        b_account,
        b_compact,
        b_src_type,
        b_src_feasible,
        b_convey,
        c_method,
        c_uic,
        c_usdw,
        c_mcls,
        c_antideg,
        c_compat,
        c_cecs,
        c_residuals,
        c_wells,
    ):
        # 1) Map choices to statuses for each branch
        site_statuses = [
            _status_from_choice(a_control),
            _status_from_choice(a_zoning),
            _status_from_choice(a_wetlands),
            _status_from_choice(a_sensitive),
            _status_from_choice(a_public),
            _status_from_choice(a_dams),
            _status_from_choice(a_seismic),
        ]

        source_statuses = [
            _status_from_choice(b_right),
            _status_from_choice(b_account),
            _status_from_choice(b_compact),
            _status_from_choice(b_src_feasible),
            _status_from_choice(b_convey),
        ]

        quality_statuses = [
            _status_from_choice(c_uic),
            _status_from_choice(c_mcls),
            _status_from_choice(c_antideg),
            _status_from_choice(c_compat),
            _status_from_choice(c_cecs),
            _status_from_choice(c_residuals),
            _status_from_choice(c_wells),
        ]

        # 2) Classify each branch
        site_result, site_color = _classify_branch(site_statuses)
        source_result, source_color = _classify_branch(source_statuses)
        quality_result, quality_color = _classify_branch(quality_statuses)

        # 3) Aggregate overall decision
        any_fatal = any(s == "fatal" for s in site_statuses + source_statuses + quality_statuses)
        num_conditional = sum(1 for s in site_statuses + source_statuses + quality_statuses if s == "cond")

        # Project/Jurisdiction overlays add conditional weight
        proj_conditional = 0
        if (federal_nexus or "").startswith("Yes"):
            proj_conditional += 1
        if tribal_interstate in ["Tribal lands/resources", "Interstate compact", "Both"]:
            proj_conditional += 1

        # Risk score heuristic
        risk_score = (5 if any_fatal else 0) + num_conditional + proj_conditional

        if any_fatal:
            final_color = "#dc3545"
            final_text = "The MAR project is NOT FEASIBLE due to one or more prohibitions."
        elif num_conditional + proj_conditional > 0:
            final_color = "#ffc107"
            final_text = "The MAR project is CONDITIONALLY FEASIBLE subject to permits/mitigations."
        else:
            final_color = "#28a745"
            final_text = "The MAR project is FEASIBLE with standard approvals."

        final_style = {
            "padding": "20px",
            "border-radius": "8px",
            "color": "#ffffff" if final_color != "#ffc107" else "#343a40",
            "background-color": final_color,
            "text-align": "left",
        }

        decision_children = [
            html.P(final_text, className="lead fw-bold mb-2"),
            html.Ul(
                [
                    html.Li(["A) Site: ", html.Strong(site_result)], className="mb-1"),
                    html.Li(["B) Water Source: ", html.Strong(source_result)], className="mb-1"),
                    html.Li(["C) Water Quality: ", html.Strong(quality_result)], className="mb-0"),
                ],
                className="mb-0",
            ),
        ]

        # 4) Gauge figure
        gauge = go.Figure(
            go.Indicator(
                mode="gauge+number",
                value=min(risk_score, 10),
                domain={"x": [0, 1], "y": [0, 1]},
                title={"text": "Regulatory Risk Score", "font": {"size": 20}},
                gauge={
                    "axis": {"range": [0, 10], "tickwidth": 1, "tickcolor": "darkblue"},
                    "bar": {"color": "darkslategray"},
                    "bgcolor": "white",
                    "borderwidth": 2,
                    "bordercolor": "gray",
                    "steps": [
                        {"range": [0, 2], "color": "lightgreen"},
                        {"range": [3, 7], "color": "yellow"},
                        {"range": [8, 10], "color": "red"},
                    ],
                    "threshold": {"line": {"color": "red", "width": 4}, "thickness": 0.75, "value": min(risk_score, 10)},
                },
            )
        )
        gauge.update_layout(
            margin=dict(l=10, r=10, t=50, b=10),
            height=250,
            autosize=True,
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
        )

        # 5) Risk details list (include acronym expansions in labels)
        def _detail_item(label, choice, status):
            color_map = {"ok": ("#d4edda", "#155724"), "cond": ("#fff3cd", "#856404"), "fatal": ("#f8d7da", "#721c24")}
            bg, fg = color_map.get(status, ("#f8f9fa", "#000000"))
            return html.Div(
                [
                    html.Span(f"{label}: {choice or '-'}", className="fw-bold"),
                    html.Span(
                        f" - {status.upper()}",
                        className="float-end badge",
                        style={"backgroundColor": fg, "color": "white"},
                    ),
                ],
                className="d-flex justify-content-between mb-1 p-2 rounded",
                style={"background-color": bg, "color": fg, "border-left": f"4px solid {fg}"},
            )

        details = []
        # Project/Jurisdiction
        details.append(_detail_item("Federal nexus", federal_nexus, "cond" if (federal_nexus or "").startswith("Yes") else "ok"))
        details.append(_detail_item("Tribal/interstate", tribal_interstate, "cond" if tribal_interstate != "None" else "ok"))
        # A) Site
        site_labels = [
            ("Site control", a_control, site_statuses[0]),
            ("Zoning/local approvals", a_zoning, site_statuses[1]),
            ("Waters/wetlands (CWA (Clean Water Act) §§404/401; RHA (Rivers and Harbors Act) §10)", a_wetlands, site_statuses[2]),
            ("Sensitive resources", a_sensitive, site_statuses[3]),
            ("Public lands/federal facilities", a_public, site_statuses[4]),
            ("Dam safety", a_dams, site_statuses[5]),
            ("Subsidence/seismic", a_seismic, site_statuses[6]),
        ]
        details.extend([_detail_item(lbl, ch, st) for (lbl, ch, st) in site_labels])

        # B) Source
        source_labels = [
            ("Water right/contract", b_right, source_statuses[0]),
            ("Recharge accounting/recovery (MAR/ASR)", b_account, source_statuses[1]),
            ("Interstate compact", b_compact, source_statuses[2]),
            ("Source-specific compliance", b_src_feasible, source_statuses[3]),
            ("Conveyance/wheeling", b_convey, source_statuses[4]),
        ]
        details.extend([_detail_item(lbl, ch, st) for (lbl, ch, st) in source_labels])

        # C) Quality
        quality_labels = [
            ("UIC (Underground Injection Control) Class V (SDWA)", c_uic, quality_statuses[0]),
            ("MCLs (Maximum Contaminant Levels)/no-endangerment/reuse", c_mcls, quality_statuses[1]),
            ("Anti-degradation/TMDLs (Total Maximum Daily Loads)", c_antideg, quality_statuses[2]),
            ("Geochemical compatibility", c_compat, quality_statuses[3]),
            ("CECs (Constituents of Emerging Concern)/PFAS (Per- and Polyfluoroalkyl Substances) compliance", c_cecs, quality_statuses[4]),
            ("Residuals handling permits", c_residuals, quality_statuses[5]),
            ("Well construction/monitoring", c_wells, quality_statuses[6]),
        ]
        details.extend([_detail_item(lbl, ch, st) for (lbl, ch, st) in quality_labels])

        # 6) Branch result badges
        def _branch_badge(text, color):
            return html.Div(
                [
                    html.Span(text),
                    html.Span(className=f"badge bg-{color} ms-2", children=text),
                ]
            )

        site_branch = html.Div(
            [
                html.P(["Site Branch Result: ", html.Strong(site_result)], className="mb-2"),
                html.Small("Outcome derived from A1–A7 inputs."),
            ]
        )
        source_branch = html.Div(
            [
                html.P(["Water Source Branch Result: ", html.Strong(source_result)], className="mb-2"),
                html.Small("Outcome derived from B1–B5 inputs."),
            ]
        )
        quality_branch = html.Div(
            [
                html.P(["Water Quality Branch Result: ", html.Strong(quality_result)], className="mb-2"),
                html.Small("Outcome derived from C1–C9 inputs."),
            ]
        )

        # 7) Required permits list
        permits = _required_permits(
            federal_nexus=federal_nexus,
            wetlands=a_wetlands,
            public_lands=a_public,
            method=c_method,
            uic_choice=c_uic,
            residuals_choice=c_residuals,
            compact=b_compact,
            src_right=b_right,
            accounting=b_account,
        )
        permits_list = [html.Li(p, className="list-group-item") for p in permits] or [
            html.Li("No specific permits inferred. Verify state/local requirements.", className="list-group-item list-group-item-light")
        ]

        # Store regulation data in data_storage for soft constraints evaluation
        regulation_data = {
            "group_0": {
                "federal_nexus": federal_nexus,
                "tribal_interstate": tribal_interstate,
            },
            "group_a": {
                "site_control": a_control,
                "zoning": a_zoning,
                "wetlands": a_wetlands,
                "sensitive": a_sensitive,
                "public_lands": a_public,
                "dams": a_dams,
                "seismic": a_seismic,
            },
            "group_b": {
                "right": b_right,
                "accounting": b_account,
                "compact": b_compact,
                "src_type": b_src_type,
                "src_feasible": b_src_feasible,
                "conveyance": b_convey,
            },
            "group_c": {
                "method": c_method,
                "uic": c_uic,
                "usdw": c_usdw,
                "mcls": c_mcls,
                "antideg": c_antideg,
                "compat": c_compat,
                "cecs": c_cecs,
                "residuals": c_residuals,
                "wells": c_wells,
            },
        }
        data_storage.set_data("regulation_data", regulation_data)

        return (
            decision_children,
            final_style,
            gauge,
            details,
            site_branch,
            source_branch,
            quality_branch,
            permits_list,
        )


