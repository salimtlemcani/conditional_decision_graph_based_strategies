class Node(ABC):
    @abstractmethod
    def evaluate(self, context):
        pass

class DecisionNode(Node):
    def __init__(
        self, 
        indicator: dict, 
        window: int, 
        operator: str, 
        threshold: Union[float, Callable[[dict], float]], 
        true_branch: Node, 
        false_branch: Node
    ):
        """
        Initializes a DecisionNode.

        :param indicator: Dictionary with 'name' and 'etf' keys.
        :param window: Window size for the indicator.
        :param operator: Comparison operator as a string ('>', '<', '>=', '<=', '==').
        :param threshold: Static float value or a callable that returns a float based on context.
        :param true_branch: Node to evaluate if condition is True.
        :param false_branch: Node to evaluate if condition is False.
        """
        self.indicator = indicator  # e.g., {'name': 'RSI', 'etf': 'QQQ UP EQUITY'}
        self.window = window
        self.operator = operator
        self.threshold = threshold  # Can be a float or a callable
        self.true_branch = true_branch
        self.false_branch = false_branch

    def evaluate(self, context):
        """
        Evaluates the condition and traverses the tree accordingly.

        :param context: Dictionary containing necessary data and parameters.
        :return: Result from the true or false branch.
        """
        if callable(self.threshold):
            threshold_value = self.threshold(context)
            print(f"[DecisionNode] Evaluating condition: {self.get_label()} with dynamic threshold {threshold_value}")
        else:
            threshold_value = self.threshold
            print(f"[DecisionNode] Evaluating condition: {self.get_label()} with threshold {threshold_value}")

        # Retrieve the indicator value from context
        indicator_value = get_indicator_value(context, self.indicator, self.window)
        print(f"[DecisionNode] Indicator Value for {self.indicator['etf']}: {indicator_value}")

        # Perform the comparison
        condition_met = self.compare(indicator_value, self.operator, threshold_value)
        print(f"[DecisionNode] Condition Met: {condition_met}")

        if condition_met:
            return self.true_branch.evaluate(context)
            print(f"[DecisionNode] Condition true. Traversing to True branch.")
        else:
            return self.false_branch.evaluate(context)
            print(f"[DecisionNode] Condition false. Traversing to False branch.")

    def compare(self, value1, operator, value2):
        """
        Compares two values based on the operator.

        :param value1: First value (indicator value).
        :param operator: Comparison operator as a string.
        :param value2: Second value (threshold).
        :return: Boolean result of the comparison.
        """
        if operator == '>':
            return value1 > value2
        elif operator == '<':
            return value1 < value2
        elif operator == '>=':
            return value1 >= value2
        elif operator == '<=':
            return value1 <= value2
        elif operator == '==':
            return value1 == value2
        else:
            raise ValueError(f"Unsupported operator: {operator}")

    def get_label(self):
        """
        Generates a descriptive label for the condition.

        :return: String label.
        """
        if callable(self.threshold):
            threshold_desc = self.threshold.__name__
        else:
            threshold_desc = self.threshold
        return f"{self.indicator['name']}({self.indicator['etf']}, {self.window}) {self.operator} {threshold_desc}"



class ActionNode(Node):
    def __init__(self, allocations: dict):
        """
        Initializes an ActionNode.

        :param allocations: Dictionary mapping ETFs to their allocation weights (in decimal).
                            e.g., {'SPY UP EQUITY': 0.5, 'TLT US EQUITY': 0.5}
        """
        self.allocations = allocations  # e.g., {'SPY UP EQUITY': 0.5, 'TLT US EQUITY': 0.5}

    def evaluate(self, context):
        """
        Executes the action by allocating the specified weights to ETFs.

        :param context: Dictionary containing necessary data and parameters.
        :return: Dictionary representing the order allocations.
        """
        print(f"[ActionNode] Executing action: {self.get_label()}")
        return self.action(context)

    def action(self, context):
        """
        Calculates the order allocations based on the allocations and ETF prices.

        :param context: Dictionary containing ETF histories and other parameters.
        :return: Dictionary with ETF orders.
        """
        allocations = {
            etf: self.allocations[etf] * context['initial_cash'] / context['etf_histories'][etf].asof(context['size_date']) 
            for etf in self.allocations
        }
        print(f"[ActionNode] Allocations: {allocations}")
        return allocations

    def get_label(self):
        """
        Generates a descriptive label for the action.

        :return: String label.
        """
        allocations_str = ', '.join([f"{etf}: {weight*100:.1f}%" for etf, weight in self.allocations.items()])
        return f"Allocate {allocations_str}"

class DecisionTree:
    def __init__(self, root):
        self.root = root

    def evaluate(self, context):
        return self.root.evaluate(context)

    def plot_tree(self, root_node):
        """
        Plots the decision tree using graphviz.
    
        :param root_node: The root node of the decision tree.
        :return: graphviz.Digraph object.
        """
        dot = Digraph(comment='Decision Tree')
        node_counter = [0]  # Mutable counter
    
        def traverse(node, parent_id=None, edge_label=''):
            node_id = str(node_counter[0])
            node_counter[0] += 1
    
            if isinstance(node, DecisionNode):
                label = node.get_label()
                dot.node(node_id, label, shape='diamond')
                traverse(node.true_branch, node_id, 'True')
                traverse(node.false_branch, node_id, 'False')
            elif isinstance(node, ActionNode):
                label = node.get_label()
                dot.node(node_id, label, shape='box')
            else:
                dot.node(node_id, 'Unknown', shape='ellipse')
    
            if parent_id is not None:
                dot.edge(parent_id, node_id, label=edge_label)
    
        traverse(root_node)
        return dot
    
    def print_tree(self, node, level=0):
        indent = "  " * level
        if isinstance(node, DecisionNode):
            print(f"{indent}Decision: {node.get_label()}")
            if node.true_branch:
                print(f"{indent}  True ->")
                print_tree(node.true_branch, level + 2)
            if node.false_branch:
                print(f"{indent}  False ->")
                print_tree(node.false_branch, level + 2)
        elif isinstance(node, ActionNode):
            print(f"{indent}Action: {node.get_label()}")
        else:
            print(f"{indent}Unknown Node")