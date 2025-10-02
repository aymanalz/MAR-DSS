#!/usr/bin/env python3
"""
Demonstration of a 4-level decision graph using the new evaluate method.
This script creates a complex decision graph and shows how the recursive
evaluation with memoization works.
"""

from mar_dss.base import DecisionGraph, Node


def create_4level_graph():
    """
    Create a 4-level decision graph with the following structure:

    Level 1 (Inputs): A, B, C
    Level 2 (Intermediate): D = A + B, E = B * C
    Level 3 (Intermediate): F = D - E, G = D / E
    Level 4 (Leaf/Decision): H = F > G, I = F + G

    Returns: DecisionGraph instance
    """

    graph = DecisionGraph()

    # Level 1: Input nodes
    nodes = [
        Node("A", True, "Input A", "numeric", False, value=10.0),
        Node("B", True, "Input B", "numeric", False, value=5.0),
        Node("C", True, "Input C", "numeric", False, value=2.0),
    ]

    # Level 2: Intermediate nodes
    def add_func(x, y):
        return x + y

    def multiply_func(x, y):
        return x * y

    nodes.extend(
        [
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
        ]
    )

    # Level 3: Intermediate nodes
    def subtract_func(x, y):
        return x - y

    def divide_func(x, y):
        return x / y if y != 0 else 0

    nodes.extend(
        [
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
        ]
    )

    # Level 4: Leaf/Decision nodes
    def greater_than_func(x, y):
        return x > y

    def sum_func(x, y):
        return x + y

    nodes.extend(
        [
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
    )

    # Add all nodes to the graph
    for node in nodes:
        graph.add_node(node)

    return graph


def demonstrate_evaluation():
    """Demonstrate the evaluation process step by step."""

    print("=== 4-Level Decision Graph Demonstration ===\n")

    # Create the graph
    graph = create_4level_graph()

    # Show graph structure
    print("Graph Structure:")
    print("Level 1 (Inputs): A, B, C")
    print("Level 2 (Intermediate): D = A + B, E = B * C")
    print("Level 3 (Intermediate): F = D - E, G = D / E")
    print("Level 4 (Leaf/Decision): H = F > G, I = F + G\n")

    # Test with different input values
    test_cases = [
        {"A": 10.0, "B": 5.0, "C": 2.0},
        {"A": 20.0, "B": 4.0, "C": 3.0},
        {"A": 8.0, "B": 2.0, "C": 4.0},
    ]

    for i, input_values in enumerate(test_cases, 1):
        print(f"Test Case {i}:")
        print(
            f"Inputs: A={input_values['A']}, B={input_values['B']}, C={input_values['C']}"
        )

        # Evaluate the graph
        results = graph.evaluate(input_values)

        # Calculate intermediate values for display
        d = input_values["A"] + input_values["B"]
        e = input_values["B"] * input_values["C"]
        f = d - e
        g = d / e if e != 0 else 0
        h = f > g
        i = f + g

        print("Intermediate calculations:")
        print(f"  D = A + B = {input_values['A']} + {input_values['B']} = {d}")
        print(f"  E = B * C = {input_values['B']} * {input_values['C']} = {e}")
        print(f"  F = D - E = {d} - {e} = {f}")
        print(f"  G = D / E = {d} / {e} = {g}")
        print("Final decisions:")
        print(f"  H = F > G = {f} > {g} = {results['H']}")
        print(f"  I = F + G = {f} + {g} = {results['I']}")
        print()

    return graph


def show_graph_visualization():
    """Show the graph visualization if plotly is available."""

    try:
        graph = create_4level_graph()
        print("Generating graph visualization...")
        graph.plotly()
        print("Graph visualization displayed!")
    except Exception as e:
        print(f"Could not display graph visualization: {e}")
        print("Make sure plotly is installed: pip install plotly")


if __name__ == "__main__":
    # Run the demonstration
    graph = demonstrate_evaluation()

    # Try to show visualization
    show_graph_visualization()

    print("=== Demonstration Complete ===")
