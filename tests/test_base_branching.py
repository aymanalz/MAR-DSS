import pytest

from mar_dss.base import Node, DecisionGraph


def b_func(a_value):
    return "B_RAN" if a_value is True else None


def c_func(a_value):
    return "C_RAN" if a_value is False else None


def d_func(b_value):
    return 2 if b_value == "B_RAN" else None


def e_func(c_value):
    return 3 if c_value == "C_RAN" else None


def build_graph():
    g = DecisionGraph()

    # Input node A
    node_a = Node(
        node_id="A",
        input_flag=True,
        name="Input A",
        node_type="boolean",
        value=None,
        leaf_flag=False,
    )

    # Rule node B depends on A; only meaningful if A is True
    node_b = Node(
        node_id="B",
        input_flag=False,
        name="Rule B",
        node_type="categorical",
        dependencies=["A"],
        function=b_func,
        leaf_flag=False,
    )

    # Rule node C depends on A; only meaningful if A is False
    node_c = Node(
        node_id="C",
        input_flag=False,
        name="Rule C",
        node_type="categorical",
        dependencies=["A"],
        function=c_func,
        leaf_flag=False,
    )

    # Node D depends on B and returns value 2 if B branch ran
    node_d = Node(
        node_id="D",
        input_flag=False,
        name="Depends on B -> 2",
        node_type="numeric",
        dependencies=["B"],
        function=d_func,
        leaf_flag=True,
    )

    # Node E depends on C and returns value 3 if C branch ran
    node_e = Node(
        node_id="E",
        input_flag=False,
        name="Depends on C -> 3",
        node_type="numeric",
        dependencies=["C"],
        function=e_func,
        leaf_flag=True,
    )

    g.add_node(node_a)
    g.add_node(node_b)
    g.add_node(node_c)
    g.add_node(node_d)
    g.add_node(node_e)
    return g


def test_branching_A_true():
    g = build_graph()
    inputs = {"A": True}
    
    # Evaluate all rule nodes (includes both leaf and intermediate rule nodes)
    results = g.evaluate(inputs)
    
    # B should run; C should return None
    assert results["B"] == "B_RAN"
    assert results["C"] is None
    # D should be 2 (since B ran); E should be None
    assert results["D"] == 2
    assert results["E"] is None


def test_branching_A_false():
    g = build_graph()
    inputs = {"A": False}
    
    # Evaluate all rule nodes (includes both leaf and intermediate rule nodes)
    results = g.evaluate(inputs)
    
    # C should run; B should return None
    assert results["B"] is None
    assert results["C"] == "C_RAN"
    # E should be 3 (since C ran); D should be None
    assert results["D"] is None
    assert results["E"] == 3


