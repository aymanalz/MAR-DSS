from pathlib import Path
import numpy as np
from mar_dss.base import DecisionGraph


def test_read_knowledge():
    """Test function to read knowledge files and create graph."""
    input_fn = "./src/mar_dss/knowledge/input.yaml"
    rules_fn = "./src/mar_dss/knowledge/rules.yaml"
    graph = DecisionGraph()
    graph.from_yamls(
        [str(Path(input_fn).resolve()), str(Path(rules_fn).resolve())]
    )
    return graph

def create_monthly_bell(min_val, max_val, peak_month=6, spread=2.5):
    """
    Create bell curve with peak at specific month.
    
    peak_month: 0=Jan, 5=Jun, 6=Jul, etc.
    spread: controls width (larger = wider bell)
    """
    months = np.arange(12)
    bell = max_val * np.exp(-0.5 * ((months - peak_month) / spread) ** 2)
    # Ensure minimum value at edges
    bell = np.maximum(bell, min_val)
    return bell.tolist()

if __name__ == "__main__":
    # Only run when file is executed directly, not when imported
    graph = test_read_knowledge()
    
    # Debug: Check if design_sizing was loaded
      
    inputs = {}
    inputs["aq_type"] = "Unconfined"
    inputs["stratigraphy_table"]= [[10, 10, 0.1],
                                  [5, 0.1, 0.15],
                                  [50, 30, 0.2],
                                  [200, 50, 0.05]]
    inputs["monthly_gw_depth"] = [20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20]
    inputs["d_gw_min"] = 5.0
    inputs["max_available_area"] = 1e7
    # for an area of 50m by 50 and inf 0.2 m/day. 
    max_source_water_volume = 200 * 200 * 0.2*30*3*3
    source_water_volume = create_monthly_bell(0.2*max_source_water_volume, 
    max_source_water_volume, peak_month=6, spread=2.5)

    inputs["source_water_volume"] = source_water_volume  


    results = graph.evaluate(inputs)
    
    # Debug: Check if design_sizing node exists and its state
    if "design_sizing" in graph.nodes:
        node = graph.nodes["design_sizing"]
        print(f"\nDEBUG - design_sizing node:")
        print(f"  Function loaded: {node.function is not None}")
        print(f"  Function: {node.function}")
        print(f"  Module: {node.module}")
        print(f"  Function name: {node.function_name}")
        print(f"  Dependencies: {node.dependencies}")
        print(f"  Value: {node.value}")
        print(f"  In results: {'design_sizing' in results}")
        if "design_sizing" in results:
            print(f"  Result value: {results['design_sizing']}")
    
    graph.plotly()
    print("\nAll results:")
    print(results)