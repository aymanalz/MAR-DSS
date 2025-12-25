"""
Hydrogeological Feasibility Scoring and Visualization Utilities
"""

import plotly.graph_objects as go
import numpy as np
import pandas as pd
import dash_bootstrap_components as dbc
from dash import html, dcc
import mar_dss.app.utils.data_storage as dash_storage
from mar_dss.app.callbacks.analysis_callbacks import get_session_graph, get_graph_inputs


# Scoring configuration for each node
SCORING_CONFIG = {
    # Leaf Nodes (Decision Nodes)
    "surface_recharge_suitability": {
        "type": "boolean",
        "weight": 3.0,
        "certainty": 0.8,
        "scoring": {True: 100, False: 0},
        "group": "Engineering Feasibility"
    },
    "rechargability": {
        "type": "numeric",
        "weight": 3.0,
        "certainty": 0.8,
        "scoring": "linear",
        "threshold": 50.0,
        "group": "Aquifer Properties"
    },
    "confined_rechargability": {
        "type": "numeric",
        "weight": 3.0,
        "certainty": 0.8,
        "scoring": "linear",
        "threshold": 50.0,
        "group": "Aquifer Properties"
    },
    "leakage_significance": {
        "type": "categorical",
        "weight": 2.0,
        "certainty": 0.8,
        "scoring": {"low": 100, "medium": 50, "high": 0},
        "group": "Aquifer Properties"
    },
    "excessive_deep_aquifer": {
        "type": "categorical",
        "weight": 1.5,
        "certainty": 0.8,
        "scoring": {"Low Depth": 100, "Moderate Deep": 60, "Too Deep": 0},
        "group": "Aquifer Properties"
    },
    "gs_slope_significance": {
        "type": "categorical",
        "weight": 1.5,
        "certainty": 0.8,
        "scoring": {"Gentle": 100, "Moderate": 70, "Steep": 0},
        "group": "Site Characteristics"
    },
    "vadose_high_toxicity_present": {
        "type": "boolean",
        "weight": 2.5,
        "certainty": 0.85,
        "scoring": {True: 0, False: 100},
        "group": "Environmental Quality"
    },
    "annual_recharge_volume": {
        "type": "numeric",
        "weight": 1.5,
        "certainty": 0.8,
        "scoring": "relative",
        "group": "Aquifer Properties"
    },
    
    # Computational Nodes
    "k_vadose_threshold": {
        "type": "boolean",
        "weight": 2.0,
        "certainty": 0.9,
        "scoring": {True: 80, False: 20},
        "group": "Aquifer Characteristics"
    },
    "k_min_vadose": {
        "type": "numeric",
        "weight": 2.5,
        "certainty": 0.9,
        "scoring": "linear",
        "threshold": 0.3,
        "group": "Aquifer Characteristics"
    },
    "vadose_pollution_present": {
        "type": "boolean",
        "weight": 1.5,
        "certainty": 0.85,
        "scoring": {True: 40, False: 100},
        "group": "Environmental Quality"
    },
    "vadose_remediation_needed": {
        "type": "boolean",
        "weight": 1.5,
        "certainty": 0.85,
        "scoring": {True: 50, False: 100},
        "group": "Environmental Quality"
    },
    "top_soil_removable": {
        "type": "boolean",
        "weight": 1.0,
        "certainty": 0.8,
        "scoring": {True: 100, False: 0, None: 50},
        "group": "Surface Feasibility"
    },
}


def calculate_node_score(node_id, value, config, all_node_values):
    """Calculate score for a single node based on its type and value."""
    if value is None:
        return 0
    
    node_type = config.get("type")
    scoring = config.get("scoring")
    
    if node_type == "boolean":
        # Handle both boolean True/False and string representations
        if isinstance(value, bool):
            return scoring.get(value, 0)
        elif isinstance(value, str):
            bool_value = value.lower() in ['true', '1', 'yes']
            return scoring.get(bool_value, 0)
        else:
            return scoring.get(bool(value), 0)
    
    elif node_type == "categorical":
        # Handle both exact matches and case-insensitive
        if value in scoring:
            return scoring[value]
        # Try case-insensitive match
        for key, score in scoring.items():
            if str(value).lower() == str(key).lower():
                return score
        return 0
    
    elif node_type == "numeric":
        try:
            value = float(value)
        except (ValueError, TypeError):
            return 0
            
        scoring_method = scoring
        if scoring_method == "linear":
            threshold = config.get("threshold", 100)
            if threshold == 0:
                return 0
            if value >= threshold:
                return 100
            else:
                return max(0, (value / threshold) * 100)
        elif scoring_method == "relative":
            # Normalize relative to source water volume
            source_volume = all_node_values.get("source_water_volume", [])
            if isinstance(source_volume, list):
                total_source = sum(source_volume) if source_volume else 1
            else:
                total_source = float(source_volume) if source_volume else 1
            
            if total_source > 0:
                ratio = value / total_source
                return min(100, ratio * 100)
            return 0
    
    return 0


def calculate_hydrogeological_feasibility_score(graph, node_values):
    """
    Calculate overall hydrogeological feasibility score (0-100%).
    
    Returns:
        dict: {
            'final_score': float (0-100),
            'component_scores': dict,
            'weighted_contributions': dict,
            'breakdown': dict
        }
    """
    if graph is None or node_values is None:
        return {
            'final_score': 0,
            'component_scores': {},
            'weighted_contributions': {},
            'breakdown': {'leaf_nodes': {}, 'computational_nodes': {}}
        }
    
    total_weighted_score = 0.0
    total_weight = 0.0
    component_scores = {}
    weighted_contributions = {}
    leaf_scores = {}
    computational_scores = {}
    
    # Iterate through all nodes
    for node_id, node in graph.nodes.items():
        if node.is_input():
            continue  # Skip input nodes
        
        # Get scoring config
        config = SCORING_CONFIG.get(node_id)
        if not config:
            continue  # Skip nodes without config
        
        # Get node value
        value = node_values.get(node_id)
        if value is None:
            continue
        
        # Calculate base score
        base_score = calculate_node_score(node_id, value, config, node_values)
        
        # Apply certainty adjustment
        certainty = config.get("certainty", 1.0)
        adjusted_score = base_score * certainty
        
        # Get weight
        weight = config.get("weight", 1.0)
        
        # Calculate contribution
        contribution = adjusted_score * weight
        total_weighted_score += contribution
        total_weight += weight * certainty
        
        # Store for breakdown
        component_scores[node_id] = base_score
        weighted_contributions[node_id] = contribution
        
        # Categorize by node type
        if node.is_leaf():
            leaf_scores[node_id] = {
                'score': base_score,
                'value': value,
                'contribution': contribution,
                'weight': weight,
                'name': node.name
            }
        else:
            computational_scores[node_id] = {
                'score': base_score,
                'value': value,
                'contribution': contribution,
                'weight': weight,
                'name': node.name
            }
    
    # Calculate final score
    if total_weight > 0:
        final_score = (total_weighted_score / total_weight)
    else:
        final_score = 0.0
    
    return {
        'final_score': round(final_score, 1),
        'component_scores': component_scores,
        'weighted_contributions': weighted_contributions,
        'breakdown': {
            'leaf_nodes': leaf_scores,
            'computational_nodes': computational_scores
        }
    }


def create_feasibility_gauge(score):
    """Create a gauge chart for the overall feasibility score."""
    # Determine color based on score
    if score >= 80:
        color = "green"
        status = "Highly Feasible"
    elif score >= 60:
        color = "yellow"
        status = "Feasible"
    elif score >= 40:
        color = "orange"
        status = "Conditionally Feasible"
    else:
        color = "red"
        status = "Infeasible"
    
    fig = go.Figure(go.Indicator(
        mode = "gauge+number+delta",
        value = score,
        domain = {'x': [0, 1], 'y': [0, 1]},
        title = {'text': "Hydrogeological Feasibility Score"},
        delta = {'reference': 50},
        gauge = {
            'axis': {'range': [None, 100]},
            'bar': {'color': color},
            'steps': [
                {'range': [0, 40], 'color': "lightgray"},
                {'range': [40, 60], 'color': "gray"},
                {'range': [60, 80], 'color': "lightyellow"},
                {'range': [80, 100], 'color': "lightgreen"}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': 50
            }
        }
    ))
    
    fig.update_layout(
        height=300,
        margin=dict(l=20, r=20, t=40, b=20)
    )
    
    return fig, status, color


def create_monthly_gw_depth_chart(monthly_gw_depth, op_gw_depth=None):
    """Create a line chart for monthly groundwater depth."""
    months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", 
              "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    
    if monthly_gw_depth is None or len(monthly_gw_depth) != 12:
        monthly_gw_depth = [20] * 12
    
    avg_depth = np.mean(monthly_gw_depth)
    min_depth = np.min(monthly_gw_depth)
    max_depth = np.max(monthly_gw_depth)
    
    fig = go.Figure()
    
    # Main line
    fig.add_trace(go.Scatter(
        x=months,
        y=monthly_gw_depth,
        mode='lines+markers',
        name='Groundwater Depth',
        line=dict(color='blue', width=3),
        marker=dict(size=8),
        fill='tozeroy',
        fillcolor='rgba(0, 100, 255, 0.1)'
    ))
    
    # Average line
    fig.add_trace(go.Scatter(
        x=months,
        y=[avg_depth] * 12,
        mode='lines',
        name='Average Depth',
        line=dict(color='green', width=2, dash='dash')
    ))
    
    # Operational depth line
    if op_gw_depth is not None:
        fig.add_trace(go.Scatter(
            x=months,
            y=[op_gw_depth] * 12,
            mode='lines',
            name='Operational Depth',
            line=dict(color='red', width=2, dash='dot')
        ))
    
    fig.update_layout(
        title="Monthly Groundwater Depth Variation",
        xaxis_title="Month",
        yaxis_title="Depth (ft)",
        height=400,
        hovermode='x unified',
        legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01)
    )
    
    return fig


def create_component_scores_chart(breakdown):
    """Create a horizontal bar chart showing component scores."""
    leaf_nodes = breakdown.get('leaf_nodes', {})
    computational_nodes = breakdown.get('computational_nodes', {})
    
    # Prepare data
    node_names = []
    scores = []
    colors = []
    node_types = []
    
    # Add leaf nodes first
    for node_id, data in sorted(leaf_nodes.items(), key=lambda x: x[1]['score'], reverse=True):
        node_names.append(data['name'])
        scores.append(data['score'])
        colors.append('#0d6efd')  # Blue for leaf nodes
        node_types.append('Decision Node')
    
    # Add computational nodes
    for node_id, data in sorted(computational_nodes.items(), key=lambda x: x[1]['score'], reverse=True):
        node_names.append(data['name'])
        scores.append(data['score'])
        colors.append('#6c757d')  # Gray for computational nodes
        node_types.append('Computational')
    
    if not node_names:
        # Return empty figure
        fig = go.Figure()
        fig.add_annotation(
            text="No data available",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False
        )
        fig.update_layout(height=300)
        return fig
    
    fig = go.Figure()
    fig.add_trace(go.Bar(
        y=node_names,
        x=scores,
        orientation='h',
        marker=dict(color=colors),
        text=[f"{s:.1f}%" for s in scores],
        textposition='outside',
        hovertemplate='<b>%{y}</b><br>Score: %{x:.1f}%<br>Type: %{customdata}<extra></extra>',
        customdata=node_types
    ))
    
    fig.update_layout(
        title="Component Scores Breakdown",
        xaxis_title="Score (%)",
        yaxis_title="",
        height=max(400, len(node_names) * 40),
        xaxis=dict(range=[0, 100]),
        margin=dict(l=200, r=50, t=50, b=50)
    )
    
    return fig


def create_stratigraphy_profile(stratigraphy_data):
    """Create a simple vertical profile visualization of stratigraphy."""
    if not stratigraphy_data or len(stratigraphy_data) == 0:
        fig = go.Figure()
        fig.add_annotation(
            text="No stratigraphy data available",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False
        )
        fig.update_layout(height=300)
        return fig
    
    # Convert to DataFrame if needed
    if isinstance(stratigraphy_data, list):
        df = pd.DataFrame(stratigraphy_data)
    else:
        df = stratigraphy_data
    
    # Calculate cumulative depths
    cumulative_depth = 0
    y_bottom = []
    y_top = []
    layer_names = []
    k_values = []
    
    for idx, row in df.iterrows():
        thickness = float(row.get('thickness', row.get('Thickness/Depth (ft)', 0)))
        k = float(row.get('conductivity', row.get('K', 0)))
        layer_name = row.get('layer', row.get('Layer', f'Layer {idx+1}'))
        
        y_top.append(cumulative_depth)
        cumulative_depth += thickness
        y_bottom.append(cumulative_depth)
        layer_names.append(layer_name)
        k_values.append(k)
    
    # Create color scale based on K values
    max_k = max(k_values) if k_values else 1
    colors = [f'rgba({int(255*(1-k/max_k))}, {int(255*(k/max_k))}, 0, 0.7)' for k in k_values]
    
    fig = go.Figure()
    
    for i, (name, top, bottom, k, color) in enumerate(zip(layer_names, y_top, y_bottom, k_values, colors)):
        fig.add_trace(go.Bar(
            x=[1],
            y=[bottom - top],
            base=top,
            name=name,
            marker=dict(color=color),
            text=f"{name}<br>K: {k:.2f} ft/day<br>Thickness: {bottom-top:.1f} ft",
            textposition='inside',
            hovertemplate=f'<b>{name}</b><br>Thickness: {bottom-top:.1f} ft<br>K: {k:.2f} ft/day<extra></extra>'
        ))
    
    fig.update_layout(
        title="Stratigraphy Profile",
        xaxis=dict(showticklabels=False, range=[0.5, 1.5]),
        yaxis=dict(title="Depth (ft)", autorange='reversed'),
        barmode='stack',
        height=400,
        showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    
    return fig

