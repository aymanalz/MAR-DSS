import pytest

from mar_dss.base import Node


def test_node_init_and_attributes():
    node = Node(
        node_id="Ks",
        input_flag=True,
        name="Hydraulic Conductivity",
        node_type="numeric",
        leaf_flag=True,
        description="Soil hydraulic conductivity",
        value=10.0,
        default=5.0,
        range_=[0.1, 100.0],
        allowed_values=None,
        certainty=0.9,
        group="soil",
        dependencies=None,
        module=None,
        function=None,
    )
    assert node.node_id == "Ks"
    assert node.input_flag is True
    assert node.name == "Hydraulic Conductivity"
    assert node.node_type == "numeric"
    assert node.leaf_flag is True
    assert node.description == "Soil hydraulic conductivity"
    assert node.value == 10.0
    assert node.default == 5.0
    assert node.range == [0.1, 100.0]
    assert node.allowed_values is None
    assert node.certainty == 0.9
    assert node.group == "soil"
    assert node.dependencies == []
    assert node.module is None
    assert node.function is None


def test_is_input_and_is_rule():
    input_node = Node(
        node_id="A", input_flag=True, name="Input A", node_type="numeric"
    )
    rule_node = Node(
        node_id="B", input_flag=False, name="Rule B", node_type="numeric"
    )
    assert input_node.is_input() is True
    assert input_node.is_rule() is False
    assert rule_node.is_input() is False
    assert rule_node.is_rule() is True


def test_evaluate_input_node_returns_value():
    node = Node(
        node_id="A",
        input_flag=True,
        name="Input A",
        node_type="numeric",
        value=42,
    )
    assert node.evaluate({}) == 42


def test_evaluate_rule_node_with_function():
    def add(x, y):
        return x + y

    node = Node(
        node_id="C",
        input_flag=False,
        name="Sum",
        node_type="numeric",
        dependencies=["A", "B"],
        function=add,
    )
    inputs = {"A": 2, "B": 3}
    assert node.evaluate(inputs) == 5


def test_evaluate_rule_node_without_function_returns_value():
    node = Node(
        node_id="D",
        input_flag=False,
        name="Constant",
        node_type="numeric",
        value=99,
    )
    assert node.evaluate({}) == 99


def test_evaluate_rule_node_with_missing_dependencies_raises_keyerror():
    def add(x, y):
        return x + y

    node = Node(
        node_id="E",
        input_flag=False,
        name="Sum",
        node_type="numeric",
        dependencies=["A", "B"],
        function=add,
    )
    with pytest.raises(KeyError):
        node.evaluate({"A": 1})  # "B" is missing
