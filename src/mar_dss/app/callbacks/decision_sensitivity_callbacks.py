"""
Decision Sensitivity Analysis callbacks for MAR DSS dashboard.

This module implements one-at-a-time (OAT) sensitivity analysis to investigate
how changes in input parameters affect DSS decision outcomes.
"""

import logging
import copy
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from dash import dcc, html, dash_table, Input, Output, State
import dash_bootstrap_components as dbc
import mar_dss.app.utils.data_storage as dash_storage
from mar_dss.app.callbacks.analysis_callbacks import run_integrated_analysis

logger = logging.getLogger(__name__)

# Parameter definitions with metadata
# Maps from dash_storage keys to parameter definitions
# Based on input.yaml with correct storage key mappings
PARAMETER_DEFINITIONS = {
    # Aquifer Properties (from input.yaml)
    "aq_type": {
        "name": "Aquifer Type",
        "type": "categorical",
        "group": "Aquifer Properties",
        "allowed_values": ["Confined", "Unconfined", "Semi-confined", "Karstic", "Fractured", "Other"],
        "storage_key": "aq_type",  # dash_storage key (matches input.yaml)
        "input_key": "aq_type",  # input.yaml key
    },
    "stratigraphy_data": {
        "name": "Stratigraphy Table",
        "type": "table",
        "group": "Aquifer Properties",
        "description": "Layer thickness, conductivity, and yield data",
        "storage_key": "stratigraphy_data",
        "input_key": "stratigraphy_table",
        "note": "Varies individual layer properties (thickness, conductivity, yield)",
    },
    "groundwater_data": {
        "name": "Groundwater Depth",
        "type": "table",
        "group": "Aquifer Properties",
        "description": "Monthly groundwater elevations",
        "storage_key": "groundwater_data",
        "input_key": "monthly_gw_depth",
        "note": "Varies monthly groundwater elevations",
    },
    "ground_surface_elevation": {
        "name": "Ground Surface Elevation",
        "type": "numeric",
        "group": "Aquifer Properties",
        "unit": "ft",
        "default_range": (-10, 10),  # percentage variation
        "storage_key": "ground_surface_elevation",
        "note": "Used to calculate monthly_gw_depth",
    },
    "d_gw_min": {
        "name": "Minimum Groundwater Depth",
        "type": "numeric",
        "group": "Design Sizing",
        "unit": "m",
        "default_range": (-20, 20),
        "min": 0.0,
        "max": 100.0,
        "storage_key": "d_gw_min",
        "note": "Currently hardcoded to 5.0 in get_graph_inputs",
    },
    "Hmax": {
        "name": "Maximum Allowable Pressure",
        "type": "numeric",
        "group": "Aquifer Properties",
        "unit": "ft",
        "default_range": (-20, 20),
        "min": 0.1,
        "max": 1000.0,
        "storage_key": "Hmax",
    },
    
    # Design Sizing (from input.yaml)
    "max_available_area": {
        "name": "Maximum Available Area",
        "type": "numeric",
        "group": "Design Sizing",
        "unit": "ft²",
        "default_range": (-30, 30),
        "min": 0,
        "storage_key": "max_available_area",
    },
    "max_infiltration_area": {
        "name": "Max Infiltration Area (%)",
        "type": "numeric",
        "group": "Design Sizing",
        "unit": "%",
        "default_range": (-20, 20),
        "min": 0,
        "max": 100,
        "storage_key": "max_infiltration_area",
    },
    
    # Water Balance (from input.yaml)
    "monthly_flow": {
        "name": "Monthly Available Source Water Volume",
        "type": "list",
        "group": "Water Balance",
        "unit": "AF/month",
        "description": "Source water volume per month (12 values)",
        "default_range": (-30, 30),  # percentage variation applied to all months
        "storage_key": "monthly_flow",
        "input_key": "source_water_volume",
        "note": "Varies all monthly values by same percentage",
    },
    
    # Site Characteristics (from input.yaml)
    "ground_surface_slope": {
        "name": "Ground Surface Slope",
        "type": "numeric",
        "group": "Site Characteristics",
        "unit": "%",
        "default_range": (-20, 20),
        "min": 0.0,
        "max": 100.0,
        "storage_key": "ground_surface_slope",
    },
    
    # Environmental Quality (from input.yaml)
    "vadose_zone_pollution": {
        "name": "Vadose Zone Pollution",
        "type": "categorical",
        "group": "Environmental Quality",
        "allowed_values": [
            "None",
            "Yes, biodegradable Pollution",
            "Yes, highly toxic contaminants in the vadose zone (e.g., heavy metals, volatile organic compounds, radioactive materials)"
        ],
        "storage_key": "vadose_zone_pollution",
        "note": "Maps from vadose_pollution_flag and vadose_pollution_high_toxicity",
    },
    
    # Environmental Risk Parameters (from environmental impact tab)
    "tss_turbidity_risk": {
        "name": "TSS/Turbidity Risk",
        "type": "categorical",
        "group": "Environmental",
        "allowed_values": ["LOW RISK", "MODERATE RISK", "HIGH RISK"],
        "storage_key": "tss_turbidity_risk",
    },
    "doc_toc_risk": {
        "name": "DOC/TOC Risk",
        "type": "categorical",
        "group": "Environmental",
        "allowed_values": ["LOW RISK", "MODERATE RISK", "HIGH RISK"],
        "storage_key": "doc_toc_risk",
    },
    "ph_alkalinity_risk": {
        "name": "pH/Alkalinity Risk",
        "type": "categorical",
        "group": "Environmental",
        "allowed_values": ["LOW RISK", "MODERATE RISK", "HIGH RISK"],
        "storage_key": "ph_alkalinity_risk",
    },
    "tds_salinity_risk": {
        "name": "TDS/Salinity Risk",
        "type": "categorical",
        "group": "Environmental",
        "allowed_values": ["LOW RISK", "MODERATE RISK", "HIGH RISK"],
        "storage_key": "tds_salinity_risk",
    },
    "inorganic_contaminants_risk": {
        "name": "Inorganic Contaminants Risk",
        "type": "categorical",
        "group": "Environmental",
        "allowed_values": ["LOW RISK", "MODERATE RISK", "HIGH RISK"],
        "storage_key": "inorganic_contaminants_risk",
    },
    "emerging_contaminants_risk": {
        "name": "Emerging Contaminants Risk",
        "type": "categorical",
        "group": "Environmental",
        "allowed_values": ["LOW RISK", "MODERATE RISK", "HIGH RISK"],
        "storage_key": "emerging_contaminants_risk",
    },
    "redox_compatibility_risk": {
        "name": "Redox Compatibility Risk",
        "type": "categorical",
        "group": "Environmental",
        "allowed_values": ["LOW RISK", "MODERATE RISK", "HIGH RISK"],
        "storage_key": "redox_compatibility_risk",
    },
    "pathogen_risk": {
        "name": "Pathogen Risk",
        "type": "categorical",
        "group": "Environmental",
        "allowed_values": ["LOW RISK", "MODERATE RISK", "HIGH RISK"],
        "storage_key": "pathogen_risk",
    },
}


def get_parameter_baseline(parameter_name):
    """Get current parameter value from dash_storage.
    
    Args:
        parameter_name: Name of the parameter (key in PARAMETER_DEFINITIONS)
        
    Returns:
        tuple: (baseline_value, parameter_metadata)
    """
    if parameter_name not in PARAMETER_DEFINITIONS:
        logger.warning(f"Parameter {parameter_name} not in definitions")
        return None, None
    
    param_def = PARAMETER_DEFINITIONS[parameter_name]
    # Use storage_key if available, otherwise use parameter_name
    storage_key = param_def.get("storage_key", parameter_name)
    baseline_value = dash_storage.get_data(storage_key)
    
    return baseline_value, param_def


def create_parameter_variations(parameter_name, baseline_value, variation_type="percentage", 
                                num_points=10, min_val=None, max_val=None):
    """Create a list of parameter values to test.
    
    Args:
        parameter_name: Name of the parameter
        baseline_value: Current/baseline value
        variation_type: "percentage", "absolute", or "categorical"
        num_points: Number of variation points (for numeric/list)
        min_val: Minimum value (for numeric)
        max_val: Maximum value (for numeric)
        
    Returns:
        list: List of parameter values to test
    """
    if baseline_value is None:
        logger.warning(f"Baseline value for {parameter_name} is None")
        return []
    
    param_def = PARAMETER_DEFINITIONS.get(parameter_name, {})
    param_type = param_def.get("type", "numeric")
    
    if param_type == "categorical":
        # Test all possible values
        allowed_values = param_def.get("allowed_values", [])
        if baseline_value in allowed_values:
            return allowed_values
        else:
            return allowed_values if allowed_values else [baseline_value]
    
    elif param_type == "numeric":
        try:
            baseline_float = float(baseline_value)
        except (ValueError, TypeError):
            logger.warning(f"Cannot convert {parameter_name} baseline to float: {baseline_value}")
            return [baseline_value]
        
        # Determine range
        if variation_type == "percentage":
            default_range = param_def.get("default_range", (-20, 20))
            pct_min = default_range[0] if min_val is None else ((min_val - baseline_float) / baseline_float * 100) if baseline_float != 0 else -20
            pct_max = default_range[1] if max_val is None else ((max_val - baseline_float) / baseline_float * 100) if baseline_float != 0 else 20
            
            min_val = baseline_float * (1 + pct_min / 100)
            max_val = baseline_float * (1 + pct_max / 100)
        else:  # absolute
            if min_val is None:
                default_range = param_def.get("default_range", (-20, 20))
                min_val = baseline_float + default_range[0]
            if max_val is None:
                default_range = param_def.get("default_range", (-20, 20))
                max_val = baseline_float + default_range[1]
        
        # Apply parameter-specific constraints
        param_min = param_def.get("min")
        param_max = param_def.get("max")
        if param_min is not None:
            min_val = max(min_val, param_min)
        if param_max is not None:
            max_val = min(max_val, param_max)
        
        # Generate variation points
        if min_val >= max_val:
            return [baseline_float]
        
        variations = np.linspace(min_val, max_val, num_points).tolist()
        return variations
    
    elif param_type == "list":
        # For lists (e.g., monthly_flow), apply percentage variation to all elements
        if not isinstance(baseline_value, list):
            logger.warning(f"Expected list for {parameter_name}, got {type(baseline_value)}")
            return [baseline_value]
        
        # Create percentage variations
        default_range = param_def.get("default_range", (-20, 20))
        pct_min = default_range[0] if min_val is None else min_val
        pct_max = default_range[1] if max_val is None else max_val
        
        variations = []
        for pct in np.linspace(pct_min, pct_max, num_points):
            multiplier = 1 + pct / 100
            varied_list = [val * multiplier if isinstance(val, (int, float)) else val 
                          for val in baseline_value]
            variations.append(varied_list)
        
        return variations
    
    elif param_type == "table":
        # For tables (e.g., stratigraphy_data, groundwater_data), vary specific properties
        # This is complex - for now, return baseline only with a note
        logger.info(f"Table type parameter {parameter_name} - returning baseline only. "
                   f"Full table variation not yet implemented.")
        return [baseline_value]
    
    elif param_type == "boolean":
        # Test both True and False
        return [True, False]
    
    else:
        # Unknown type, return baseline only
        logger.warning(f"Unknown parameter type {param_type} for {parameter_name}")
        return [baseline_value]


def extract_decision_outputs(dss_results):
    """Extract all relevant decision metrics from DSS results.
    
    Args:
        dss_results: DSS results object from forward_run
        
    Returns:
        dict: Structured dictionary with decision outputs
    """
    if dss_results is None or not hasattr(dss_results, 'results') or not dss_results.results:
        return None
    
    results = dss_results.results
    filters = getattr(dss_results, 'filters', {})
    scores = getattr(dss_results, 'scores', {})
    
    decision_outputs = {
        "option_statuses": {},
        "option_rankings": {},
        "option_scores": {},
        "option_benefit_scores": {},
    }
    
    # Extract statuses and benefit scores
    for option_name, result in results.items():
        decision_outputs["option_statuses"][option_name] = result.get("status", "Unknown")
        decision_outputs["option_benefit_scores"][option_name] = result.get("benefit_score", 0.0)
        
        # Extract individual scores if available
        if option_name in scores:
            decision_outputs["option_scores"][option_name] = scores[option_name]
    
    # Calculate rankings based on benefit scores
    sorted_options = sorted(
        decision_outputs["option_benefit_scores"].items(),
        key=lambda x: x[1],
        reverse=True
    )
    for rank, (option_name, _) in enumerate(sorted_options, start=1):
        decision_outputs["option_rankings"][option_name] = rank
    
    return decision_outputs


def run_sensitivity_analysis(parameter_name, variation_range=None, num_points=10):
    """Run sensitivity analysis for a single parameter.
    
    Args:
        parameter_name: Name of parameter to analyze
        variation_range: Tuple (min, max) for variation range (percentage or absolute)
        num_points: Number of variation points to test
        
    Returns:
        dict: Sensitivity analysis results
    """
    logger.info(f"Running sensitivity analysis for parameter: {parameter_name}")
    
    # Get baseline
    baseline_value, param_def = get_parameter_baseline(parameter_name)
    if baseline_value is None:
        logger.error(f"Cannot get baseline for {parameter_name}")
        return None
    
    # Create variations
    min_val = variation_range[0] if variation_range and len(variation_range) >= 2 else None
    max_val = variation_range[1] if variation_range and len(variation_range) >= 2 else None
    
    variations = create_parameter_variations(
        parameter_name, baseline_value, 
        num_points=num_points, min_val=min_val, max_val=max_val
    )
    
    if not variations:
        logger.error(f"No variations generated for {parameter_name}")
        return None
    
    # Get baseline decision outputs
    baseline_dss_results = dash_storage.get_data("dss_results")
    baseline_outputs = extract_decision_outputs(baseline_dss_results)
    
    if baseline_outputs is None:
        logger.warning("No baseline DSS results available, running analysis...")
        try:
            baseline_dss_results, _ = run_integrated_analysis()
            baseline_outputs = extract_decision_outputs(baseline_dss_results)
        except Exception as e:
            logger.error(f"Error running baseline analysis: {e}", exc_info=True)
            return None
    
    # Store original parameter value
    original_value = copy.deepcopy(baseline_value)
    
    # Run sensitivity analysis
    sensitivity_results = {
        "parameter_name": parameter_name,
        "parameter_display_name": param_def.get("name", parameter_name),
        "baseline_value": baseline_value,
        "variations": [],
        "baseline_outputs": baseline_outputs,
    }
    
    for i, variation_value in enumerate(variations):
        logger.debug(f"Testing variation {i+1}/{len(variations)}: {variation_value}")
        
        try:
            # Get storage key for this parameter
            param_def = PARAMETER_DEFINITIONS.get(parameter_name, {})
            storage_key = param_def.get("storage_key", parameter_name)
            
            # Set modified parameter
            dash_storage.set_data(storage_key, variation_value)
            
            # Run analysis - this will use the modified parameter
            dss_results, _ = run_integrated_analysis()
            
            # Extract outputs
            outputs = extract_decision_outputs(dss_results)
            
            if outputs:
                sensitivity_results["variations"].append({
                    "parameter_value": variation_value,
                    "outputs": outputs,
                })
            
        except Exception as e:
            logger.error(f"Error in sensitivity analysis iteration {i+1}: {e}", exc_info=True)
            continue
    
    # Restore original parameter value
    param_def = PARAMETER_DEFINITIONS.get(parameter_name, {})
    storage_key = param_def.get("storage_key", parameter_name)
    dash_storage.set_data(storage_key, original_value)
    
    # Re-run analysis to restore baseline state
    try:
        run_integrated_analysis()
    except Exception as e:
        logger.warning(f"Error restoring baseline state: {e}")
    
    logger.info(f"Sensitivity analysis completed for {parameter_name}: {len(sensitivity_results['variations'])} variations tested")
    
    return sensitivity_results


def calculate_sensitivity_metrics(sensitivity_results):
    """Calculate sensitivity metrics from analysis results.
    
    Args:
        sensitivity_results: Results from run_sensitivity_analysis()
        
    Returns:
        dict: Sensitivity metrics
    """
    if not sensitivity_results or not sensitivity_results.get("variations"):
        return None
    
    baseline_outputs = sensitivity_results["baseline_outputs"]
    if not baseline_outputs:
        return None
    
    baseline_statuses = baseline_outputs.get("option_statuses", {})
    baseline_rankings = baseline_outputs.get("option_rankings", {})
    baseline_benefit_scores = baseline_outputs.get("option_benefit_scores", {})
    
    # Collect all option names
    all_options = set(baseline_statuses.keys())
    
    metrics = {
        "status_changes": {},  # How many times each option changed status
        "ranking_changes": {},  # How many times each option changed rank
        "max_benefit_score_delta": {},  # Maximum change in benefit score for each option
        "total_status_changes": 0,
        "total_ranking_changes": 0,
    }
    
    for option_name in all_options:
        metrics["status_changes"][option_name] = 0
        metrics["ranking_changes"][option_name] = 0
        metrics["max_benefit_score_delta"][option_name] = 0.0
    
    # Analyze each variation
    for variation in sensitivity_results["variations"]:
        outputs = variation.get("outputs", {})
        variation_statuses = outputs.get("option_statuses", {})
        variation_rankings = outputs.get("option_rankings", {})
        variation_benefit_scores = outputs.get("option_benefit_scores", {})
        
        # Check status changes
        for option_name in all_options:
            baseline_status = baseline_statuses.get(option_name, "Unknown")
            variation_status = variation_statuses.get(option_name, "Unknown")
            if baseline_status != variation_status:
                metrics["status_changes"][option_name] += 1
                metrics["total_status_changes"] += 1
        
        # Check ranking changes
        for option_name in all_options:
            baseline_rank = baseline_rankings.get(option_name, 999)
            variation_rank = variation_rankings.get(option_name, 999)
            if baseline_rank != variation_rank:
                metrics["ranking_changes"][option_name] += 1
                metrics["total_ranking_changes"] += 1
        
        # Check benefit score changes
        for option_name in all_options:
            baseline_score = baseline_benefit_scores.get(option_name, 0.0)
            variation_score = variation_benefit_scores.get(option_name, 0.0)
            score_delta = abs(variation_score - baseline_score)
            metrics["max_benefit_score_delta"][option_name] = max(
                metrics["max_benefit_score_delta"][option_name],
                score_delta
            )
    
    # Calculate overall sensitivity score (0-100)
    num_variations = len(sensitivity_results["variations"])
    if num_variations > 0:
        status_change_rate = metrics["total_status_changes"] / (num_variations * len(all_options))
        ranking_change_rate = metrics["total_ranking_changes"] / (num_variations * len(all_options))
        avg_max_score_delta = np.mean(list(metrics["max_benefit_score_delta"].values()))
        
        # Normalize to 0-100 scale
        sensitivity_score = min(100, (status_change_rate * 50 + ranking_change_rate * 30 + avg_max_score_delta * 20) * 100)
        metrics["sensitivity_score"] = sensitivity_score
    else:
        metrics["sensitivity_score"] = 0.0
    
    return metrics


def create_sensitivity_summary_table(sensitivity_results_list):
    """Create a summary table of sensitivity analysis results.
    
    Args:
        sensitivity_results_list: List of sensitivity_results dictionaries
        
    Returns:
        dash_table.DataTable component
    """
    if not sensitivity_results_list:
        return html.Div("No sensitivity analysis results available.")
    
    table_data = []
    for sens_result in sensitivity_results_list:
        metrics = calculate_sensitivity_metrics(sens_result)
        if metrics:
            table_data.append({
                "Parameter": sens_result.get("parameter_display_name", sens_result.get("parameter_name", "Unknown")),
                "Status Changes": metrics.get("total_status_changes", 0),
                "Ranking Changes": metrics.get("total_ranking_changes", 0),
                "Max Score Δ": f"{max(metrics.get('max_benefit_score_delta', {}).values()):.2f}" if metrics.get('max_benefit_score_delta') else "0.00",
                "Sensitivity": f"{metrics.get('sensitivity_score', 0):.1f}",
            })
    
    if not table_data:
        return html.Div("No valid sensitivity results to display.")
    
    df = pd.DataFrame(table_data)
    
    # Sort by sensitivity score
    df["Sensitivity_Num"] = df["Sensitivity"].astype(float)
    df = df.sort_values("Sensitivity_Num", ascending=False)
    df = df.drop("Sensitivity_Num", axis=1)
    
    return dash_table.DataTable(
        id="sensitivity-summary-table",
        columns=[{"name": col, "id": col} for col in df.columns],
        data=df.to_dict('records'),
        style_cell={
            'textAlign': 'left',
            'padding': '8px',
            'fontSize': '12px',
        },
        style_header={
            'backgroundColor': '#007bff',
            'color': 'white',
            'fontWeight': 'bold',
        },
        style_data_conditional=[
            {
                'if': {'filter_query': '{Sensitivity} >= 50'},
                'backgroundColor': '#ffcccc',
            },
            {
                'if': {'filter_query': '{Sensitivity} >= 25 && {Sensitivity} < 50'},
                'backgroundColor': '#fff4cc',
            },
            {
                'if': {'filter_query': '{Sensitivity} < 25'},
                'backgroundColor': '#ccffcc',
            },
        ],
    )


def create_tornado_plot(sensitivity_results, selected_option=None):
    """Create a tornado plot showing parameter impact on benefit scores.
    
    Args:
        sensitivity_results: Results from run_sensitivity_analysis()
        selected_option: Option name to focus on (if None, uses top-ranked option)
        
    Returns:
        plotly.graph_objects.Figure
    """
    if not sensitivity_results or not sensitivity_results.get("variations"):
        return go.Figure()
    
    baseline_outputs = sensitivity_results["baseline_outputs"]
    if not baseline_outputs:
        return go.Figure()
    
    baseline_benefit_scores = baseline_outputs.get("option_benefit_scores", {})
    if not baseline_benefit_scores:
        return go.Figure()
    
    # Select option to analyze
    if selected_option is None:
        selected_option = max(baseline_benefit_scores.items(), key=lambda x: x[1])[0]
    
    baseline_score = baseline_benefit_scores.get(selected_option, 0.0)
    
    # Calculate score deltas for each variation
    score_deltas = []
    param_values = []
    
    for variation in sensitivity_results["variations"]:
        param_value = variation.get("parameter_value")
        outputs = variation.get("outputs", {})
        benefit_scores = outputs.get("option_benefit_scores", {})
        variation_score = benefit_scores.get(selected_option, 0.0)
        
        score_delta = variation_score - baseline_score
        score_deltas.append(score_delta)
        param_values.append(param_value)
    
    # Create tornado plot (bar chart)
    fig = go.Figure()
    
    # Positive deltas (bars to the right)
    positive_deltas = [d if d > 0 else 0 for d in score_deltas]
    negative_deltas = [d if d < 0 else 0 for d in score_deltas]
    
    fig.add_trace(go.Bar(
        x=positive_deltas,
        y=[f"{v:.2f}" if isinstance(v, float) else str(v) for v in param_values],
        orientation='h',
        name='Increase',
        marker_color='green',
        base=baseline_score,
    ))
    
    fig.add_trace(go.Bar(
        x=negative_deltas,
        y=[f"{v:.2f}" if isinstance(v, float) else str(v) for v in param_values],
        orientation='h',
        name='Decrease',
        marker_color='red',
        base=baseline_score,
    ))
    
    param_name = sensitivity_results.get("parameter_display_name", sensitivity_results.get("parameter_name", "Parameter"))
    fig.update_layout(
        title=f"Parameter Impact on {selected_option} Benefit Score",
        xaxis_title="Benefit Score Change",
        yaxis_title=param_name,
        template="plotly_white",
        height=400,
        showlegend=True,
    )
    
    return fig


def create_status_transition_heatmap(sensitivity_results):
    """Create a heatmap showing status changes for each option.
    
    Args:
        sensitivity_results: Results from run_sensitivity_analysis()
        
    Returns:
        plotly.graph_objects.Figure
    """
    if not sensitivity_results or not sensitivity_results.get("variations"):
        return go.Figure()
    
    baseline_outputs = sensitivity_results["baseline_outputs"]
    if not baseline_outputs:
        return go.Figure()
    
    baseline_statuses = baseline_outputs.get("option_statuses", {})
    all_options = list(baseline_statuses.keys())
    
    # Count status changes for each option
    status_change_counts = {option: 0 for option in all_options}
    
    for variation in sensitivity_results["variations"]:
        outputs = variation.get("outputs", {})
        variation_statuses = outputs.get("option_statuses", {})
        
        for option in all_options:
            baseline_status = baseline_statuses.get(option, "Unknown")
            variation_status = variation_statuses.get(option, "Unknown")
            if baseline_status != variation_status:
                status_change_counts[option] += 1
    
    # Create heatmap data
    num_variations = len(sensitivity_results["variations"])
    change_rates = [status_change_counts[option] / num_variations if num_variations > 0 else 0 
                    for option in all_options]
    
    fig = go.Figure(data=go.Heatmap(
        z=[change_rates],
        x=all_options,
        y=["Status Change Rate"],
        colorscale='RdYlGn_r',
        text=[[f"{rate:.1%}" for rate in change_rates]],
        texttemplate='%{text}',
        textfont={"size": 10},
        colorbar=dict(title="Change Rate"),
    ))
    
    param_name = sensitivity_results.get("parameter_display_name", sensitivity_results.get("parameter_name", "Parameter"))
    fig.update_layout(
        title=f"Status Change Frequency by Option ({param_name})",
        xaxis_title="MAR Option",
        yaxis_title="",
        template="plotly_white",
        height=200,
    )
    
    return fig


def setup_decision_sensitivity_callbacks(app):
    """Set up all callbacks for the Decision Sensitivity tab."""
    
    @app.callback(
        [
            Output("sensitivity-parameter-selector", "options"),
            Output("sensitivity-parameter-selector", "value"),
        ],
        [
            Input("analysis-tabs", "active_tab"),
        ],
        prevent_initial_call=False
    )
    def initialize_sensitivity_tab(active_tab):
        """Initialize sensitivity tab with parameter options."""
        if active_tab != "analysis-decision-sensitivity":
            return [], None
        
        # Group parameters by category
        param_options = []
        for param_id, param_def in PARAMETER_DEFINITIONS.items():
            group = param_def.get("group", "Other")
            param_options.append({
                "label": f"{group}: {param_def.get('name', param_id)}",
                "value": param_id,
            })
        
        # Get current selection (if any)
        selected_param = dash_storage.get_data("sensitivity_selected_parameter")
        
        return param_options, selected_param
    
    @app.callback(
        Output("sensitivity-variation-settings", "children"),
        [
            Input("sensitivity-parameter-selector", "value"),
            Input("analysis-tabs", "active_tab"),
        ],
        prevent_initial_call=False
    )
    def update_variation_settings(selected_parameter, active_tab):
        """Update variation settings UI based on selected parameter."""
        # Initialize with default message when tab is first opened
        if active_tab != "analysis-decision-sensitivity":
            return html.Div([
                html.P("Select a parameter above to configure sensitivity analysis.", 
                       className="text-muted small"),
            ])
        
        if not selected_parameter:
            return html.Div([
                html.P("Select a parameter to configure sensitivity analysis.", 
                       className="text-muted small"),
            ])
        
        # Store selection
        dash_storage.set_data("sensitivity_selected_parameter", selected_parameter)
        
        # Get parameter definition
        param_def = PARAMETER_DEFINITIONS.get(selected_parameter, {})
        param_type = param_def.get("type", "numeric")
        baseline_value, _ = get_parameter_baseline(selected_parameter)
        
        if param_type == "categorical":
            allowed_values = param_def.get("allowed_values", [])
            return html.Div([
                html.H6("Parameter Type: Categorical", className="mb-2"),
                html.P(f"Current Value: {baseline_value}", className="small"),
                html.P(f"All {len(allowed_values)} possible values will be tested.", 
                       className="text-muted small"),
            ])
        
        elif param_type == "list":
            list_length = len(baseline_value) if isinstance(baseline_value, list) else 0
            return html.Div([
                html.H6("Parameter Type: List", className="mb-2"),
                html.P(f"Current Value: List with {list_length} elements", className="small"),
                html.P("All elements will be varied by the same percentage.", 
                       className="text-muted small mb-3"),
                dbc.Row([
                    dbc.Col([
                        html.Label("Min Variation (%)", className="small"),
                        dbc.Input(
                            id="sensitivity-min-variation",
                            type="number",
                            value=default_range[0],
                            min=-100,
                            max=100,
                            step=5,
                            className="small",
                        ),
                    ], width=4),
                    dbc.Col([
                        html.Label("Max Variation (%)", className="small"),
                        dbc.Input(
                            id="sensitivity-max-variation",
                            type="number",
                            value=default_range[1],
                            min=-100,
                            max=100,
                            step=5,
                            className="small",
                        ),
                    ], width=4),
                    dbc.Col([
                        html.Label("Number of Points", className="small"),
                        dbc.Input(
                            id="sensitivity-num-points",
                            type="number",
                            value=10,
                            min=3,
                            max=50,
                            step=1,
                            className="small",
                        ),
                    ], width=4),
                ], className="mb-2"),
            ])
        
        elif param_type == "table":
            return html.Div([
                html.H6("Parameter Type: Table", className="mb-2"),
                html.P(f"Table variation is complex and not yet fully implemented.", 
                       className="text-muted small"),
                html.P("Only baseline value will be tested.", className="text-warning small"),
            ])
        
        elif param_type == "boolean":
            return html.Div([
                html.H6("Parameter Type: Boolean", className="mb-2"),
                html.P(f"Current Value: {baseline_value}", className="small"),
                html.P("Both True and False will be tested.", 
                       className="text-muted small"),
            ])
        
        else:  # numeric
            default_range = param_def.get("default_range", (-20, 20))
            unit = param_def.get("unit", "")
            
            return html.Div([
                html.H6("Variation Settings", className="mb-2"),
                html.P(f"Current Value: {baseline_value} {unit}", className="small mb-3"),
                dbc.Row([
                    dbc.Col([
                        html.Label("Min Variation (%)", className="small"),
                        dbc.Input(
                            id="sensitivity-min-variation",
                            type="number",
                            value=default_range[0],
                            min=-100,
                            max=100,
                            step=5,
                            className="small",
                        ),
                    ], width=4),
                    dbc.Col([
                        html.Label("Max Variation (%)", className="small"),
                        dbc.Input(
                            id="sensitivity-max-variation",
                            type="number",
                            value=default_range[1],
                            min=-100,
                            max=100,
                            step=5,
                            className="small",
                        ),
                    ], width=4),
                    dbc.Col([
                        html.Label("Number of Points", className="small"),
                        dbc.Input(
                            id="sensitivity-num-points",
                            type="number",
                            value=10,
                            min=3,
                            max=50,
                            step=1,
                            className="small",
                        ),
                    ], width=4),
                ], className="mb-2"),
            ])
    
    @app.callback(
        [
            Output("sensitivity-results-container", "children"),
            Output("sensitivity-progress", "children"),
        ],
        [
            Input("sensitivity-run-button", "n_clicks"),
        ],
        [
            State("sensitivity-parameter-selector", "value"),
            State("sensitivity-min-variation", "value"),
            State("sensitivity-max-variation", "value"),
            State("sensitivity-num-points", "value"),
        ],
        prevent_initial_call=True
    )
    def run_sensitivity_analysis_callback(n_clicks, selected_parameter, min_var, max_var, num_points):
        """Run sensitivity analysis and display results."""
        if not n_clicks or not selected_parameter:
            return html.Div(), html.Div()
        
        # Get variation settings
        min_var = min_var if min_var is not None else -20
        max_var = max_var if max_var is not None else 20
        num_points = num_points if num_points is not None else 10
        
        variation_range = (min_var, max_var)
        
        # Show progress
        progress_msg = dbc.Alert(
            f"Running sensitivity analysis for {PARAMETER_DEFINITIONS.get(selected_parameter, {}).get('name', selected_parameter)}... This may take a few minutes.",
            color="info",
            className="mb-2",
        )
        
        try:
            # Run analysis
            sensitivity_results = run_sensitivity_analysis(
                selected_parameter,
                variation_range=variation_range,
                num_points=num_points
            )
            
            if not sensitivity_results:
                return html.Div([
                    dbc.Alert("Sensitivity analysis failed. Please check the logs.", color="danger"),
                ]), html.Div()
            
            # Calculate metrics
            metrics = calculate_sensitivity_metrics(sensitivity_results)
            
            # Create visualizations
            tornado_fig = create_tornado_plot(sensitivity_results)
            status_heatmap = create_status_transition_heatmap(sensitivity_results)
            
            # Create results display
            results_container = html.Div([
                html.H5("Sensitivity Analysis Results", className="mb-3"),
                
                # Summary metrics
                dbc.Row([
                    dbc.Col([
                        dbc.Card([
                            dbc.CardBody([
                                html.H6("Total Status Changes", className="card-title small"),
                                html.H3(f"{metrics.get('total_status_changes', 0)}", className="text-primary"),
                            ]),
                        ], className="mb-2"),
                    ], width=3),
                    dbc.Col([
                        dbc.Card([
                            dbc.CardBody([
                                html.H6("Total Ranking Changes", className="card-title small"),
                                html.H3(f"{metrics.get('total_ranking_changes', 0)}", className="text-warning"),
                            ]),
                        ], className="mb-2"),
                    ], width=3),
                    dbc.Col([
                        dbc.Card([
                            dbc.CardBody([
                                html.H6("Sensitivity Score", className="card-title small"),
                                html.H3(f"{metrics.get('sensitivity_score', 0):.1f}", className="text-danger"),
                            ]),
                        ], className="mb-2"),
                    ], width=3),
                    dbc.Col([
                        dbc.Card([
                            dbc.CardBody([
                                html.H6("Variations Tested", className="card-title small"),
                                html.H3(f"{len(sensitivity_results.get('variations', []))}", className="text-info"),
                            ]),
                        ], className="mb-2"),
                    ], width=3),
                ], className="mb-3"),
                
                # Visualizations
                dbc.Row([
                    dbc.Col([
                        dcc.Graph(figure=tornado_fig, id="sensitivity-tornado-plot"),
                    ], width=12, className="mb-3"),
                ]),
                
                dbc.Row([
                    dbc.Col([
                        dcc.Graph(figure=status_heatmap, id="sensitivity-status-heatmap"),
                    ], width=12, className="mb-3"),
                ]),
            ])
            
            # Store results for later use
            dash_storage.set_data(f"sensitivity_results_{selected_parameter}", sensitivity_results)
            
            return results_container, html.Div()
            
        except Exception as e:
            logger.error(f"Error in sensitivity analysis callback: {e}", exc_info=True)
            return html.Div([
                dbc.Alert(f"Error running sensitivity analysis: {str(e)}", color="danger"),
            ]), html.Div()

