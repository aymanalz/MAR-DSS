from typing import Any, Callable, List, Optional
import yaml
import networkx as nx
import numpy as np
import matplotlib.pyplot as plt
import plotly.graph_objects as go

class Node:
    def __init__(
        self,
        node_id: str,
        input_flag: bool,
        name: str,
        node_type: str,
        leaf_flag: bool = True,
        description: Optional[str] = None,
        value: Optional[Any] = None,
        default: Optional[Any] = None,
        range_: Optional[List[Any]] = None,
        allowed_values: Optional[List[Any]] = None,
        certainty: float = 1.0,
        group: Optional[str] = None,
        dependencies: Optional[List[str]] = None,
        module: Optional[str] = None,  
        function: Optional[Callable] = None,
    ):
        self.node_id = node_id                  # symbolic ID, e.g., "Ks", "Vs"
        self.input_flag = input_flag       
        self.name = name                        # human-readable name
        self.node_type = node_type              # "numeric", "boolean", etc.
        self.leaf_flag = leaf_flag                  # True if no dependencies
        self.description = description
        self.value = value                      # current value (for input nodes)
        self.default = default                  # default value
        self.range = range_                     # numeric range
        self.allowed_values = allowed_values    # categorical/boolean allowed values
        self.certainty = certainty
        self.group = group
        self.dependencies = dependencies or []  # list of node_ids this depends on
        self.module = module                    # Python module path
        self.function = function                # optional: Python callable 
        

    def is_input(self) -> bool:
        return self.input_flag

    def is_rule(self) -> bool:
        return not self.input_flag

    def evaluate(self, inputs: dict) -> Any:
        """Evaluate the node if it’s a rule node using function reference."""
        if self.is_rule():
            if self.function:
                args = [inputs[dep] for dep in self.dependencies]
                return self.function(*args)
            else:
                return self.value
        else:
            # For input nodes, just return the value
            return self.value

class DecisionGraph:
    def __init__(self):
        self.nodes = {}  # key: node_id, value: Node instance

    def add_node(self, node: Node):
        self.nodes[node.node_id] = node

    def get_node(self, node_id: str) -> Optional[Node]:
        return self.nodes.get(node_id)
    
    def from_yamls(self, filepaths: List[str]):
        """Load nodes from multiple YAML files."""
        
        for filepath in filepaths:
            input_flag = True
            if not "input" in filepath:
                input_flag = False
            with open(filepath, 'r') as file:
                data = yaml.safe_load(file)
                for key, items in data.items():
                    if not isinstance(items, list):
                        continue  # skip if value is not a list
                    for item in items:
                        if not isinstance(item, dict):
                            continue  # skip items that are not dicts
                        node = Node(
                            node_id=item['id'],
                            input_flag=input_flag,
                            name=item['name'],
                            node_type=item['type'],
                            leaf_flag=item.get('leaf', False),
                            description=item.get('description'),
                            value=item.get('value'),
                            default=item.get('default'),
                            range_=item.get('range'),
                            allowed_values=item.get('allowed_values'),
                            certainty=item.get('certainty', 1.0),
                            group=item.get('group'),
                            dependencies=item.get('dependencies'),
                            module=item.get('module'),
                            function=None  # Function can be set later if needed
                        )
                        self.add_node(node)

    def evaluate_node(self, node_id: str, input_values: dict, cache: dict) -> Any:
        """Recursively evaluate a node with memoization."""
        if node_id in cache:
            return cache[node_id]

        node = self.nodes[node_id]

        if node.is_input():
            value = input_values.get(node_id, node.value)
        else:
            # recursively evaluate dependencies
            dep_values = {
                dep: self.evaluate_node(dep, input_values, cache)
                for dep in node.dependencies
            }
            if node.function:
                value = node.function(*dep_values.values())
            else:
                value = node.value

        # Update the node's value with the computed result
        node.value = value
        cache[node_id] = value
        return value

    def evaluate(self, input_values: dict) -> dict:
        """Evaluate all leaf nodes in the graph."""
        cache = {}  # Cache for all computed values
        leaf_nodes = [nid for nid, n in self.nodes.items() if n.leaf_flag]
        results = {}  # Only leaf node results

        for nid in leaf_nodes:
            results[nid] = self.evaluate_node(nid, input_values, cache)

        return results
    
    def get_node_values(self) -> dict:
        """Get current values of all nodes in the graph."""
        return {node_id: node.value for node_id, node in self.nodes.items()}
    
    def get_node_value(self, node_id: str) -> Any:
        """Get the current value of a specific node."""
        node = self.nodes.get(node_id)
        return node.value if node else None
    
    def get_all_computed_values(self, input_values: dict) -> dict:
        """Get all computed values including intermediate nodes."""
        # Just evaluate leaf nodes (which computes everything) and return cache
        cache = {}
        leaf_nodes = [nid for nid, n in self.nodes.items() if n.leaf_flag]
        
        for nid in leaf_nodes:
            self.evaluate_node(nid, input_values, cache)
        
        return cache
    
    # using networkx, plot the graph
    def plot(self):
        G = nx.DiGraph()
        node_colors = []
        for node_id, node in self.nodes.items():
            G.add_node(node_id, label=node.name)
            for dep in node.dependencies:
                G.add_edge(dep, node_id)

        # Assign colors: input nodes blue, rule nodes orange
        for node_id in G.nodes():
            node = self.nodes[node_id]
            if node.is_input():
                node_colors.append('skyblue')
            else:
                node_colors.append('orange')

        pos = nx.spring_layout(G)
        nx.draw(G, pos, with_labels=True, arrows=True, node_color=node_colors)

        # Draw labels on the right side of each node
        labels = nx.get_node_attributes(G, 'label')
        label_pos = {k: (v[0] + 0.08, v[1]) for k, v in pos.items()}
        nx.draw_networkx_labels(G, label_pos, labels, horizontalalignment='left')
        plt.show()


    def plotly(self, layout: str = "kamada_kawai"):

        G = nx.DiGraph()
        # Build graph
        for node_id, node in self.nodes.items():
            G.add_node(node_id, label=node.name, type="input" if node.is_input() else "rule")
            for dep in node.dependencies:
                G.add_edge(dep, node_id)        

        if layout == "shell":
            pos = nx.shell_layout(G)
        elif layout == "circular":
            pos = nx.circular_layout(G)
        elif layout == "kamada_kawai":
            pos = nx.kamada_kawai_layout(G)
        elif layout == "spectral":
            pos = nx.spectral_layout(G)
        elif layout == "planar":
            pos = nx.planar_layout(G)

        # Edges
        edge_x = []
        edge_y = []
        for src, dst in G.edges():
            x0, y0 = pos[src]
            x1, y1 = pos[dst]
            edge_x.extend([x0, x1, None])
            edge_y.extend([y0, y1, None])

        edge_trace = go.Scatter(
            x=edge_x,
            y=edge_y,
            line=dict(width=1, color='gray'),
            hoverinfo='none',
            mode='lines',
            showlegend=False
        )

        # Nodes
        node_x = []
        node_y = []
        node_color = []
        node_text = []
        node_hover = []
        label_offsets = {}

        # Compute label offsets to minimize overlap
        # Offset labels radially outward from the graph center
        center = np.mean(np.array(list(pos.values())), axis=0)
        offset_dist = 0.08  # adjust as needed

        for node_id in G.nodes():
            x, y = pos[node_id]
            node_x.append(x)
            node_y.append(y)
            n = self.nodes[node_id]
            # Color logic: leaf node -> red, else input -> skyblue, else orange
            if n.leaf_flag:
                node_color.append('red')
            elif n.is_input():
                node_color.append('skyblue')
            else:
                node_color.append('orange')
            hover = (
                f"id: {n.node_id}<br>"
                f"name: {n.name}<br>"
                f"description: {n.description or ''}<br>"
                f"value: {n.value}<br>"
                f"certainty: {n.certainty}<br>"
                f"group: {n.group or ''}"
            )
            node_hover.append(hover)
            # Calculate offset direction
            dx, dy = x - center[0], y - center[1]
            norm = np.sqrt(dx**2 + dy**2)
            if norm == 0:
                dx, dy = 1, 0
                norm = 1
            dx /= norm
            dy /= norm
            label_offsets[node_id] = (x + dx * offset_dist, y + dy * offset_dist)
            node_text.append("")  # We'll add text as a separate trace

        node_trace = go.Scatter(
            x=node_x,
            y=node_y,
            mode='markers',
            hoverinfo='text',
            hovertext=node_hover,
            marker=dict(
                showscale=False,
                color=node_color,
                size=30,
                line=dict(width=2, color='black')
            ),
            showlegend=False
        )

        # Add a separate trace for labels with offset positions
        label_trace = go.Scatter(
            x=[label_offsets[nid][0] for nid in G.nodes()],
            y=[label_offsets[nid][1] for nid in G.nodes()],
            text=[self.nodes[nid].name for nid in G.nodes()],
            mode='text',
            textposition='middle right',
            hoverinfo='none',
            textfont=dict(size=12, color='black'),
            showlegend=False
        )

        # Legend traces (dummy invisible points for legend)
        legend_traces = [
            go.Scatter(
                x=[None], y=[None],
                mode='markers',
                marker=dict(color='skyblue', size=20, line=dict(width=2, color='black')),
                name='Input Node',
                showlegend=True
            ),
            go.Scatter(
                x=[None], y=[None],
                mode='markers',
                marker=dict(color='orange', size=20, line=dict(width=2, color='black')),
                name='Rule Node',
                showlegend=True
            ),
            go.Scatter(
                x=[None], y=[None],
                mode='markers',
                marker=dict(color='red', size=20, line=dict(width=2, color='black')),
                name='Decision Node',
                showlegend=True
            ),
        ]

        fig = go.Figure(
            data=[edge_trace, node_trace, label_trace] + legend_traces,
            layout=go.Layout(
                showlegend=True,
                hovermode='closest',
                margin=dict(b=20, l=5, r=5, t=40),
                xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                yaxis=dict(showgrid=False, zeroline=False, showticklabels=False)
            )
        )

        fig.show()

        
        
