from pathlib import Path

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


if __name__ == "__main__":
    # Only run when file is executed directly, not when imported
    graph = test_read_knowledge()
    
    # Debug: Check if design_sizing was loaded
    print(f"\nDEBUG - After loading graph:")
    print(f"  Total nodes: {len(graph.nodes)}")
    if "design_sizing" in graph.nodes:
        node = graph.nodes["design_sizing"]
        print(f"  design_sizing found:")
        print(f"    node_id: {node.node_id}")
        print(f"    input_flag: {node.input_flag}")
        print(f"    is_rule(): {node.is_rule()}")
        print(f"    module: {node.module}")
        print(f"    function_name: {node.function_name}")
        print(f"    dependencies: {node.dependencies}")
    else:
        print(f"  design_sizing NOT FOUND in nodes!")
        print(f"  Available nodes: {list(graph.nodes.keys())}")
    
    inputs = {}
    inputs["aq_type"] = "Unconfined"
    inputs["stratigraphy_table"]= [[10, 10, 0.1],
                                  [5, 0.1, 0.15],
                                  [50, 30, 0.2],
                                  [200, 50, 0.05]]
    inputs["monthly_gw_depth"] = [20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20]
    inputs["d_gw_min"] = 5.0
    inputs["max_available_area"] = 1e7
    inputs["source_water_volume"] = [300000, 300000, 300000, 300000, 300000, 300000, 300000, 300000, 300000, 300000, 300000, 300000]


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