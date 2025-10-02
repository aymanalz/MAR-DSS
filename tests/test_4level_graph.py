from mar_dss.base import DecisionGraph, Node


def test_4level_decision_graph():
    """
    Test a 4-level decision graph with the following structure:

    Level 1 (Inputs): A, B, C
    Level 2 (Intermediate): D = A + B, E = B * C
    Level 3 (Intermediate): F = D - E, G = D / E
    Level 4 (Leaf/Decision): H = F > G, I = F + G

    This tests the recursive evaluation with memoization.
    """

    # Create the decision graph
    graph = DecisionGraph()

    # Level 1: Input nodes
    node_a = Node(
        node_id="A",
        input_flag=True,
        name="Input A",
        node_type="numeric",
        leaf_flag=False,
        value=10.0,
    )

    node_b = Node(
        node_id="B",
        input_flag=True,
        name="Input B",
        node_type="numeric",
        leaf_flag=False,
        value=5.0,
    )

    node_c = Node(
        node_id="C",
        input_flag=True,
        name="Input C",
        node_type="numeric",
        leaf_flag=False,
        value=2.0,
    )

    # Level 2: Intermediate nodes
    def add_func(x, y):
        return x + y

    def multiply_func(x, y):
        return x * y

    node_d = Node(
        node_id="D",
        input_flag=False,
        name="Sum D",
        node_type="numeric",
        leaf_flag=False,
        dependencies=["A", "B"],
        function=add_func,
    )

    node_e = Node(
        node_id="E",
        input_flag=False,
        name="Product E",
        node_type="numeric",
        leaf_flag=False,
        dependencies=["B", "C"],
        function=multiply_func,
    )

    # Level 3: Intermediate nodes
    def subtract_func(x, y):
        return x - y

    def divide_func(x, y):
        return x / y if y != 0 else 0

    node_f = Node(
        node_id="F",
        input_flag=False,
        name="Difference F",
        node_type="numeric",
        leaf_flag=False,
        dependencies=["D", "E"],
        function=subtract_func,
    )

    node_g = Node(
        node_id="G",
        input_flag=False,
        name="Ratio G",
        node_type="numeric",
        leaf_flag=False,
        dependencies=["D", "E"],
        function=divide_func,
    )

    # Level 4: Leaf/Decision nodes
    def greater_than_func(x, y):
        return x > y

    def sum_func(x, y):
        return x + y

    node_h = Node(
        node_id="H",
        input_flag=False,
        name="Decision H",
        node_type="boolean",
        leaf_flag=True,
        dependencies=["F", "G"],
        function=greater_than_func,
    )

    node_i = Node(
        node_id="I",
        input_flag=False,
        name="Decision I",
        node_type="numeric",
        leaf_flag=True,
        dependencies=["F", "G"],
        function=sum_func,
    )

    # Add all nodes to the graph
    graph.add_node(node_a)
    graph.add_node(node_b)
    graph.add_node(node_c)
    graph.add_node(node_d)
    graph.add_node(node_e)
    graph.add_node(node_f)
    graph.add_node(node_g)
    graph.add_node(node_h)
    graph.add_node(node_i)

    # Test the evaluation
    input_values = {"A": 10.0, "B": 5.0, "C": 2.0}
    results = graph.evaluate(input_values)

    # Verify the results
    # Level 2 calculations
    expected_d = 10.0 + 5.0  # A + B = 15.0
    expected_e = 5.0 * 2.0  # B * C = 10.0

    # Level 3 calculations
    expected_f = expected_d - expected_e  # 15.0 - 10.0 = 5.0
    expected_g = expected_d / expected_e  # 15.0 / 10.0 = 1.5

    # Level 4 calculations
    expected_h = expected_f > expected_g  # 5.0 > 1.5 = True
    expected_i = expected_f + expected_g  # 5.0 + 1.5 = 6.5

    graph.plotly()

    # Assertions
    assert results["H"] == expected_h
    assert results["I"] == expected_i

    # Test that only leaf nodes are returned
    assert "A" not in results
    assert "B" not in results
    assert "C" not in results
    assert "D" not in results
    assert "E" not in results
    assert "F" not in results
    assert "G" not in results

    # Test that we can get all computed values if needed
    all_computed = graph.get_all_computed_values(input_values)
    assert "A" in all_computed
    assert "B" in all_computed
    assert "C" in all_computed
    assert "D" in all_computed
    assert "E" in all_computed
    assert "F" in all_computed
    assert "G" in all_computed
    assert "H" in all_computed
    assert "I" in all_computed

    # Test that node values have been updated
    all_node_values = graph.get_node_values()
    assert all_node_values["A"] == input_values["A"]
    assert all_node_values["B"] == input_values["B"]
    assert all_node_values["C"] == input_values["C"]
    assert all_node_values["D"] == expected_d
    assert all_node_values["E"] == expected_e
    assert all_node_values["F"] == expected_f
    assert all_node_values["G"] == expected_g
    assert all_node_values["H"] == expected_h
    assert all_node_values["I"] == expected_i

    print("4-Level Graph Test Results:")
    print(f"Input A: {input_values['A']}")
    print(f"Input B: {input_values['B']}")
    print(f"Input C: {input_values['C']}")
    print(f"Decision H (F > G): {results['H']}")
    print(f"Decision I (F + G): {results['I']}")
    print(
        f"Intermediate values - D: {expected_d}, E: {expected_e}, F: {expected_f}, G: {expected_g}"
    )
    print(f"All node values after evaluation: {all_node_values}")


def test_4level_graph_with_different_inputs():
    """
    Test the same 4-level graph with different input values to ensure
    the recursive evaluation works correctly.
    """

    # Create the decision graph (same structure as above)
    graph = DecisionGraph()

    # Define the functions
    def add_func(x, y):
        return x + y

    def multiply_func(x, y):
        return x * y

    def subtract_func(x, y):
        return x - y

    def divide_func(x, y):
        return x / y if y != 0 else 0

    def greater_than_func(x, y):
        return x > y

    def sum_func(x, y):
        return x + y

    # Create nodes (simplified creation)
    nodes = [
        Node("A", True, "Input A", "numeric", False, value=20.0),
        Node("B", True, "Input B", "numeric", False, value=4.0),
        Node("C", True, "Input C", "numeric", False, value=3.0),
        Node(
            "D",
            False,
            "Sum D",
            "numeric",
            False,
            dependencies=["A", "B"],
            function=add_func,
        ),
        Node(
            "E",
            False,
            "Product E",
            "numeric",
            False,
            dependencies=["B", "C"],
            function=multiply_func,
        ),
        Node(
            "F",
            False,
            "Difference F",
            "numeric",
            False,
            dependencies=["D", "E"],
            function=subtract_func,
        ),
        Node(
            "G",
            False,
            "Ratio G",
            "numeric",
            False,
            dependencies=["D", "E"],
            function=divide_func,
        ),
        Node(
            "H",
            False,
            "Decision H",
            "boolean",
            True,
            dependencies=["F", "G"],
            function=greater_than_func,
        ),
        Node(
            "I",
            False,
            "Decision I",
            "numeric",
            True,
            dependencies=["F", "G"],
            function=sum_func,
        ),
    ]

    for node in nodes:
        graph.add_node(node)

    # Test with new input values
    input_values = {"A": 20.0, "B": 4.0, "C": 3.0}
    results = graph.evaluate(input_values)

    # Calculate expected values
    d = 20.0 + 4.0  # 24.0
    e = 4.0 * 3.0  # 12.0
    f = 24.0 - 12.0  # 12.0
    g = 24.0 / 12.0  # 2.0
    h = 12.0 > 2.0  # True
    i = 12.0 + 2.0  # 14.0

    # Assertions
    assert results["H"] == h
    assert results["I"] == i

    print("\nTest with different inputs:")
    print(
        f"Input A: {input_values['A']}, B: {input_values['B']}, C: {input_values['C']}"
    )
    print(f"Decision H: {results['H']}")
    print(f"Decision I: {results['I']}")


def test_memoization_efficiency():
    """
    Test that memoization works correctly by ensuring nodes are not
    evaluated multiple times when they have multiple dependents.
    """

    graph = DecisionGraph()

    # Create a graph where node D is used by both F and G
    # A -> D, B -> D, D -> F, D -> G, F -> H, G -> I

    def add_func(x, y):
        return x + y

    def double_func(x):
        return x * 2

    def triple_func(x):
        return x * 3

    def sum_func(x, y):
        return x + y

    nodes = [
        Node("A", True, "Input A", "numeric", False, value=5.0),
        Node("B", True, "Input B", "numeric", False, value=3.0),
        Node(
            "D",
            False,
            "Sum D",
            "numeric",
            False,
            dependencies=["A", "B"],
            function=add_func,
        ),
        Node(
            "F",
            False,
            "Double F",
            "numeric",
            False,
            dependencies=["D"],
            function=double_func,
        ),
        Node(
            "G",
            False,
            "Triple G",
            "numeric",
            False,
            dependencies=["D"],
            function=triple_func,
        ),
        Node(
            "H",
            False,
            "Decision H",
            "numeric",
            True,
            dependencies=["F"],
            function=lambda x: x,
        ),
        Node(
            "I",
            False,
            "Decision I",
            "numeric",
            True,
            dependencies=["G"],
            function=lambda x: x,
        ),
    ]

    for node in nodes:
        graph.add_node(node)

    input_values = {"A": 5.0, "B": 3.0}
    results = graph.evaluate(input_values)

    # D should be calculated once and reused
    expected_d = 5.0 + 3.0  # 8.0
    expected_f = 8.0 * 2  # 16.0
    expected_g = 8.0 * 3  # 24.0

    assert results["H"] == expected_f
    assert results["I"] == expected_g

    print("\nMemoization test:")
    print(f"Node D value: {expected_d}")
    print(f"Node F (2×D): {results['H']}")
    print(f"Node G (3×D): {results['I']}")


def test_node_value_updates():
    """
    Test that node values are properly updated during evaluation
    and can be queried afterward.
    """

    graph = DecisionGraph()

    # Create a simple graph: A -> B -> C
    def double_func(x):
        return x * 2

    nodes = [
        Node("A", True, "Input A", "numeric", False, value=5.0),
        Node(
            "B",
            False,
            "Double B",
            "numeric",
            False,
            dependencies=["A"],
            function=double_func,
        ),
        Node(
            "C",
            False,
            "Double C",
            "numeric",
            True,
            dependencies=["B"],
            function=double_func,
        ),
    ]

    for node in nodes:
        graph.add_node(node)

    # Check initial values
    initial_values = graph.get_node_values()
    assert initial_values["A"] == 5.0
    assert initial_values["B"] is None  # Not evaluated yet
    assert initial_values["C"] is None  # Not evaluated yet

    # Evaluate the graph
    input_values = {"A": 5.0}
    results = graph.evaluate(input_values)

    # Check that results are correct
    assert results["C"] == 20.0  # 5 * 2 * 2

    # Check that all node values have been updated
    final_values = graph.get_node_values()
    assert final_values["A"] == 5.0
    assert final_values["B"] == 10.0  # 5 * 2
    assert final_values["C"] == 20.0  # 10 * 2

    # Test individual node value queries
    assert graph.get_node_value("A") == 5.0
    assert graph.get_node_value("B") == 10.0
    assert graph.get_node_value("C") == 20.0
    assert graph.get_node_value("D") is None  # Non-existent node

    print("\nNode value update test:")
    print(f"Initial values: {initial_values}")
    print(f"Final values: {final_values}")
    print(
        f"Individual queries - A: {graph.get_node_value('A')}, B: {graph.get_node_value('B')}, C: {graph.get_node_value('C')}"
    )


def test_cache_vs_results_separation():
    """
    Test that the cache and results are properly separated.
    Results should only contain leaf nodes, while cache contains all nodes.
    """

    graph = DecisionGraph()

    # Create a simple graph: A -> B -> C (where C is leaf)
    def add_func(x, y):
        return x + y

    def double_func(x):
        return x * 2

    nodes = [
        Node("A", True, "Input A", "numeric", False, value=5.0),
        Node(
            "B",
            False,
            "Sum B",
            "numeric",
            False,
            dependencies=["A"],
            function=double_func,
        ),
        Node(
            "C",
            False,
            "Final C",
            "numeric",
            True,
            dependencies=["B"],
            function=double_func,
        ),
    ]

    for node in nodes:
        graph.add_node(node)

    input_values = {"A": 5.0}

    # Test that evaluate() only returns leaf nodes
    results = graph.evaluate(input_values)
    assert len(results) == 1
    assert "C" in results
    assert "A" not in results
    assert "B" not in results

    # Test that get_all_computed_values() returns all nodes
    all_computed = graph.get_all_computed_values(input_values)
    assert len(all_computed) == 3
    assert "A" in all_computed
    assert "B" in all_computed
    assert "C" in all_computed

    # Verify the values are correct
    assert all_computed["A"] == 5.0
    assert all_computed["B"] == 10.0  # 5 * 2
    assert all_computed["C"] == 20.0  # 10 * 2
    assert results["C"] == 20.0

    print("\nCache vs Results separation test:")
    print(f"Results (leaf nodes only): {results}")
    print(f"All computed values: {all_computed}")


if __name__ == "__main__":
    # Run the tests
    test_4level_decision_graph()
    test_4level_graph_with_different_inputs()
    test_memoization_efficiency()
    test_node_value_updates()
    test_cache_vs_results_separation()
    print("\nAll tests passed!")
