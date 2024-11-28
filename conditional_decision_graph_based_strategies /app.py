import streamlit as st

from modules.add_strategy import add_strategy
from modules.manage_conditions import manage_conditions
from modules.manage_actions import manage_actions
from modules.view_specs import view_specs
from modules.visualize_decision_tree import visualize_decision_tree
from modules.my_strategies import my_strategies


def main():
    st.title("Trading Strategy Builder")

    # Initialize app_mode in session_state if not present
    if 'app_mode' not in st.session_state:
        st.session_state['app_mode'] = 'Add Strategy'

    # Sidebar for navigation
    st.sidebar.header("Options")
    if 'selected_strategy_name' not in st.session_state:
        app_mode = st.sidebar.selectbox(
            "Choose Option",
            ["Add Strategy"],
            key='navigation'
        )
    else:
        app_mode = st.sidebar.selectbox(
            "Choose Option",
            [
                "Add Strategy",
                "Manage Conditions",
                "Manage Actions",
                "View Specifications",
                "Visualize Decision Tree",
                "My Strategies"
            ],
            key='navigation'
        )

    # Update st.session_state['app_mode'] based on selection
    st.session_state['app_mode'] = app_mode


    if st.session_state['app_mode'] == "Add Strategy":
        add_strategy()
    elif st.session_state['app_mode'] == "Manage Conditions":
        manage_conditions(st.session_state['selected_strategy_name'])
    elif st.session_state['app_mode'] == "Manage Actions":
        manage_actions(st.session_state['selected_strategy_name'])
    elif st.session_state['app_mode'] == "View Specifications":
        view_specs(st.session_state['selected_strategy_name'])
    elif st.session_state['app_mode'] == "Visualize Decision Tree":
        visualize_decision_tree(st.session_state['selected_strategy_name'])
    elif st.session_state['app_mode'] == "My Strategies":
        my_strategies()


if __name__ == "__main__":
    main()
