from strategy_builder import build_decision_tree_from_specs
from utils.data_utils import load_conditions, load_actions

actions = load_actions('actions.json')
conditions = load_actions('conditions.json')

if __name__ == '__main__':
    build_decision_tree_from_specs(
        condition_specs=conditions,
        action_specs=actions,
    )