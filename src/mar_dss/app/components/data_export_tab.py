"""
Data Export tab content for MAR DSS dashboard.
"""

import dash_bootstrap_components as dbc
from dash import html


def create_data_export_content():
    """Create content for Data Export sidebar tab."""
    return html.Div(
        [
            html.H3("Data Export"),
            html.P("Export analysis results and data."),
            dbc.Card(
                [
                    dbc.CardBody(
                        [
                            html.H5("Export Options"),
                            dbc.Row(
                                [
                                    dbc.Col(
                                        [
                                            dbc.Button(
                                                "Export CSV",
                                                id="export-csv-btn",
                                                color="primary",
                                                className="mb-2",
                                                title="Export tabular results as comma-separated values",
                                            ),
                                            dbc.Button(
                                                "Export Excel",
                                                id="export-excel-btn",
                                                color="success",
                                                className="mb-2",
                                                title="Export results as a spreadsheet workbook",
                                            ),
                                            dbc.Button(
                                                "Export PDF",
                                                id="export-pdf-btn",
                                                color="warning",
                                                className="mb-2",
                                                title="Export a printable PDF summary",
                                            ),
                                        ],
                                        width=6,
                                    ),
                                    dbc.Col(
                                        [
                                            html.P("Select data range:"),
                                            dbc.Select(
                                                id="export-date-range-select",
                                                options=[
                                                    {
                                                        "label": "Last 7 days",
                                                        "value": "7days",
                                                    },
                                                    {
                                                        "label": "Last 30 days",
                                                        "value": "30days",
                                                    },
                                                    {
                                                        "label": "Last 90 days",
                                                        "value": "90days",
                                                    },
                                                    {
                                                        "label": "All data",
                                                        "value": "all",
                                                    },
                                                ],
                                                value="30days",
                                            ),
                                        ],
                                        width=6,
                                    ),
                                ]
                            ),
                            dbc.Tooltip(
                                "Time window included in the export file",
                                target="export-date-range-select",
                                placement="top",
                            ),
                        ]
                    )
                ]
            ),
        ]
    )


