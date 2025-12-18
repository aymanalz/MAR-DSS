"""
Callbacks for the Analysis tab lazy loading.
"""
from pathlib import Path
import dash
from dash import Input, Output, html
import mar_dss
import mar_dss.app.utils.data_storage as dash_storage
from mar_dss.base import DecisionGraph
import pandas as pd
import os
import hashlib
import json
import numpy as np
# Import all the analysis components
try:
    from mar_dss.app.components.dss_algorithm_tab import create_dss_algorithm_content
    from mar_dss.app.components.decision_sensitivity_tab import create_decision_sensitivity_content
    from mar_dss.app.components.decision_interpretation_tab import create_decision_interpretation_content
    from mar_dss.app.components.scenarios_comparison_tab import create_scenarios_comparison_content
    from mar_dss.app.components.ai_generated_decision_tab import create_ai_generated_decision_content
    from mar_dss.app.components.data_export_tab import create_data_export_content
except ImportError:
    from ..components.dss_algorithm_tab import create_dss_algorithm_content
    from ..components.decision_sensitivity_tab import create_decision_sensitivity_content
    from ..components.decision_interpretation_tab import create_decision_interpretation_content
    from ..components.scenarios_comparison_tab import create_scenarios_comparison_content
    from ..components.ai_generated_decision_tab import create_ai_generated_decision_content
    from ..components.data_export_tab import create_data_export_content

def read_knowledge():
    """Test function to read knowledge files and create graph."""
    # Get the path to the knowledge directory relative to the mar_dss package
    # Find the mar_dss package root
    
    mar_dss_path = Path(mar_dss.__file__).parent
    knowledge_dir = mar_dss_path / "knowledge"
    
    input_fn = knowledge_dir / "input.yaml"
    rules_fn = knowledge_dir / "rules.yaml"
    
    # Check if files exist
    if not input_fn.exists():
        raise FileNotFoundError(f"Knowledge file not found: {input_fn}")
    if not rules_fn.exists():
        raise FileNotFoundError(f"Knowledge file not found: {rules_fn}")
    
    graph = DecisionGraph()
    graph.from_yamls(
        [str(input_fn.resolve()), str(rules_fn.resolve())]
    )
    return graph

def get_session_graph():
    """Get or create the knowledge graph for this session."""
    graph = dash_storage.get_data("decision_graph")
    if graph is None:
        graph = read_knowledge()
        
    return graph

def get_graph_inputs():
    """Get the inputs for the graph."""
    inputs = {}    
    inputs["aq_type"] = dash_storage.get_data("aquifer_type")
    max_infiltration_area = dash_storage.get_data("max_infiltration_area")
    if max_infiltration_area is None:
        max_infiltration_area = 1e7
    else:
        try:
            max_infiltration_area = float(max_infiltration_area)
        except (ValueError, TypeError):
            max_infiltration_area = 1e7
    max_infiltration_area_ft2 = max_infiltration_area * 43560
    if max_infiltration_area_ft2 <= 0:
        max_infiltration_area_ft2 = 1e7
    inputs["max_available_area"] = max_infiltration_area_ft2
    inputs["ground_surface_slope"] = float(dash_storage.get_data("ground_surface_slope")) or 0.0
    start_table = dash_storage.get_data("stratigraphy_data")
    start_df = pd.DataFrame(start_table)
    start_stable = start_df[['thickness', 'conductivity', 'yield']].values.tolist()
    inputs["stratigraphy_table"]= start_stable
    gw_data = pd.DataFrame(dash_storage.get_data("groundwater_data"))
    gs_elevation = dash_storage.get_data("ground_surface_elevation")
    depth_to_gw = float(gs_elevation) - gw_data['elevation'].values
    inputs["monthly_gw_depth"] = depth_to_gw
    source_water_volume = dash_storage.get_data("monthly_flow")
    inputs["source_water_volume"] = source_water_volume
    inputs["d_gw_min"] = 5.0
    return inputs

def create_inputs_hash(inputs):
    """Create a hash from the graph inputs for caching purposes."""
    # Convert inputs to a hashable format
    hashable_data = {}
    
    for key, value in inputs.items():
        if isinstance(value, (np.ndarray, np.generic)):
            # Convert numpy arrays to lists
            hashable_data[key] = value.tolist() if hasattr(value, 'tolist') else float(value)
        elif isinstance(value, (list, tuple)):
            # Ensure lists are hashable (convert nested arrays)
            hashable_data[key] = [
                [float(x) if isinstance(x, (np.generic, np.ndarray)) else x for x in row] 
                if isinstance(row, (list, tuple, np.ndarray)) 
                else (float(row) if isinstance(row, (np.generic, np.ndarray)) else row)
                for row in value
            ]
        elif isinstance(value, (int, float, str, bool, type(None))):
            hashable_data[key] = value
        else:
            # For other types, convert to string representation
            hashable_data[key] = str(value)
    
    # Create a JSON string from the hashable data (sorted for consistency)
    json_str = json.dumps(hashable_data, sort_keys=True, default=str)
    
    # Generate MD5 hash
    hash_obj = hashlib.md5(json_str.encode('utf-8'))
    return hash_obj.hexdigest()

def calculate_feasibility_score(selected_technology, graph=None):
    """Calculate overall feasibility score based on selected technology and site conditions."""
    if selected_technology is None:
        return 0
    
    if graph is None:
        graph = dash_storage.get_data("decision_graph")
    
    if graph is None:
        # If no graph, return a default score based on technology
        default_scores = {
            "spreading_basins": 60,
            "injection_wells": 65,
            "dry_wells": 55,
        }
        return default_scores.get(selected_technology, 50)
    
    try:
        # Base score starts at 50%
        base_score = 50.0
        
        # Get aquifer type from storage (it's an input, not a computed node)
        aq_type = dash_storage.get_data("aquifer_type")
        if aq_type is None:
            # Try to get from graph node values as fallback
            node_values = graph.get_node_values()
            aq_type = node_values.get('aq_type', '')
        
        # Normalize aquifer type
        if aq_type:
            aq_type = str(aq_type).lower()
        else:
            aq_type = ''
            # Default to unconfined if not specified
            base_score = 60  # Default score when aquifer type unknown
        
        # Get node values from decision graph for other parameters
        # Ensure graph is evaluated first
        try:
            inputs = get_graph_inputs()
            graph.evaluate(inputs)  # Ensure graph is evaluated
        except Exception as eval_error:
            print(f"Warning: Could not evaluate graph in calculate_feasibility_score: {eval_error}")
        
        node_values = graph.get_node_values()
        
        print(f"Debug - aq_type: {aq_type}, selected_tech: {selected_technology}")
        print(f"Debug - node_values keys: {list(node_values.keys())[:10]}")  # Print first 10 keys
        
        # Technology-specific scoring adjustments
        if selected_technology == "spreading_basins":
            if aq_type == "unconfined":
                surface_recharge = node_values.get('surface_recharge_suitability')
                if surface_recharge:
                    base_score += 25
                else:
                    base_score += 10  # Conditionally feasible
            else:
                base_score = 0  # Infeasible for confined
        
        elif selected_technology == "injection_wells":
            if aq_type == "confined":
                confined_rechargability = node_values.get('confined_rechargability', 100)
                leakage = node_values.get('leakage_significance', '')
                
                if confined_rechargability >= 50 and leakage == "low":
                    base_score += 30
                elif confined_rechargability >= 50 or leakage == "low":
                    base_score += 15  # Conditionally feasible
                else:
                    base_score += 5
            else:
                base_score += 20  # Works for unconfined but less ideal
        
        elif selected_technology == "dry_wells":
            if aq_type == "unconfined":
                base_score += 25
            else:
                base_score = 0  # Infeasible for confined
        
        # Cap score between 0 and 100
        score = max(0, min(100, base_score))
        
        return round(score)
    except Exception as e:
        print(f"Error calculating feasibility score: {e}")
        return 0

def calculate_project_cost_range(selected_technology):
    """Calculate project cost range based on selected technology."""
    if selected_technology is None:
        return "$0 - $0"
    
    try:
        # Get stored cost data if available
        capital_cost = dash_storage.get_data("capital_cost_num")
        
        if capital_cost is not None:
            # Use actual calculated cost with ±20% range
            low_cost = capital_cost * 0.8
            high_cost = capital_cost * 1.2
            
            # Format in millions
            if low_cost >= 1000000:
                low_str = f"${low_cost/1000000:.1f}M"
            else:
                low_str = f"${low_cost/1000:.0f}K"
            
            if high_cost >= 1000000:
                high_str = f"${high_cost/1000000:.1f}M"
            else:
                high_str = f"${high_cost/1000:.0f}K"
            
            return f"{low_str} - {high_str}"
        
        # Default cost ranges by technology type (if no calculation available)
        default_costs = {
            "spreading_basins": (1.5, 3.0),
            "injection_wells": (2.5, 4.5),
            "dry_wells": (1.0, 2.5),
        }
        
        cost_range = default_costs.get(selected_technology, (2.0, 4.0))
        return f"${cost_range[0]:.1f}M - ${cost_range[1]:.1f}M"
        
    except Exception as e:
        print(f"Error calculating project cost: {e}")
        return "$0 - $0"

def run_feasibility_analysis():
    """Run the feasibility analysis only if inputs have changed (hash-based caching)."""
    # Get current inputs
    inputs = get_graph_inputs()
    
    # Create hash of current inputs
    current_hash = create_inputs_hash(inputs)
    
    # Get the last stored hash
    last_hash = dash_storage.get_data("feasibility_analysis_hash")
    
    # Check if inputs have changed
    if current_hash == last_hash and last_hash is not None:
        # Inputs haven't changed, skip analysis
        print("Feasibility analysis skipped - inputs unchanged (hash match)")
        # Still return the existing graph if available
        graph = dash_storage.get_data("decision_graph")
        if graph is None:
            # If no graph exists, we need to create one
            graph = get_session_graph()
            dash_storage.set_data("decision_graph", graph)
        return 1
    
    # Inputs have changed, run the analysis
    print(f"Feasibility analysis running - inputs changed (hash: {current_hash[:8]}...)")
    
    graph = get_session_graph()
    results = graph.evaluate(inputs)
    dash_storage.set_data("decision_graph", graph)
    
    # Store the new hash for next time
    dash_storage.set_data("feasibility_analysis_hash", current_hash)
    
    print("\nAll results:")
    #graph.plotly()

    
    return 1

def setup_analysis_callbacks(app):
    """Set up callbacks for lazy loading analysis tab content."""
    
    # Callback to initialize knowledge graph when Analysis tab is accessed
    @app.callback(
        Output("knowledge-graph-store", "data"),
        [Input("top-tabs", "active_tab")],
        prevent_initial_call=False
    )
    def initialize_knowledge_graph(active_tab):
        """Initialize knowledge graph when Analysis tab is accessed."""
        if active_tab == "analysis":
            # Initialize the graph and store in data_storage
            graph = read_knowledge()
            dash_storage.set_data("decision_graph", graph)
            return {"initialized": True}
        return dash.no_update
    
    # Callback to update title and print when Analysis tab or Feasibility Summary tab is selected
    @app.callback(
        [Output("feasibility-summary-title", "children"),
         Output("knowledge-graph-store", "data", allow_duplicate=True)],
        [Input("top-tabs", "active_tab"),
         Input("analysis-tabs", "active_tab")],
        prevent_initial_call='initial_duplicate'
    )
    def handle_feasibility_summary_tab(top_tab, analysis_tab):
        """Handle when Analysis tab or Feasibility Summary tab is selected."""


        # Trigger when Analysis tab is selected OR when Feasibility Summary sub-tab is selected
        if top_tab == "analysis" or analysis_tab == "analysis-dashboard":
            run_feasibility_analysis()
            # Get project name from data_storage
            project_name = dash_storage.get_data("project_name") or ""
            # Update title with project name
            if project_name:
                title = f"Feasible MAR Technologies - {project_name}"
            else:
                title = "Feasible MAR Technologies"
            return title, dash.no_update
        return dash.no_update, dash.no_update
    
    # Callback to populate feasible, conditionally feasible, and infeasible technology cards based on analysis results
    @app.callback(
        [Output("feasible-technologies-container", "children"),
         Output("conditionally-feasible-technologies-container", "children"),
         Output("infeasible-technologies-container", "children")],
        [Input("top-tabs", "active_tab"),
         Input("analysis-tabs", "active_tab"),
         Input("knowledge-graph-store", "data")],
        prevent_initial_call=False
    )
    def populate_technology_cards(top_tab, analysis_tab, graph_store):
        """Populate feasible, conditionally feasible, and infeasible technology cards based on decision graph results."""
        import dash_bootstrap_components as dbc
        
        # Default technology list with labels
        all_technologies = {
            #"asr": "Aquifer Storage and Recovery (ASR)",
            #"infiltration_basins": "Infiltration Basins",
            #"sand_dams": "Sand Dams",
            #"check_dams": "Check Dams",
            #"percolation_ponds": "Percolation Ponds",
            #"recharge_wells": "Recharge Wells",
            "spreading_basins": "Spreading Basins",
            "injection_wells": "Injection Wells",
            "dry_wells": "Dry Wells",
            # "urban_stormwater_recharge": "Urban Stormwater Recharge",
            # "riverbank_filtration": "Riverbank Filtration",
            # "dune_infiltration": "Dune Infiltration",
            # "artificial_recharge_wells": "Artificial Recharge Wells",
            # "coastal_aquifer_recharge": "Coastal Aquifer Recharge",
            # "mountain_recharge_systems": "Mountain Recharge Systems",
            # "industrial_wastewater_recharge": "Industrial Wastewater Recharge"
        }
        
        # Default: assume all basic technologies are feasible, advanced ones are infeasible
        default_feasible = ["spreading_basins", "injection_wells", "dry_wells"]        
        default_conditionally_feasible = []
        default_infeasible = []
        
        feasible_list = default_feasible.copy()
        conditionally_feasible_list = default_conditionally_feasible.copy()
        infeasible_list = default_infeasible.copy()
        
        # Try to extract feasible technologies from decision graph
        try:
            graph = dash_storage.get_data("decision_graph")
            if graph is not None:
                # Get all node values
                if (graph.get_node_value('aq_type')).lower()== "unconfined":
                    if not graph.get_node_value('surface_recharge_suitability'):                       
                        feasible_list.remove("spreading_basins")
                        conditionally_feasible_list.append("spreading_basins")
                    
                else: # confined aquifer
                    feasible_list.remove("spreading_basins")
                    infeasible_list.append("spreading_basins")
                    feasible_list.remove("dry_wells")
                    infeasible_list.append("dry_wells")

                    if graph.get_node_value('confined_rechargability')< 50:
                        feasible_list.remove("injection_wells")
                        conditionally_feasible_list.append("injection_wells")
                    
                    if not (graph.get_node_value('leakage_significance') == "low"):
                        feasible_list.remove("injection_wells")
                        conditionally_feasible_list.append("injection_wells")                   
               
                
            
        except Exception as e:
            print(f"Error extracting feasible technologies from graph: {e}")
            # Use default lists on error
        
        # Create feasible technologies RadioItems
        feasible_options = [
            {"label": all_technologies.get(tech, tech.replace("_", " ").title()), "value": tech}
            for tech in feasible_list if tech in all_technologies
        ]
        
        feasible_content = dbc.RadioItems(
            id="feasible-technologies",
            options=feasible_options,
            value=None,
            inline=False,
            className="mb-3"
        )
        
        # Create conditionally feasible technologies RadioItems
        conditionally_feasible_options = [
            {"label": all_technologies.get(tech, tech.replace("_", " ").title()), "value": tech}
            for tech in conditionally_feasible_list if tech in all_technologies
        ]
        
        conditionally_feasible_content = dbc.RadioItems(
            id="conditionally-feasible-technologies",
            options=conditionally_feasible_options,
            value=None,
            inline=False,
            className="mb-3"
        ) if conditionally_feasible_options else html.P("No conditionally feasible technologies identified.", className="text-muted")
        
        # Create infeasible technologies list
        infeasible_items = [
            html.Li(all_technologies.get(tech, tech.replace("_", " ").title()), className="mb-2")
            for tech in infeasible_list if tech in all_technologies
        ]
        
        infeasible_content = html.Ul(
            infeasible_items,
            className="mb-3"
        ) if infeasible_items else html.P("No infeasible technologies identified.", className="text-muted")
        
        return feasible_content, conditionally_feasible_content, infeasible_content
    
    # Callback for MAR technology selection - activated when RadioItem is selected in Feasible MAR Technologies
    @app.callback(
        [Output("technology-selection-feedback", "children"),
         Output("conditionally-feasible-technologies", "value", allow_duplicate=True),
         Output("overall-feasibility-score", "children", allow_duplicate=True),
         Output("total-project-cost", "children", allow_duplicate=True)],
        [Input("feasible-technologies", "value")],
        prevent_initial_call='False'
    )
    def handle_technology_selection(selected_technology):
        """Handle technology selection from Feasible MAR Technologies RadioItems."""
        import dash_bootstrap_components as dbc
        
        if selected_technology:
            # Save selected technology to data storage
            dash_storage.set_data("selected_mar_technology", selected_technology)
            dash_storage.set_data("is_conditionally_feasible", False)
            
            # Format the technology name for display
            tech_name = selected_technology.replace('_', ' ').title()
            
            # Create success alert
            feedback = dbc.Alert(
                [
                    html.Strong(f"✅ {tech_name} selected"),
                    html.Br(),
                    html.Small("This technology has been saved for your analysis.", className="text-muted")
                ],
                color="success",
                className="mb-0"
            )
            
            print(f"Selected MAR Technology: {selected_technology}")
            # Clear conditionally feasible selection when feasible is selected
            run_feasibility_analysis()
            
            # Calculate and update feasibility score and cost
            graph = dash_storage.get_data("decision_graph")
            feasibility_score = calculate_feasibility_score(selected_technology, graph)
            cost_range = calculate_project_cost_range(selected_technology)
            
            print(f"DEBUG - Calculated feasibility score: {feasibility_score}%")
            print(f"DEBUG - Calculated cost range: {cost_range}")
            print(f"DEBUG - Graph available: {graph is not None}")
            
            feasibility_score_text = f"Overall Feasibility Score: {feasibility_score}%"
            cost_text = f"Total Project Cost: {cost_range}"
            
            print(f"DEBUG - Returning score text: {feasibility_score_text}")
            print(f"DEBUG - Returning cost text: {cost_text}")
            
            return feedback, None, feasibility_score_text, cost_text
        else:
            # No selection
            dash_storage.set_data("selected_mar_technology", None)
            dash_storage.set_data("is_conditionally_feasible", False)
            return html.Div(), dash.no_update, "Overall Feasibility Score: 0%", "Total Project Cost: $0 - $0"
    
    # Callback for MAR technology selection - activated when RadioItem is selected in Conditionally Feasible MAR Technologies
    @app.callback(
        [Output("technology-selection-feedback", "children", allow_duplicate=True),
         Output("feasible-technologies", "value", allow_duplicate=True),
         Output("overall-feasibility-score", "children", allow_duplicate=True),
         Output("total-project-cost", "children", allow_duplicate=True)],
        [Input("conditionally-feasible-technologies", "value")],
        prevent_initial_call=True
    )
    def handle_conditionally_feasible_selection(selected_technology):
        """Handle technology selection from Conditionally Feasible MAR Technologies RadioItems."""
        import dash_bootstrap_components as dbc
        
        if selected_technology:
            # Save selected technology to data storage
            dash_storage.set_data("selected_mar_technology", selected_technology)
            dash_storage.set_data("is_conditionally_feasible", True)
            
            # Format the technology name for display
            tech_name = selected_technology.replace('_', ' ').title()
            
            # Create warning alert for conditionally feasible
            feedback = dbc.Alert(
                [
                    html.Strong(f"⚠️ {tech_name} selected (Conditionally Feasible)"),
                    html.Br(),
                    html.Small("This technology may be feasible with certain conditions or modifications.", className="text-muted")
                ],
                color="warning",
                className="mb-0"
            )
            
            print(f"Selected MAR Technology: {selected_technology} (Conditionally Feasible)")
            # Clear feasible selection when conditionally feasible is selected
            run_feasibility_analysis()
            
            # Calculate and update feasibility score and cost
            graph = dash_storage.get_data("decision_graph")
            feasibility_score = calculate_feasibility_score(selected_technology, graph)
            cost_range = calculate_project_cost_range(selected_technology)
            
            print(f"Calculated feasibility score: {feasibility_score}%")
            print(f"Calculated cost range: {cost_range}")
            
            feasibility_score_text = f"Overall Feasibility Score: {feasibility_score}%"
            cost_text = f"Total Project Cost: {cost_range}"
            
            return feedback, None, feasibility_score_text, cost_text
        else:
            # No selection
            dash_storage.set_data("selected_mar_technology", None)
            dash_storage.set_data("is_conditionally_feasible", False)
            return html.Div(), dash.no_update, "Overall Feasibility Score: 0%", "Total Project Cost: $0 - $0"
    
    # Callback to update feasibility score and cost when analysis runs or dashboard loads
    @app.callback(
        [Output("overall-feasibility-score", "children", allow_duplicate=True),
         Output("total-project-cost", "children", allow_duplicate=True)],
        [Input("top-tabs", "active_tab"),
         Input("analysis-tabs", "active_tab"),
         Input("knowledge-graph-store", "data")],
        prevent_initial_call='initial_duplicate'
    )
    def update_feasibility_metrics(top_tab, analysis_tab, graph_store):
        """Update feasibility score and cost when analysis runs or dashboard is accessed."""
        # Only update if we're on the analysis tab
        if top_tab != "analysis":
            return dash.no_update, dash.no_update
        
        # Get selected technology
        selected_technology = dash_storage.get_data("selected_mar_technology")
        
        if selected_technology:
            # Calculate and update feasibility score and cost
            graph = dash_storage.get_data("decision_graph")
            feasibility_score = calculate_feasibility_score(selected_technology, graph)
            cost_range = calculate_project_cost_range(selected_technology)
            
            feasibility_score_text = f"Overall Feasibility Score: {feasibility_score}%"
            cost_text = f"Total Project Cost: {cost_range}"
            
            return feasibility_score_text, cost_text
        else:
            # No technology selected
            return "Overall Feasibility Score: 0%", "Total Project Cost: $0 - $0"
    
    @app.callback(
        Output("analysis-dss-algorithm-content", "children"),
        [Input("analysis-tabs", "active_tab")],
        prevent_initial_call=True
    )
    def load_dss_algorithm_content(active_tab):
        if active_tab == "analysis-dss-algorithm":
            return create_dss_algorithm_content()
        return "Loading..."
    
    @app.callback(
        Output("analysis-decision-sensitivity-content", "children"),
        [Input("analysis-tabs", "active_tab")],
        prevent_initial_call=True
    )
    def load_decision_sensitivity_content(active_tab):
        if active_tab == "analysis-decision-sensitivity":
            return create_decision_sensitivity_content()
        return "Loading..."
    
    @app.callback(
        Output("analysis-decision-interpretation-content", "children"),
        [Input("analysis-tabs", "active_tab")],
        prevent_initial_call=True
    )
    def load_decision_interpretation_content(active_tab):
        if active_tab == "analysis-decision-interpretation":
            return create_decision_interpretation_content()
        return "Loading..."
    
    @app.callback(
        Output("analysis-scenarios-comparison-content", "children"),
        [Input("analysis-tabs", "active_tab")],
        prevent_initial_call=True
    )
    def load_scenarios_comparison_content(active_tab):
        if active_tab == "analysis-scenarios-comparison":
            return create_scenarios_comparison_content()
        return "Loading..."
    
    @app.callback(
        Output("analysis-ai-decision-content", "children"),
        [Input("analysis-tabs", "active_tab")],
        prevent_initial_call=True
    )
    def load_ai_decision_content(active_tab):
        if active_tab == "analysis-ai-decision":
            return create_ai_generated_decision_content()
        return "Loading..."
    
    @app.callback(
        Output("analysis-data-export-content", "children"),
        [Input("analysis-tabs", "active_tab")],
        prevent_initial_call=True
    )
    def load_data_export_content(active_tab):
        if active_tab == "analysis-data-export":
            return create_data_export_content()
        return "Loading..."
