"""
Sidebar content for MAR DSS dashboard.
"""

from dash import html, dcc
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
import pandas as pd
import numpy as np


def create_water_levels_content():
    """Create content for Water Levels sidebar tab."""
    # Generate sample data
    dates = pd.date_range(start='2023-01-01', end='2023-12-31', freq='D')
    water_levels = np.random.normal(100, 10, len(dates)) + \
                  5 * np.sin(np.arange(len(dates)) * 2 * np.pi / 365)
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=dates,
        y=water_levels,
        mode='lines+markers',
        name='Water Level',
        line=dict(color='#1f77b4', width=2),
        marker=dict(size=4)
    ))
    
    fig.update_layout(
        title='Water Level Monitoring',
        xaxis_title='Date',
        yaxis_title='Water Level (m)',
        hovermode='x unified',
        template='plotly_white'
    )
    
    return html.Div([
        html.H3("Water Level Monitoring"),
        html.P("Real-time water level data and historical trends."),
        dcc.Graph(figure=fig)
    ])


def create_recharge_content():
    """Create content for Recharge Rates sidebar tab."""
    # Generate sample data
    dates = pd.date_range(start='2023-01-01', end='2023-12-31', freq='D')
    recharge_data = np.random.exponential(2, len(dates)) * \
                   (1 + 0.5 * np.sin(np.arange(len(dates)) * 2 * np.pi / 365))
    
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=dates,
        y=recharge_data,
        name='Recharge Rate',
        marker_color='#2ca02c'
    ))
    
    fig.update_layout(
        title='Recharge Rate Analysis',
        xaxis_title='Date',
        yaxis_title='Recharge Rate (mm/day)',
        template='plotly_white'
    )
    
    return html.Div([
        html.H3("Recharge Rate Analysis"),
        html.P("Recharge rate monitoring and analysis tools."),
        dcc.Graph(figure=fig)
    ])


def create_quality_content():
    """Create content for Water Quality sidebar tab."""
    # Generate sample data
    dates = pd.date_range(start='2023-01-01', end='2023-12-31', freq='D')
    quality_data = np.random.normal(7.5, 0.5, len(dates))
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=dates,
        y=quality_data,
        mode='lines+markers',
        name='pH Level',
        line=dict(color='#ff7f0e', width=2),
        marker=dict(size=4)
    ))
    
    fig.update_layout(
        title='Water Quality Monitoring',
        xaxis_title='Date',
        yaxis_title='pH Level',
        hovermode='x unified',
        template='plotly_white'
    )
    
    return html.Div([
        html.H3("Water Quality Monitoring"),
        html.P("Water quality parameters and analysis."),
        dcc.Graph(figure=fig)
    ])


def create_export_content():
    """Create content for Data Export sidebar tab."""
    return html.Div([
        html.H3("Data Export"),
        html.P("Export data in various formats."),
        dbc.Card([
            dbc.CardBody([
                html.H5("Export Options"),
                dbc.Row([
                    dbc.Col([
                        dbc.Button("Export CSV", color="primary", className="mb-2"),
                        dbc.Button("Export Excel", color="success", className="mb-2"),
                        dbc.Button("Export PDF", color="warning", className="mb-2")
                    ], width=6),
                    dbc.Col([
                        html.P("Select data range:"),
                        dbc.Select(
                            options=[
                                {"label": "Last 7 days", "value": "7days"},
                                {"label": "Last 30 days", "value": "30days"},
                                {"label": "Last 3 months", "value": "3months"},
                                {"label": "All data", "value": "all"}
                            ],
                            value="30days"
                        )
                    ], width=6)
                ])
            ])
        ])
    ])
