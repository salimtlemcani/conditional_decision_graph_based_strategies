
import streamlit as st
from utils.data_utils import load_conditions, load_actions
from utils.decision_tree_utils import generate_dot

# File paths
CONDITIONS_FILE = 'conditions.json'
ACTIONS_FILE = 'actions.json'

# Directory to store strategy objects
STRATEGY_DIR = 'strategies'


def visualize_decision_tree():
    st.header("Decision Tree Visualization")

    # Load conditions and actions
    conditions = load_conditions(CONDITIONS_FILE)
    actions = load_actions(ACTIONS_FILE)

    if not conditions and not actions:
        st.info("No conditions or actions defined to visualize.")
        return

    # Generate DOT code
    dot = generate_dot(conditions, actions)

    # Display the graph
    st.graphviz_chart(dot)
