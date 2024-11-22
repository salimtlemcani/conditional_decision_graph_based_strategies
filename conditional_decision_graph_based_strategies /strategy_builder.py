from graph_factory import ActionNode, DecisionNode, DecisionTree
from helper import get_cum_return, get_rsi, get_vol, allocate_values, create_comparison_function, get_indicator_value

import logging

def build_decision_tree_from_specs(condition_specs, action_specs):
    """
    Builds a decision tree based on condition and action specifications.
    
    :param condition_specs: List of condition specifications (dictionaries).
    :param action_specs: Dictionary mapping action names to allocation dictionaries.
    :return: DecisionTree object.

    ---
    Example condition specification
    condition_spec = {
        'indicator': 'RSI',
        'etf': 'QQQ UP EQUITY',
        'window': 20,
        'operator': '>',
        'threshold': 70,
        'true_branch': 'action_node1',
        'false_branch': 'decision_node2'
    }

    """
    # Validate specifications first
    if not validate_specs(condition_specs, action_specs):
        logging.error("Specification validation failed. Aborting decision tree construction.")
        return None
        
    nodes = {}

    # Create ActionNodes
    for action_name, allocations in action_specs.items():
        nodes[action_name] = ActionNode(allocations=allocations)
    
    # Create DecisionNodes in reverse order to ensure dependencies are resolved
    for spec in reversed(condition_specs):
        threshold = spec['threshold']
        if isinstance(threshold, dict):
            # If threshold is another condition, retrieve its function
            comparison_func = create_comparison_function(
                indicator_name=threshold['indicator'],
                etf1=threshold['etf1'],
                etf2=threshold['etf2'],
                window=threshold.get('window', 60),
                operator=threshold.get('operator', '>')
            )
        elif callable(threshold):
            # If threshold is a callable function
            comparison_func = threshold
        else:
            # Static threshold value
            comparison_func = threshold
        
        # Initialize DecisionNode
        nodes[spec['node_name']] = DecisionNode(
            indicator={'name': spec['indicator'], 'etf': spec['etf']},
            window=spec['window'],
            operator=spec['operator'],
            threshold=comparison_func,
            true_branch=nodes.get(spec['true_branch']),
            false_branch=nodes.get(spec['false_branch'])
        )
    
    # The first node in the list is the root node
    root_node = nodes[condition_specs[0]['node_name']]
    decision_tree = DecisionTree(root_node)
    return decision_tree


def build_decision_tree():
    # Leaf nodes (actions)
    action_node1 = ActionNode(allocations={'SPY UP EQUITY': 0.5, 'TLT US EQUITY': 0.5})
    action_node2a = ActionNode(allocations={'TQQQ US EQUITY': 1.0})
    action_node2b = ActionNode(allocations={'SPY UP EQUITY': 0.55, 'SVXY US EQUITY': 0.225, 'TLT US EQUITY': 0.225})
    action_node3 = ActionNode(allocations={'TQQQ US EQUITY': 1.0})
    action_node4 = ActionNode(allocations={'BIL UP EQUITY': 0.25, 'SPY UP EQUITY': 0.25, 'TLT US EQUITY': 0.25, 'GLD UP EQUITY': 0.25})

    # Dynamic comparison functions
    cumulative_return_comparison = create_comparison_function(
        indicator_name='cumulative return',
        etf1='BND UP EQUITY',
        etf2='BIL UP EQUITY',
        window=60,
        operator='>'
    )

    # Decision nodes
    decision_node2a = DecisionNode(
        indicator={'name': 'Cumulative Return', 'etf': 'BND UP EQUITY'},
        window=60,
        operator='>',
        threshold=cumulative_return_comparison,  # Using callable for dynamic threshold
        true_branch=action_node2a,
        false_branch=action_node2b
    )

    decision_node3 = DecisionNode(
        indicator={'name': 'RSI', 'etf': 'QQQ UP EQUITY'},
        window=31,
        operator='<',
        threshold=10,
        true_branch=action_node3,
        false_branch=action_node4
    )

    decision_node2 = DecisionNode(
        indicator={'name': 'Volatility', 'etf': 'VIXY US EQUITY'},
        window=11,
        operator='>',
        threshold=0.025,
        true_branch=decision_node2a,
        false_branch=decision_node3
    )

    root_node = DecisionNode(
        indicator={'name': 'RSI', 'etf': 'QQQ UP EQUITY'},
        window=20,
        operator='>',
        threshold=70,
        true_branch=action_node1,
        false_branch=decision_node2
    )

    # Initialize the decision tree
    decision_tree = DecisionTree(root_node)
    return decision_tree


def validate_specs(condition_specs, action_specs):
    valid = True
    action_names = set(action_specs.keys())
    node_names = set(spec['node_name'] for spec in condition_specs)
    
    for spec in condition_specs:
        # Check required fields
        required_fields = ['node_name', 'indicator', 'etf', 'window', 'operator', 'threshold', 'true_branch', 'false_branch']
        for field in required_fields:
            if field not in spec:
                logging.error(f"Missing field '{field}' in condition specification: {spec}")
                valid = False
        
        # Check if branches reference existing nodes or actions
        for branch in ['true_branch', 'false_branch']:
            if spec[branch] not in node_names and spec[branch] not in action_names:
                logging.error(f"Branch '{branch}' in node '{spec['node_name']}' references unknown node/action '{spec[branch]}'")
                valid = False
    
    return valid


def condition1(context):
    rsi_series = get_rsi(context['etf_histories']['QQQ UP EQUITY'], 20)
    midnight_dt = context['midnight_dt']
    if midnight_dt not in rsi_series.index:
        return False
    rsi_value = rsi_series.loc[midnight_dt]
    return rsi_value > 70

def condition2(context):
    vol_series = get_vol(context['etf_histories']['VIXY US EQUITY'], 11)
    midnight_dt = context['midnight_dt']
    if midnight_dt not in vol_series.index:
        return False
    vol_value = vol_series.loc[midnight_dt]
    return vol_value > 0.025

def condition2a(context):
    cumul_bnd = get_cum_return(context['etf_histories']['BND UP EQUITY'].loc[:context['midnight_dt']], 60)
    cumul_bil = get_cum_return(context['etf_histories']['BIL UP EQUITY'].loc[:context['midnight_dt']], 60)
    return cumul_bnd > cumul_bil

def condition3(context):
    rsi_series = get_rsi(context['etf_histories']['QQQ UP EQUITY'], 31)
    midnight_dt = context['midnight_dt']
    if midnight_dt not in rsi_series.index:
        return False
    rsi_value = rsi_series.loc[midnight_dt]
    return rsi_value < 10
