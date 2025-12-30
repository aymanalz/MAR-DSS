"""
Callbacks for the DSS Algorithm tab - Multi-Criteria Decision Support System.
"""

import dash
from dash import Input, Output, html, dcc, callback_context
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
import pandas as pd
import numpy as np
import mar_dss.app.utils.data_storage as dash_storage
import logging

logger = logging.getLogger(__name__)


def _get_decision_matrix(dss_results):
    """
    Create a decision matrix from DSS results.
    
    Returns:
        pandas.DataFrame: Decision matrix with options as rows and metrics as columns.
        Columns: Hydrogeologic, Environmental, Regulation, Capital Cost Efficiency, 
                 Maintenance Cost Efficiency, NPV Efficiency
    """
    if dss_results is None or not hasattr(dss_results, 'results') or not dss_results.results:
        return pd.DataFrame()
    
    # Get scores
    scores = getattr(dss_results, 'scores', {})
    if not scores:
        return pd.DataFrame()
    
    # Get cost data
    capital_cost_num = dash_storage.get_data("capital_cost_num")
    maintenance_cost_num = dash_storage.get_data("maintenance_cost_num")
    net_val_dict = dash_storage.get_data("net_val") or {}
    
    # Map option names to cost column names
    option_to_capital_col = {
        "Surface Recharge": "Spreading Pond Cost ($)",
        "Injection Well": "Injection Wells Cost ($)",
        "Dry Well": "Dry Wells Cost ($)"
    }
    
    option_to_maintenance_col = {
        "Surface Recharge": "Spreading Pond Maintenance Cost ($)",
        "Injection Well": "Injection Wells Maintenance Cost ($)",
        "Dry Well": "Dry Wells Maintenance Cost ($)"
    }
    
    option_to_npv_col = {
        "Surface Recharge": "Spreading Pond Net Present Value ($)",
        "Injection Well": "Injection Wells Net Present Value ($)",
        "Dry Well": "Dry Wells Net Present Value ($)"
    }
    
    # Collect all costs to find minimums
    capital_costs = []
    maintenance_costs = []
    npv_values = []
    
    for option_name in scores.keys():
        # Capital cost
        capital_col = option_to_capital_col.get(option_name)
        if capital_col and capital_cost_num is not None and capital_col in capital_cost_num.index:
            capital_val = float(capital_cost_num[capital_col]) if pd.notna(capital_cost_num[capital_col]) else 0
            if capital_val > 0:
                capital_costs.append(capital_val)
        
        # Maintenance cost
        maintenance_col = option_to_maintenance_col.get(option_name)
        if maintenance_col and maintenance_cost_num is not None and maintenance_col in maintenance_cost_num.index:
            maintenance_val = float(maintenance_cost_num[maintenance_col]) if pd.notna(maintenance_cost_num[maintenance_col]) else 0
            if maintenance_val > 0:
                maintenance_costs.append(maintenance_val)
        
        # NPV
        npv_col = option_to_npv_col.get(option_name)
        if npv_col and npv_col in net_val_dict:
            npv_val = float(net_val_dict[npv_col]) if pd.notna(net_val_dict[npv_col]) else 0
            if npv_val > 0:
                npv_values.append(npv_val)
    
    # Find minimums
    min_capital_cost = min(capital_costs) if capital_costs else 1
    min_maintenance_cost = min(maintenance_costs) if maintenance_costs else 1
    min_npv = min(npv_values) if npv_values else 1
    
    # Build decision matrix
    matrix_data = []
    option_names = []
    
    for option_name, option_scores in scores.items():
        # Get constraint scores
        hydro_score = option_scores.get("hydrogeologic", 0.0)
        env_score = option_scores.get("environmental", 0.0)
        reg_score = option_scores.get("regulation", 0.0)
        
        # Calculate cost efficiencies
        capital_col = option_to_capital_col.get(option_name)
        capital_val = 0.0
        if capital_col and capital_cost_num is not None and capital_col in capital_cost_num.index:
            capital_val = float(capital_cost_num[capital_col]) if pd.notna(capital_cost_num[capital_col]) else 0
        
        maintenance_col = option_to_maintenance_col.get(option_name)
        maintenance_val = 0.0
        if maintenance_col and maintenance_cost_num is not None and maintenance_col in maintenance_cost_num.index:
            maintenance_val = float(maintenance_cost_num[maintenance_col]) if pd.notna(maintenance_cost_num[maintenance_col]) else 0
        
        npv_col = option_to_npv_col.get(option_name)
        npv_val = 0.0
        if npv_col and npv_col in net_val_dict:
            npv_val = float(net_val_dict[npv_col]) if pd.notna(net_val_dict[npv_col]) else 0
        
        # Calculate efficiencies
        if capital_val > 0 and min_capital_cost > 0:
            capital_efficiency = 100.0 * (min_capital_cost / capital_val)
        else:
            capital_efficiency = 0.0
        
        if maintenance_val > 0 and min_maintenance_cost > 0:
            maintenance_efficiency = 100.0 * (min_maintenance_cost / maintenance_val)
        else:
            maintenance_efficiency = 0.0
        
        if npv_val > 0 and min_npv > 0:
            npv_efficiency = 100.0 * (min_npv / npv_val)
        else:
            npv_efficiency = 0.0
        
        # Add to matrix
        matrix_data.append([
            hydro_score,
            env_score,
            reg_score,
            capital_efficiency,
            maintenance_efficiency,
            npv_efficiency
        ])
        option_names.append(option_name)
    
    # Create DataFrame
    df = pd.DataFrame(
        matrix_data,
        index=option_names,
        columns=[
            "Hydrogeologic",
            "Environmental",
            "Regulation",
            "Capital Cost Efficiency",
            "Maintenance Cost Efficiency",
            "NPV Efficiency"
        ]
    )
    
    return df


def _normalize_matrix(df):
    """
    Normalize the decision matrix using min-max normalization.
    All metrics are benefit criteria (higher is better).
    """
    normalized_df = df.copy()
    
    # Min-max normalization: (x - min) / (max - min)
    for col in normalized_df.columns:
        col_min = normalized_df[col].min()
        col_max = normalized_df[col].max()
        col_range = col_max - col_min
        
        if col_range > 0:
            normalized_df[col] = (normalized_df[col] - col_min) / col_range
        else:
            # All values are the same, set to 1.0
            normalized_df[col] = 1.0
    
    return normalized_df


def _calculate_weighted_scores(df, weights):
    """
    Calculate weighted scores for each option using weighted sum method.
    
    Args:
        df: Normalized decision matrix
        weights: Dictionary with metric names as keys and weights as values
    
    Returns:
        pandas.Series: Weighted scores for each option
    """
    # Normalize weights to sum to 1
    total_weight = sum(weights.values())
    if total_weight == 0:
        # Default equal weights
        normalized_weights = {col: 1.0 / len(df.columns) for col in df.columns}
    else:
        normalized_weights = {col: weights.get(col, 0.0) / total_weight for col in df.columns}
    
    # Calculate weighted sum
    weighted_scores = pd.Series(0.0, index=df.index)
    for col in df.columns:
        weight = normalized_weights.get(col, 0.0)
        weighted_scores += df[col] * weight
    
    return weighted_scores, normalized_weights


def setup_dss_algorithm_callbacks(app):
    """Set up all callbacks for the DSS Algorithm tab."""
    
    @app.callback(
        [
            Output("dss-decision-matrix-table", "children"),
            Output("dss-weighted-scores", "children"),
            Output("dss-ranking", "children"),
            Output("dss-sensitivity-chart", "figure")
        ],
        [
            Input("analysis-tabs", "active_tab"),
            Input("weight-hydrogeologic", "value"),
            Input("weight-environmental", "value"),
            Input("weight-regulation", "value"),
            Input("weight-capital-cost", "value"),
            Input("weight-maintenance-cost", "value"),
            Input("weight-npv", "value")
        ],
        prevent_initial_call=False
    )
    def update_dss_algorithm(
        active_tab,
        weight_hydro,
        weight_env,
        weight_reg,
        weight_capital,
        weight_maintenance,
        weight_npv
    ):
        """Update DSS algorithm results based on weights."""
        # Only trigger when DSS Algorithm tab is active
        if active_tab != "analysis-dss-algorithm":
            return (
                html.Div("Please select the DSS Algorithm tab to view results."),
                html.Div(),
                html.Div(),
                go.Figure()
            )
        
        # Get DSS results
        dss_results = dash_storage.get_data("dss_results")
        
        # Create decision matrix
        decision_matrix = _get_decision_matrix(dss_results)
        
        if decision_matrix.empty:
            return (
                html.Div(
                    "No DSS evaluation results available. Please run the feasibility analysis first.",
                    className="text-muted text-center p-4"
                ),
                html.Div(),
                html.Div(),
                go.Figure()
            )
        
        # Get weights (default to 1.0 if None)
        weights = {
            "Hydrogeologic": weight_hydro if weight_hydro is not None else 1.0,
            "Environmental": weight_env if weight_env is not None else 1.0,
            "Regulation": weight_reg if weight_reg is not None else 1.0,
            "Capital Cost Efficiency": weight_capital if weight_capital is not None else 1.0,
            "Maintenance Cost Efficiency": weight_maintenance if weight_maintenance is not None else 1.0,
            "NPV Efficiency": weight_npv if weight_npv is not None else 1.0
        }
        
        # Normalize matrix
        normalized_matrix = _normalize_matrix(decision_matrix)
        
        # Calculate weighted scores
        weighted_scores, normalized_weights = _calculate_weighted_scores(normalized_matrix, weights)
        
        # Create decision matrix table
        matrix_table = _create_decision_matrix_table(decision_matrix, normalized_weights)
        
        # Create weighted scores display
        scores_display = _create_weighted_scores_display(weighted_scores)
        
        # Create ranking
        ranking_display = _create_ranking_display(weighted_scores)
        
        # Create sensitivity chart
        sensitivity_chart = _create_sensitivity_chart(decision_matrix, weighted_scores, normalized_weights)
        
        return matrix_table, scores_display, ranking_display, sensitivity_chart


def _create_decision_matrix_table(df, weights):
    """Create a formatted table for the decision matrix."""
    # Create table header using actual DataFrame column names
    header_cells = [
        html.Th("Option", style={"position": "sticky", "left": 0, "backgroundColor": "white", "zIndex": 1})
    ]
    
    # Add header cells for each column in the DataFrame
    for col in df.columns:
        weight = weights.get(col, 0.0)
        # Format column name for display
        if "Cost Efficiency" in col:
            # Split "Capital Cost Efficiency" or "Maintenance Cost Efficiency"
            if "Capital" in col:
                display_name = ["Capital Cost", "Efficiency"]
            elif "Maintenance" in col:
                display_name = ["Maintenance Cost", "Efficiency"]
            else:
                display_name = [col.replace(" Cost Efficiency", ""), "Cost Efficiency"]
        elif "Efficiency" in col:
            display_name = [col.replace(" Efficiency", ""), "Efficiency"]
        else:
            display_name = [col]
        
        # Create header with proper line breaks using html structure
        header_content = []
        for i, part in enumerate(display_name):
            if i > 0:
                header_content.append(html.Br())
            header_content.append(part)
        header_content.append(html.Br())
        header_content.append(f"(Weight: {weight:.2f})")
        
        header_cells.append(
            html.Th(
                header_content,
                style={"textAlign": "center", "fontSize": "0.8rem", "padding": "0.5rem"}
            )
        )
    
    header = [
        html.Thead([
            html.Tr(header_cells)
        ])
    ]
    
    # Create table body using actual DataFrame column names
    body = [html.Tbody([
        html.Tr([
            html.Td(option_name, style={"position": "sticky", "left": 0, "backgroundColor": "white", "zIndex": 1, "fontSize": "0.85rem", "padding": "0.5rem"})] +
            [html.Td(f"{df.loc[option_name, col]:.1f}%", style={"textAlign": "center", "fontSize": "0.85rem", "padding": "0.5rem"}) for col in df.columns]
        )
        for option_name in df.index
    ])]
    
    table = dbc.Table(
        header + body,
        bordered=True,
        hover=True,
        responsive=True,
        striped=True,
        className="table-sm table-hover",
        style={"fontSize": "0.85rem", "marginBottom": "0"}
    )
    
    return table


def _create_weighted_scores_display(weighted_scores):
    """Create display for weighted scores."""
    scores_list = []
    for option_name, score in weighted_scores.items():
        scores_list.append(
            html.Div([
                html.Small(f"{option_name}: ", className="fw-bold"),
                html.Span(f"{score * 100:.2f}%", className="text-primary fw-bold")
            ], className="mb-1 small")
        )
    
    return html.Div(scores_list)


def _create_ranking_display(weighted_scores):
    """Create ranking display."""
    # Sort by score (descending)
    ranked = weighted_scores.sort_values(ascending=False)
    
    ranking_items = []
    for rank, (option_name, score) in enumerate(ranked.items(), 1):
        badge_color = "success" if rank == 1 else "primary" if rank == 2 else "secondary"
        ranking_items.append(
            dbc.ListGroupItem([
                dbc.Badge(f"#{rank}", color=badge_color, className="me-2"),
                html.Small(option_name, className="fw-bold"),
                html.Span(f" {score * 100:.2f}%", className="text-muted ms-1 small")
            ], className="py-1")
        )
    
    return dbc.ListGroup(ranking_items, flush=True)


def _create_sensitivity_chart(decision_matrix, weighted_scores, weights):
    """Create a sensitivity chart showing how weights affect rankings."""
    # Create a bar chart showing weighted scores
    fig = go.Figure()
    
    ranked = weighted_scores.sort_values(ascending=False)
    
    colors = ['#28a745', '#007bff', '#6c757d']  # Green, Blue, Gray
    
    fig.add_trace(go.Bar(
        x=ranked.index,
        y=ranked.values * 100,
        marker_color=[colors[min(i, 2)] for i in range(len(ranked))],
        text=[f"{val * 100:.2f}%" for val in ranked.values],
        textposition='outside',
        hovertemplate='<b>%{x}</b><br>Weighted Score: %{y:.2f}%<extra></extra>'
    ))
    
    fig.update_layout(
        title=dict(text="Weighted Scores Ranking", font=dict(size=14)),
        xaxis_title="MAR Option",
        yaxis_title="Weighted Score (%)",
        template="plotly_white",
        height=300,
        showlegend=False,
        margin=dict(l=50, r=50, t=40, b=50)
    )
    
    return fig

