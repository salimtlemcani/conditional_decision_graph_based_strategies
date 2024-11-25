
def generate_dot(conditions, actions):
    """
    Generates DOT code for the decision tree based on conditions and actions.

    Parameters:
        conditions (list): List of condition dictionaries.
        actions (dict): Dictionary of actions with allocations.

    Returns:
        str: DOT language string representing the decision tree.
    """
    dot = 'digraph DecisionTree {\n'
    dot += '    node [shape=rectangle, style=filled, fillcolor="#EFEFEF"];\n\n'

    # Define condition nodes
    for cond in conditions:
        node_name = cond['node_name']
        indicator = cond['indicator']
        etf = cond['etf']
        window = cond['window']
        operator = cond['operator']
        threshold = cond['threshold']

        # Customize label based on threshold type
        if isinstance(threshold, (int, float)):
            threshold_display = f"{threshold}"
        else:
            threshold_display = f"Dynamic: {threshold['indicator']} {threshold['etf1']} {threshold['operator']} {threshold['etf2']} ({threshold['window']})"

        label = f"{node_name}\\n{indicator} {operator} {etf} ({window})\\nThreshold: {threshold_display}"
        dot += f'    "{node_name}" [shape=diamond, fillcolor="#FFD700", style=filled, color="#8B6508", fontcolor=black, label="{label}"];\n'

    # Define action nodes
    for action_name, allocations in actions.items():
        allocations_display = "\\n".join([f"{etf}: {alloc}" for etf, alloc in allocations.items()])
        label = f"{action_name}\\nAllocations:\\n{allocations_display}"
        dot += f'    "{action_name}" [shape=oval, fillcolor="#ADFF2F", style=filled, color="#556B2F", fontcolor=black, label="{label}"];\n'

    dot += '\n'

    # Define edges based on true_branch and false_branch
    for cond in conditions:
        node_name = cond['node_name']
        true_branch = cond['true_branch']
        false_branch = cond['false_branch']

        # Edge for true_branch
        dot += f'    "{node_name}" -> "{true_branch}" [label="True", color="#228B22"];\n'

        # Edge for false_branch
        dot += f'    "{node_name}" -> "{false_branch}" [label="False", color="#B22222"];\n'

    dot += '}'
    return dot
