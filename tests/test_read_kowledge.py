import yaml
from mar_dss.base import Node, DecisionGraph
from pathlib import Path    

input_fn = "./src/mar_dss/knowledge/input.yaml"
rules_fn = "./src/mar_dss/knowledge/rules.yaml"
graph = DecisionGraph()
graph.from_yamls([str(Path(input_fn).resolve()), str(Path(rules_fn).resolve())])
graph.plotly()
vv = 1