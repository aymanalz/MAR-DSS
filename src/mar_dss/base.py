from typing import Any, Callable, List, Optional
import yaml

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
            with open(filepath, 'r') as file:
                data = yaml.safe_load(file)
                for item in data:
                    node = Node(
                        node_id=item['id'],
                        input_flag=item.get('input', False),
                        name=item['name'],
                        node_type=item['type'],
                        leaf_flag=item.get('leaf', True),
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

    def evaluate(self, input_values: dict) -> dict:
        """Evaluate all rule nodes based on input values."""
        results = {}
        for node_id, node in self.nodes.items():
            if node.is_input():
                results[node_id] = input_values.get(node_id, node.value)
            else:
                results[node_id] = node.evaluate(results)
        return results
