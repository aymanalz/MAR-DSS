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

def run_feasibility_analysis():
    """Run the feasibility analysis."""
    graph = get_session_graph()
    inputs = get_graph_inputs()
    results = graph.evaluate(inputs)
    dash_storage.set_data("decision_graph", graph)

    
    print("\nAll results:")
    graph.plotly()

    
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
                    
                    # if not graph['dry_wells_suitability']:
                    #     feasible_list.remove("dry_wells")
                    #     default_conditionally_feasible.append("dry_wells")
                
                
            
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
    
    # Callback for MAR technology selection - only feasible technologies are selectable
    @app.callback(
        [Output("selected-feasible", "children"),
         Output("selected-infeasible", "children"),
         Output("selection-validation", "children"),
         Output("selection-validation", "color"),
         Output("generate-report-btn", "disabled")],
        [Input("feasible-technologies", "value")],
        prevent_initial_call=True
    )
    def handle_technology_selection(feasible_selection):
        # Update display texts
        if feasible_selection:
            feasible_text = f"✅ {feasible_selection.replace('_', ' ').title()}"
            infeasible_text = "❌ All infeasible technologies listed below"
            validation_text = "✅ Feasible technology selected. Ready to proceed!"
            validation_color = "success"
            button_disabled = False
        else:
            feasible_text = "None selected"
            infeasible_text = "❌ All infeasible technologies listed below"
            validation_text = "Please select a feasible technology to proceed."
            validation_color = "warning"
            button_disabled = True
        
        return (feasible_text, infeasible_text, validation_text, validation_color, button_disabled)
    
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
