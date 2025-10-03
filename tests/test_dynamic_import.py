from mar_dss.base import DecisionGraph, Node


def test_dynamic_import_from_file(tmp_path):
    module_code = (
        "def multiply(x, y):\n"
        "    return x * y\n"
    )
    module_path = tmp_path / "math_rules.py"
    module_path.write_text(module_code, encoding="utf-8")

    graph = DecisionGraph()
    graph.add_node(
        Node(
            node_id="x",
            input_flag=True,
            name="X",
            node_type="numeric",
            leaf_flag=False,
        )
    )
    graph.add_node(
        Node(
            node_id="y",
            input_flag=True,
            name="Y",
            node_type="numeric",
            leaf_flag=False,
        )
    )
    graph.add_node(
        Node(
            node_id="prod",
            input_flag=False,
            name="Product",
            node_type="numeric",
            leaf_flag=True,
            dependencies=["x", "y"],
            module=str(module_path),
            function_name="multiply",
        )
    )

    results = graph.evaluate({"x": 3, "y": 4})
    assert results["prod"] == 12


def test_dynamic_import_by_module_name_unconfined():
    graph = DecisionGraph()
    graph.add_node(
        Node(
            node_id="Dgw",
            input_flag=True,
            name="Depth to GW",
            node_type="numeric",
            leaf_flag=False,
        )
    )
    graph.add_node(
        Node(
            node_id="Dgw_min",
            input_flag=True,
            name="Min Depth",
            node_type="numeric",
            leaf_flag=False,
        )
    )
    graph.add_node(
        Node(
            node_id="Aqtype",
            input_flag=True,
            name="Aquifer Type",
            node_type="categorical",
            leaf_flag=False,
        )
    )
    graph.add_node(
        Node(
            node_id="Ss",
            input_flag=True,
            name="Storage Coef",
            node_type="numeric",
            leaf_flag=False,
        )
    )
    graph.add_node(
        Node(
            node_id="Hmax",
            input_flag=True,
            name="Max Head Change",
            node_type="numeric",
            leaf_flag=False,
        )
    )
    graph.add_node(
        Node(
            node_id="Vs",
            input_flag=False,
            name="Available Storage",
            node_type="numeric",
            leaf_flag=True,
            dependencies=["Dgw", "Dgw_min", "Aqtype", "Ss", "Hmax"],
            module="mar_dss.rules.geohydro_rules",
            function_name="compute_available_storage",
        )
    )

    inputs = {
        "Dgw": 20.0,
        "Dgw_min": 5.0,
        "Aqtype": "unconfined",
        "Ss": 0.15,
        "Hmax": 2.0,
    }
    results = graph.evaluate(inputs)
    assert results["Vs"] == 0.15 * (20.0 - 5.0)


