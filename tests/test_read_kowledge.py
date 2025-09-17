import yaml
from mar_dss.base import Node, DecisionGraph
from pathlib import Path    

def test_read_knowledge():
    """Test function to read knowledge files and create graph."""
    input_fn = "./src/mar_dss/knowledge/input.yaml"
    rules_fn = "./src/mar_dss/knowledge/rules.yaml"
    graph = DecisionGraph()
    graph.from_yamls([str(Path(input_fn).resolve()), str(Path(rules_fn).resolve())])
    return graph

if __name__ == "__main__":
    # Only run when file is executed directly, not when imported
    graph = test_read_knowledge()
    graph.plotly()