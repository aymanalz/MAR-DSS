"""
Engineering Options tab component.
"""

import dash_bootstrap_components as dbc
from dash import html, dcc
import mar_dss.app.utils.data_storage as dash_storage


def create_engineering_elements_content():
    """Create the Engineering Elements sub-tab content."""
    return [
        dbc.Row(
            [
                dbc.Col(
                    [
                        dbc.Card(
                            [
                                dbc.CardBody(
                                    [
                                        html.H4("Design Metrics"),
                                        html.P(
                                            "Choose Method for Hydrologic "
                                            "Design Parameters:",
                                            className="mt-3 mb-2"
                                        ),
                                        dbc.RadioItems(
                                            options=[
                                                {
                                                    "label": "User Supplied "
                                                    "Parameters",
                                                    "value": "user_supplied"
                                                },
                                                {
                                                    "label": "Import from "
                                                    "Runoff Calculation Tab",
                                                    "value": "import_runoff"
                                                }
                                            ],
                                            value="user_supplied",
                                            id="hydrologic-design-method-radio",
                                        ),
                                        html.Label(
                                            "Peak Flow Available for "
                                            "Recharge (gpm):",
                                            className="form-label mt-3"
                                        ),
                                        dbc.Input(
                                            type="number",
                                            value=0.0,
                                            id="peak-flow-available-input",
                                            min=0,
                                            step=0.1,
                                            className="mb-2"
                                        ),
                                        html.Label(
                                            "Fraction of Flow to Capture:",
                                            className="form-label"
                                        ),
                                        dbc.Input(
                                            type="number",
                                            value=0.0,
                                            id="fraction-flow-capture-input",
                                            min=0,
                                            max=1,
                                            step=0.01,
                                            className="mb-2"
                                        ),
                                        html.Div(
                                            id="design-flow-rate-display",
                                            children="Design Flow Rate is: 0.0",
                                            className="mt-2 mb-2",
                                            style={
                                                "font-weight": "bold",
                                                "font-size": "16px",
                                                "color": "#2c3e50"
                                            }
                                        ),
                                    ]
                                ),
                            ],
                            className="mb-4",
                        ),
                        dbc.Card(
                            [
                                dbc.CardBody(
                                    [
                                        html.H4("Flow Capture"),
                                        dbc.Checklist(
                                            options=[
                                                {
                                                    "label": "Flow Capture "
                                                    "Structure",
                                                    "value": "flow_capture_structure"
                                                },
                                                {
                                                    "label": "Pump is used to "
                                                    "divert water",
                                                    "value": "pump_used"
                                                },
                                                {
                                                    "label": "Rough Grading/"
                                                    "Grubbing in Field",
                                                    "value": "rough_grading"
                                                }
                                            ],
                                            value=[
                                                "flow_capture_structure",
                                                "rough_grading"
                                            ],
                                            id="flow-capture-pump-check",
                                            switch=True,
                                        ),
                                    ]
                                ),
                            ],
                            className="mb-4",
                        ),
                        dbc.Card(
                            [
                                dbc.CardBody(
                                    [
                                        html.H4("Conveyance To Sediment Pond"),
                                        html.Label(
                                            "Choose conveyance Method.",
                                            className="form-label"
                                        ),
                                        dbc.RadioItems(
                                            options=[
                                                {
                                                    "label": "Trapezoidal Channel",
                                                    "value": "trapezoidal"
                                                },
                                                {
                                                    "label": "Gravity Conveyance "
                                                    "Pipeline",
                                                    "value": "pipeline"
                                                },
                                                {
                                                    "label": "Pumped Conveyance",
                                                    "value": "pumped"
                                                }
                                            ],
                                            value="trapezoidal",
                                            id="conveyance-method-radio",
                                        ),
                                        html.Label(
                                            "Distance from Collection Point to "
                                            "Sediment Removal Pond (miles):",
                                            className="form-label mt-3"
                                        ),
                                        dbc.Input(
                                            type="number",
                                            value=1.0,
                                            id="distance-collection-to-sediment",
                                            min=0,
                                            step=0.1,
                                        ),
                                    ]
                                ),
                            ],
                            className="mb-4",
                        ),
                        dbc.Card(
                            [
                                dbc.CardBody(
                                    [
                                        html.H4("Sediment Removal Pond"),
                                        dbc.Checklist(
                                            options=[
                                                {
                                                    "label": "Trash Rack",
                                                    "value": "trash_rack"
                                                },
                                                {
                                                    "label": "Contech Filtration",
                                                    "value": "contech_filtration"
                                                }
                                            ],
                                            value=["trash_rack"],
                                            id="sediment-removal-pond-check",
                                            switch=True,
                                        ),
                                        html.Label(
                                            "Sediment Removal Target:",
                                            className="form-label mt-3"
                                        ),
                                        dbc.RadioItems(
                                            options=[
                                                {
                                                    "label": "Fine Silt",
                                                    "value": "fine_silt"
                                                },
                                                {
                                                    "label": "Medium Silt",
                                                    "value": "medium_silt"
                                                }
                                            ],
                                            value="medium_silt",
                                            id="sediment-removal-target-radio",
                                        ),
                                    ]
                                ),
                            ],
                            className="mb-4",
                        ),
                        dbc.Card(
                            [
                                dbc.CardBody(
                                    [
                                        html.H4("Pumped Conveyance To Storage Pond"),
                                        dbc.Checklist(
                                            options=[
                                                {
                                                    "label": "Pipeline Cost",
                                                    "value": "pipeline_cost"
                                                },
                                                {
                                                    "label": "Pumping and Bag Filter "
                                                    "Cost",
                                                    "value": "pumping_bag_filter_cost"
                                                },
                                                {
                                                    "label": "Controls",
                                                    "value": "controls"
                                                },
                                                {
                                                    "label": "Electrical System",
                                                    "value": "electrical_system"
                                                }
                                            ],
                                            value=[
                                                "pipeline_cost",
                                                "pumping_bag_filter_cost",
                                                "controls",
                                                "electrical_system"
                                            ],
                                            id="pumped-conveyance-storage-check",
                                            switch=True,
                                        ),
                                    ]
                                ),
                            ],
                            className="mb-4",
                        ),
                        dbc.Card(
                            [
                                dbc.CardBody(
                                    [
                                        html.H4("Storage Pond"),
                                        dbc.Checklist(
                                            options=[
                                                {
                                                    "label": "Storage Pond "
                                                    "Construction",
                                                    "value": "storage_pond_construction"
                                                }
                                            ],
                                            value=["storage_pond_construction"],
                                            id="storage-pond-check",
                                            switch=True,
                                        ),
                                    ]
                                ),
                            ],
                            className="mb-4",
                        ),
                        dbc.Card(
                            [
                                dbc.CardBody(
                                    [
                                        html.H4(
                                            "Pumped Conveyance To Infiltration "
                                            "Site"
                                        ),
                                        dbc.Checklist(
                                            options=[
                                                {
                                                    "label": "Pipeline Cost",
                                                    "value": "infiltration_pipeline_cost"
                                                },
                                                {
                                                    "label": "Pumping and Bag Filter "
                                                    "Cost",
                                                    "value": "infiltration_pumping_bag_filter_cost"
                                                },
                                                {
                                                    "label": "Controls",
                                                    "value": "infiltration_controls"
                                                },
                                                {
                                                    "label": "Electrical System",
                                                    "value": "infiltration_electrical_system"
                                                }
                                            ],
                                            value=[
                                                "infiltration_pipeline_cost",
                                                "infiltration_pumping_bag_filter_cost",
                                                "infiltration_controls",
                                                "infiltration_electrical_system"
                                            ],
                                            id="pumped-conveyance-infiltration-check",
                                            switch=True,
                                        ),
                                    ]
                                ),
                            ],
                            className="mb-4",
                        ),
                        dbc.Card(
                            [
                                dbc.CardBody(
                                    [
                                        html.H4("Infiltration Method"),
                                        dbc.RadioItems(
                                            options=[
                                                {
                                                    "label": "Dry Wells",
                                                    "value": "dry_wells"
                                                },
                                                {
                                                    "label": "Injection Wells",
                                                    "value": "injection_wells"
                                                },
                                                {
                                                    "label": "Infiltration Basin",
                                                    "value": "infiltration_basin"
                                                }
                                            ],
                                            value="infiltration_basin",
                                            id="infiltration-method-radio",
                                        ),
                                    ]
                                ),
                            ],
                            className="mb-4",
                        ),
                    ],
                    width=8,
                ),
                dbc.Col(
                    [
                        dbc.Card(
                            [
                                dbc.CardBody(
                                    [
                                        html.Img(
                                            src="assets/Engineering.jpg",
                                            alt="Engineering",
                                            style={
                                                "width": "100%",
                                                "height": "auto",
                                                "display": "block"
                                            }
                                        ),
                                    ]
                                ),
                            ],
                            className="mb-4",
                            style={
                                "height": "100%",
                                "display": "flex",
                                "flex-direction": "column"
                            }
                        )
                    ],
                    width=4,
                ),
            ],
            className="mb-4",
        )
    ]


def create_cost_content():
    """Create the Cost sub-tab content."""
    return [
        dbc.Card(
            [
                dbc.CardBody(
                    [
                        html.H4("Cost Summary"),
                    ]
                ),
            ],
            className="mb-4",
        ),
        dbc.Row(
            [
                dbc.Col(
                    [
                        dbc.Card(
                            [
                                dbc.CardBody(
                                    [
                                        html.H5(
                                            "Capital Cost",
                                            className="text-center mb-3"
                                        ),
                                        html.H2(
                                            "$0",
                                            className="text-center",
                                            id="capital-cost-display",
                                            style={
                                                "font-size": "2.5rem",
                                                "font-weight": "bold",
                                                "color": "#2c3e50"
                                            }
                                        ),
                                    ]
                                ),
                            ],
                            className="mb-4 text-center",
                        )
                    ],
                    width=4,
                ),
                dbc.Col(
                    [
                        dbc.Card(
                            [
                                dbc.CardBody(
                                    [
                                        html.H5(
                                            "Annual Maintenance Cost",
                                            className="text-center mb-3"
                                        ),
                                        html.H2(
                                            "$0",
                                            className="text-center",
                                            id="annual-maintenance-cost-display",
                                            style={
                                                "font-size": "2.5rem",
                                                "font-weight": "bold",
                                                "color": "#2c3e50"
                                            }
                                        ),
                                    ]
                                ),
                            ],
                            className="mb-4 text-center",
                        )
                    ],
                    width=4,
                ),
                dbc.Col(
                    [
                        dbc.Card(
                            [
                                dbc.CardBody(
                                    [
                                        html.H5(
                                            "Net Present Value After 20 Years",
                                            className="text-center mb-3"
                                        ),
                                        html.H2(
                                            "$0",
                                            className="text-center",
                                            id="npv-20-years-display",
                                            style={
                                                "font-size": "2.5rem",
                                                "font-weight": "bold",
                                                "color": "#2c3e50"
                                            }
                                        ),
                                    ]
                                ),
                            ],
                            className="mb-4 text-center",
                        )
                    ],
                    width=4,
                ),
            ],
            className="mb-4",
        ),
        dbc.Tabs(
            [
                dbc.Tab(
                    label="Capital Cost Table",
                    tab_id="capital-cost-table-tab",
                    children=[
                        dbc.Card(
                            [
                                dbc.CardBody(
                                    [
                                        html.P(
                                            "Capital Cost Table will be displayed "
                                            "here.",
                                            id="capital-cost-table-content"
                                        ),
                                    ]
                                ),
                            ],
                            className="mb-4",
                        )
                    ]
                ),
                dbc.Tab(
                    label="Maintenance Cost Table",
                    tab_id="maintenance-cost-table-tab",
                    children=[
                        dbc.Card(
                            [
                                dbc.CardBody(
                                    [
                                        html.P(
                                            "Maintenance Cost Table will be "
                                            "displayed here.",
                                            id="maintenance-cost-table-content"
                                        ),
                                    ]
                                ),
                            ],
                            className="mb-4",
                        )
                    ]
                ),
                dbc.Tab(
                    label="Net Present Value Table",
                    tab_id="npv-table-tab",
                    children=[
                        dbc.Card(
                            [
                                dbc.CardBody(
                                    [
                                        html.P(
                                            "Net Present Value Table will be "
                                            "displayed here.",
                                            id="npv-table-content"
                                        ),
                                    ]
                                ),
                            ],
                            className="mb-4",
                        )
                    ]
                ),
            ],
            id="cost-tables-tabs",
            active_tab="capital-cost-table-tab"
        )
    ]


def create_engineering_options_content():
    """Create the Engineering Options tab content."""
    return create_engineering_elements_content()

