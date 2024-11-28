
import streamlit as st
import os

from utils.data_utils import load_conditions, load_actions
from utils.decision_tree_utils import generate_dot

# Directory to store strategy objects
STRATEGY_DIR = 'strategies'


def visualize_decision_tree(strategy_name):
    st.header("Decision Tree Visualization")

    # Load conditions and actions
    strategy_folder = os.path.join(STRATEGY_DIR, strategy_name)
    conditions_file = os.path.join(strategy_folder, 'conditions.json')
    actions_file = os.path.join(strategy_folder, 'actions.json')

    conditions = load_conditions(conditions_file)
    actions = load_actions(actions_file)

    if not conditions and not actions:
        st.info("No conditions or actions defined to visualize.")
        return

    # Generate DOT code
    dot = generate_dot(conditions, actions)

    # Display the graph
    st.graphviz_chart(dot)
