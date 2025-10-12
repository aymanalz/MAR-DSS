"""
Main dashboard application for MAR DSS.
"""

from datetime import datetime

import dash
import dash_bootstrap_components as dbc
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from dash import Input, Output, dcc, html
import mar_dss.app.utils.data_storage as dash_storage

dash_storage.set_data('test', 1)
try:
    # Try absolute imports first (when run as module)
    from mar_dss.app.components.ai_generated_decision_tab import (
        create_ai_generated_decision_content,
    )
    from mar_dss.app.components.dashboard_tab import create_dashboard_content
    from mar_dss.app.components.data_export_tab import (
        create_data_export_content,
    )
    from mar_dss.app.components.decision_interpretation_tab import (
        create_decision_interpretation_content,
    )
    from mar_dss.app.components.decision_sensitivity_tab import (
        create_decision_sensitivity_content,
    )
    from mar_dss.app.components.dss_algorithm_tab import (
        create_dss_algorithm_content,
    )
    from mar_dss.app.components.hydro_tab import create_hydro_tab_content
    from mar_dss.app.callbacks.hydro_callbacks import setup_hydro_callbacks
    from mar_dss.app.components.reports_tab import create_reports_tab_content
    from mar_dss.app.components.scenarios_comparison_tab import (
        create_scenarios_comparison_content,
    )
    from mar_dss.app.components.water_source_tab import (
        create_general_tab_content,
    )
except ImportError:
    # Fallback to relative imports (when run directly)
    from .components.ai_generated_decision_tab import (
        create_ai_generated_decision_content,
    )
    from .components.dashboard_tab import create_dashboard_content
    from .components.data_export_tab import create_data_export_content
    from .components.decision_interpretation_tab import (
        create_decision_interpretation_content,
    )
    from .components.decision_sensitivity_tab import (
        create_decision_sensitivity_content,
    )
    from .components.dss_algorithm_tab import create_dss_algorithm_content
    from .components.hydro_tab import create_hydro_tab_content
    from .components.reports_tab import create_reports_tab_content
    from .components.scenarios_comparison_tab import (
        create_scenarios_comparison_content,
    )
    from .components.water_source_tab import create_general_tab_content


class DashboardApp:
    """Main dashboard application class."""

    def __init__(self):
        """Initialize the dashboard application."""
        # 
        self.app = dash.Dash(
            __name__,
            external_stylesheets=[
                "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css"
            ],
            suppress_callback_exceptions=True,
            assets_folder="assets",
        )
        self.current_theme = "CERULEAN"
        self.setup_layout()
        self.setup_callbacks()
        
        # Set up hydrogeology callbacks
        setup_hydro_callbacks(self.app)

    def create_sample_data(self):
        """Create sample data for demonstration."""
        # Generate sample time series data
        dates = pd.date_range(start="2023-01-01", end="2023-12-31", freq="D")

        # Water level data
        water_levels = np.random.normal(100, 10, len(dates)) + 5 * np.sin(
            np.arange(len(dates)) * 2 * np.pi / 365
        )

        # Recharge data
        recharge_data = np.random.exponential(2, len(dates)) * (
            1 + 0.5 * np.sin(np.arange(len(dates)) * 2 * np.pi / 365)
        )

        # Quality data
        quality_data = np.random.normal(7.5, 0.5, len(dates))

        return {
            "dates": dates,
            "water_levels": water_levels,
            "recharge_data": recharge_data,
            "quality_data": quality_data,
        }

    def create_water_level_chart(self, data):
        """Create water level time series chart."""
        fig = go.Figure()
        fig.add_trace(
            go.Scatter(
                x=data["dates"],
                y=data["water_levels"],
                mode="lines+markers",
                name="Water Level",
                line=dict(color="#1f77b4", width=2),
                marker=dict(size=4),
            )
        )

        fig.update_layout(
            title="Water Level Over Time",
            xaxis_title="Date",
            yaxis_title="Water Level (m)",
            hovermode="x unified",
            template="plotly_white",
        )

        return fig

    def create_recharge_chart(self, data):
        """Create recharge rate chart."""
        fig = go.Figure()
        fig.add_trace(
            go.Bar(
                x=data["dates"],
                y=data["recharge_data"],
                name="Recharge Rate",
                marker_color="#2ca02c",
            )
        )

        fig.update_layout(
            title="Recharge Rate Over Time",
            xaxis_title="Date",
            yaxis_title="Recharge Rate (mm/day)",
            template="plotly_white",
        )

        return fig

    def create_quality_chart(self, data):
        """Create water quality chart."""
        fig = go.Figure()
        fig.add_trace(
            go.Scatter(
                x=data["dates"],
                y=data["quality_data"],
                mode="lines+markers",
                name="pH Level",
                line=dict(color="#ff7f0e", width=2),
                marker=dict(size=4),
            )
        )

        fig.update_layout(
            title="Water Quality (pH) Over Time",
            xaxis_title="Date",
            yaxis_title="pH Level",
            hovermode="x unified",
            template="plotly_white",
        )

        return fig

    def create_summary_cards(self, data):
        """Create summary cards for the dashboard."""
        current_level = data["water_levels"][-1]
        avg_recharge = np.mean(data["recharge_data"])
        current_quality = data["quality_data"][-1]

        cards = [
            dbc.Card(
                [
                    dbc.CardBody(
                        [
                            html.H4(
                                f"{current_level:.1f} m", className="card-title"
                            ),
                            html.P(
                                "Current Water Level", className="card-text"
                            ),
                            html.I(className="fas fa-tint fa-2x text-primary"),
                        ]
                    )
                ],
                className="text-center mb-3",
            ),
            dbc.Card(
                [
                    dbc.CardBody(
                        [
                            html.H4(
                                f"{avg_recharge:.2f} mm/day",
                                className="card-title",
                            ),
                            html.P(
                                "Average Recharge Rate", className="card-text"
                            ),
                            html.I(
                                className="fas fa-cloud-rain fa-2x text-success"
                            ),
                        ]
                    )
                ],
                className="text-center mb-3",
            ),
            dbc.Card(
                [
                    dbc.CardBody(
                        [
                            html.H4(
                                f"{current_quality:.2f}", className="card-title"
                            ),
                            html.P("Current pH Level", className="card-text"),
                            html.I(className="fas fa-flask fa-2x text-warning"),
                        ]
                    )
                ],
                className="text-center mb-3",
            ),
        ]

        return cards

    def create_mar_purpose_section(self):
        """Create MAR Project Purpose section for overview."""
        return dbc.Card(
            [
                dbc.CardHeader(
                    "MAR Project Purpose",
                    className="fw-bold bg-primary text-white",
                ),
                dbc.CardBody(
                    [
                        html.Label("Project Name:", className="fw-bold"),
                        dbc.Input(
                            id="project-name-input",
                            type="text",
                            placeholder="Enter your MAR project name...",
                            value="",
                            style={"margin-bottom": "15px"},
                        ),
                        html.Label("Analysis Date:", className="fw-bold"),
                        dbc.Input(
                            id="analysis-date-input",
                            type="date",
                            value=datetime.now().strftime("%Y-%m-%d"),
                            style={"margin-bottom": "15px"},
                        ),
                        html.Label("Project Location:", className="fw-bold"),
                        dbc.Input(
                            id="project-location-input",
                            type="text",
                            placeholder="Enter project location (e.g., Sacramento, CA)...",
                            value="",
                            style={"margin-bottom": "20px"},
                        ),
                        html.Label("MAR Project Purpose:", className="fw-bold"),
                        html.P(
                            "Select one or more purposes for your MAR project:",
                            className="text-muted small",
                        ),
                        dbc.Checklist(
                            id="mar-purpose-checklist",
                            options=[
                                {
                                    "label": "Secure Water Supply",
                                    "value": "secure_water_supply",
                                },
                                {
                                    "label": "Restore Depleted Aquifer Storage",
                                    "value": "restore_aquifer_storage",
                                },
                                {
                                    "label": "Reduce Flood Impact",
                                    "value": "reduce_flood_impact",
                                },
                                {
                                    "label": "Mitigate Seawater Intrusion",
                                    "value": "mitigate_seawater_intrusion",
                                },
                                {
                                    "label": "Improve Water Quality",
                                    "value": "improve_water_quality",
                                },
                            ],
                            value=["secure_water_supply"],  # Default selection
                            inline=False,
                            style={"margin-top": "10px"},
                        ),
                    ]
                ),
            ]
        )

    def create_location_map_section(self):
        """Create location map section for overview."""
        # Import the function from components.water_source_tab
        try:
            from mar_dss.app.components.water_source_tab import (
                create_location_map,
            )
        except ImportError:
            from .components.water_source_tab import create_location_map

        return dbc.Card(
            [
                dbc.CardHeader(
                    "Project Location - Sacramento, California, United States",
                    id="location-card-header",
                    className="fw-bold bg-primary text-white",
                ),
                dbc.CardBody(
                    [
                        dcc.Graph(
                            figure=create_location_map(),
                            config={"displayModeBar": True},
                            id="location-map",
                        )
                    ]
                ),
            ]
        )

    def setup_layout(self):
        """Set up the main dashboard layout by delegating to layout module."""
        # Import locally to avoid potential circular imports
        try:
            from mar_dss.app.components.layout import (
                setup_layout as _setup_layout,
            )
        except ImportError:
            from .components.layout import setup_layout as _setup_layout

        _setup_layout(self)

    def setup_callbacks(self):
        """Set up dashboard callbacks."""
        # Import and set up main callbacks
        try:
            from mar_dss.app.callbacks.main_callbacks import setup_main_callbacks
        except ImportError:
            from .callbacks.main_callbacks import setup_main_callbacks
        
        setup_main_callbacks(self.app, self)

    def get_theme_css(self, theme_name):
        """Get CSS for the selected theme."""
        theme_map = {
            "CERULEAN": dbc.themes.CERULEAN,
            "DARKLY": dbc.themes.DARKLY,
            "FLATLY": dbc.themes.FLATLY,
            "CYBORG": dbc.themes.CYBORG,
            "SLATE": dbc.themes.SLATE,
        }
        return theme_map.get(theme_name, dbc.themes.CERULEAN)

    def run(self, debug=True, port=8050, open_browser=True):
        """Run the dashboard application."""
        url = f"http://127.0.0.1:{port}/"
        print(f"Dashboard running at: {url}")
        print("Open the URL in your browser to view the dashboard.")

        if open_browser:
            import webbrowser

            print(f"Opening browser to: {url}")
            webbrowser.open(url)

        self.app.run(debug=debug, port=port)


def main(port: int = 8050, open_browser: bool = True):
    """Main function to run the dashboard."""
    dashboard = DashboardApp()
    dashboard.run(port=port, open_browser=open_browser)


if __name__ == "__main__":
    port = 8050
    main(port)