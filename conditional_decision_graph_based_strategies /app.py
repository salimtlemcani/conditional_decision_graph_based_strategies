import streamlit as st

from modules.manage_conditions import manage_conditions
from modules.manage_actions import manage_actions
from modules.view_specs import view_specs
from modules.visualize_decision_tree import visualize_decision_tree
from modules.my_strategies import my_strategies


def main():
    st.title("Trading Strategy Builder")

    # Sidebar for navigation
    st.sidebar.header("Options")
    app_mode = st.sidebar.selectbox(
        "Choose Option",
        [
            "Manage Conditions",
            "Manage Actions",
            "View Specifications",
            "Visualize Decision Tree",
            "My Strategies"
        ]
    )

    if app_mode == "Manage Conditions":
        manage_conditions()
    elif app_mode == "Manage Actions":
        manage_actions()
    elif app_mode == "View Specifications":
        view_specs()
    elif app_mode == "Visualize Decision Tree":
        visualize_decision_tree()
    elif app_mode == "My Strategies":
        my_strategies()


if __name__ == "__main__":
    main()
