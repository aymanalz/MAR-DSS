
from mar_dss.base import Node, DecisionGraph
import yaml

def test_node_default_values():
    node = Node(
        node_id="X",
        input_flag=True,
        name="Default Node",
        node_type="numeric"
    )
    assert node.leaf_flag is True
    assert node.description is None
    assert node.value is None
    assert node.default is None
    assert node.range is None
    assert node.allowed_values is None
    assert node.certainty == 1.0
    assert node.group is None
    assert node.dependencies == []
    assert node.module is None
    assert node.function is None

def test_decision_graph_add_and_get_node():
    graph = DecisionGraph()
    node = Node(
        node_id="A",
        input_flag=True,
        name="Input A",
        node_type="numeric"
    )
    graph.add_node(node)
    assert graph.get_node("A") is node
    assert graph.get_node("B") is None

def test_decision_graph_evaluate_simple():
    graph = DecisionGraph()
    node1 = Node(
        node_id="A",
        input_flag=True,
        name="Input A",
        node_type="numeric"
    )
    node2 = Node(
        node_id="B",
        input_flag=False,
        name="Rule B",
        node_type="numeric",
        dependencies=["A"],
        function=lambda x: x * 2
    )
    graph.add_node(node1)
    graph.add_node(node2)
    result = graph.evaluate({"A": 3})
    assert result["A"] == 3
    assert result["B"] == 6

def test_decision_graph_evaluate_with_defaults():
    graph = DecisionGraph()
    node1 = Node(
        node_id="A",
        input_flag=True,
        name="Input A",
        node_type="numeric",
        value=7
    )
    node2 = Node(
        node_id="B",
        input_flag=False,
        name="Rule B",
        node_type="numeric",
        dependencies=["A"],
        function=lambda x: x + 1
    )
    graph.add_node(node1)
    graph.add_node(node2)
    result = graph.evaluate({})
    assert result["A"] == 7
    assert result["B"] == 8

def test_decision_graph_evaluate_multiple_dependencies():
    graph = DecisionGraph()
    node1 = Node(
        node_id="A",
        input_flag=True,
        name="Input A",
        node_type="numeric"
    )
    node2 = Node(
        node_id="B",
        input_flag=True,
        name="Input B",
        node_type="numeric"
    )
    node3 = Node(
        node_id="C",
        input_flag=False,
        name="Sum",
        node_type="numeric",
        dependencies=["A", "B"],
        function=lambda x, y: x + y
    )
    graph.add_node(node1)
    graph.add_node(node2)
    graph.add_node(node3)
    result = graph.evaluate({"A": 2, "B": 5})
    assert result["C"] == 7

def test_decision_graph_evaluate_rule_without_function_returns_value():
    graph = DecisionGraph()
    node = Node(
        node_id="X",
        input_flag=False,
        name="Constant",
        node_type="numeric",
        value=123
    )
    graph.add_node(node)
    result = graph.evaluate({})
    assert result["X"] == 123

def test_decision_graph_evaluate_missing_input_uses_node_value():
    graph = DecisionGraph()
    node = Node(
        node_id="A",
        input_flag=True,
        name="Input A",
        node_type="numeric",
        value=55
    )
    graph.add_node(node)
    result = graph.evaluate({})
    assert result["A"] == 55

def test_decision_graph_from_yamls(tmp_path):

    yaml_content = [
        {
            "id": "A",
            "input": True,
            "name": "Input A",
            "type": "numeric",
            "value": 10
        },
        {
            "id": "B",
            "input": False,
            "name": "Rule B",
            "type": "numeric",
            "dependencies": ["A"],
            "value": 20
        }
    ]
    yaml_file = tmp_path / "nodes.yaml"
    yaml_file.write_text(yaml.dump(yaml_content))
    graph = DecisionGraph()
    graph.from_yamls([str(yaml_file)])
    assert "A" in graph.nodes
    assert "B" in graph.nodes
    assert graph.nodes["A"].name == "Input A"
    assert graph.nodes["B"].dependencies == ["A"]
    graph.plot()
    v = 1
