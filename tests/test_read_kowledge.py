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
    inputs = {}
    inputs["aq_type"] = "Unconfined"
    inputs["stratigraphy_table"]= [[10, 10, 0.1],
                                  [5, 0.1, 0.15],
                                  [50, 30, 0.2],
                                  [200, 50, 0.05]]


    results = graph.evaluate(inputs)
    graph.plotly()
    print(results)
    xx = 1