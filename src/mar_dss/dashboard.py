"""
Dashboard launcher for MAR DSS.
"""

from mar_dss.app.main import DashboardApp


def launch_dashboard(debug=True, port=8050):
    """
    Launch the MAR DSS dashboard.

    Args:
        debug (bool): Run in debug mode
        port (int): Port number to run the dashboard on
    """
    dashboard = DashboardApp()
    dashboard.run(debug=debug, port=port)


if __name__ == "__main__":
    launch_dashboard()
