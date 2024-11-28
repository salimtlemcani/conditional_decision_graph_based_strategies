
import streamlit as st
import datetime as dtm
import os
import pickle
from matplotlib import pyplot as plt
import pandas as pd

import sigtech.framework as sig

from strategy_builder import validate_specs, build_decision_tree_from_specs
from strategy_execution import run_strategy

from utils.data_utils import load_conditions, load_actions
from utils.decision_tree_utils import generate_dot
from utils.plotting_utils import plot_performance
from utils.strategy_utils import list_saved_strategies, load_strategy


# Directory to store strategy objects
STRATEGY_DIR = 'strategies'
DEBUG = False


def select_strategy_name_selectbox(key: str = None):
    # List all strategy folders
    strategy_names = [name for name in os.listdir(STRATEGY_DIR) if os.path.isdir(os.path.join(STRATEGY_DIR, name))]

    if not strategy_names:
        st.info("No strategies have been saved yet.")
        return

    selected_strategy_name = st.selectbox("Select a Strategy", strategy_names, key=key)
    return selected_strategy_name


def my_strategies():
    st.header("My Strategies")

    # Manage active tab in session state
    if "active_tab" not in st.session_state:
        st.session_state.active_tab = "Run New Strategy"  # Default tab

    # Tab selection
    tabs = ["Run New Strategy", "View Saved Strategies"]
    active_tab = st.radio("Select a Tab", tabs, key="active_tab_selector")

    # Update session state with the selected tab
    st.session_state.active_tab = active_tab

    # Render content based on active tab
    if st.session_state.active_tab == "Run New Strategy":
        run_new_strategy()
    elif st.session_state.active_tab == "View Saved Strategies":
        view_saved_strategies()


def run_new_strategy():
    st.subheader("Run New Strategy")

    selected_strategy_name = select_strategy_name_selectbox(key='run_strategy_selector')
    if selected_strategy_name:
        st.session_state['run_strategy_name'] = selected_strategy_name
        if DEBUG: print(f'DEBUG [view_saved_strategies]: {selected_strategy_name}')

    with st.form("strategy_params"):
        start_date = st.date_input("Start Date", value=dtm.date.today() - dtm.timedelta(days=365))
        end_date = st.date_input("End Date", value=dtm.date.today())
        initial_cash = st.number_input("Initial Cash", min_value=1000, step=100, value=100000)

        submitted = st.form_submit_button("Run Strategy")
        if DEBUG: print('DEBUG [run_new_strategy]', {
            "Strategy Name": selected_strategy_name,
            "Start Date": start_date,
            "End Date": end_date,
            "Initial Cash": initial_cash,
            "Submitted": submitted
        })
    if submitted:
        if not selected_strategy_name:
            st.error("Strategy name cannot be empty.")
            return

        # Check if strategy with the same name exists
        # Define the strategy folder path
        strategy_folder = os.path.join(STRATEGY_DIR, selected_strategy_name)
        if not os.path.exists(strategy_folder):
            st.error("Strategy name does not exists. Please make sure to add your strategy before running it.")
            return

        with st.spinner("Running strategy..."):
            try:
                # Initialize SigTech environment
                sig.init()

                # File paths
                conditions_file = os.path.join(strategy_folder, 'conditions.json')
                actions_file = os.path.join(strategy_folder, 'actions.json')
                if DEBUG: print(f'DEBUG [run_new_strategy] actions_file: {actions_file}')
                if DEBUG: print(f'DEBUG [run_new_strategy] conditions_file: {conditions_file}')

                # Load conditions and actions
                conditions = load_conditions(conditions_file)
                actions = load_actions(actions_file)
                if DEBUG: print(f'DEBUG [run_new_strategy] conditions: {conditions}')
                if DEBUG: print(f'DEBUG [run_new_strategy] actions: {actions}')

                # Validate specifications
                if not validate_specs(conditions, actions):
                    st.error("Invalid condition or action specifications. Strategy build aborted.")
                    return

                # Build the decision tree
                decision_tree = build_decision_tree_from_specs(conditions, actions)
                if decision_tree is None:
                    st.error("Failed to build the decision tree.")
                    return
                if DEBUG: print(f'DEBUG [run_new_strategy] decision_tree: {decision_tree}')

                try:
                    sig_strategy_object = run_strategy(start_date, end_date, initial_cash, conditions_file, actions_file)
                except Exception as e:
                    st.error(e)

                if DEBUG: print('*' * 50)
                if DEBUG: print(f'DEBUG [run_new_strategy] new sig strategy object : {sig_strategy_object}')
                # Get performance data
                performance = sig_strategy_object.history()
                # Reset the Series name to a simple string
                performance.name = f'{selected_strategy_name} NAV'
                # Convert to DataFrame
                performance = performance.to_frame()

                # Create a strategy object to save
                strategy_object = {
                    'name': selected_strategy_name,
                    'start_date': start_date,
                    'end_date': end_date,
                    'initial_cash': initial_cash,
                    'performance': performance,
                    'conditions': conditions,
                    'actions': actions,
                }
                if DEBUG: print('*' * 50)
                if DEBUG: print(f'DEBUG [run_new_strategy] new strategy object : {strategy_object}')
                # Save the strategy object in the strategy folder
                if DEBUG: print(f'DEBUG [run_new_strategy] Updating strategy {selected_strategy_name}')
                strategy_file = os.path.join(strategy_folder, 'strategy.pkl')
                with open(strategy_file, 'wb') as f:
                    pickle.dump(strategy_object, f)
                if DEBUG: print(f'DEBUG [run_new_strategy] strategy saved to {strategy_file}')
                if DEBUG: print('*'*50)
                if DEBUG: print(f'DEBUG [run_new_strategy] new strategy object : {strategy_object}')
                st.success(f"Strategy '{selected_strategy_name}' has been saved.")

            except Exception as e:
                st.error(f"An error occurred while running the strategy: {e}")


def view_saved_strategies():
    if DEBUG: print('DEBUG [view_saved_strategies]')
    st.subheader("Saved Strategies")

    selected_strategy_name = st.session_state.get('view_strategy_name')
    if not selected_strategy_name:
        selected_strategy_name = select_strategy_name_selectbox(key='view_saved_strategies_selector')

    if selected_strategy_name:
        st.session_state['view_strategy_name'] = selected_strategy_name
        # Define the strategy folder path
        strategy_folder = os.path.join(STRATEGY_DIR, selected_strategy_name)

        # Load the strategy object
        if DEBUG: print('DEBUG [view_saved_strategies] loading strategy object')
        strategy_object = load_strategy(selected_strategy_name)
        if DEBUG: print(f'DEBUG [view_saved_strategies] strategy_object: {strategy_object}')
        if strategy_object is None:
            st.error("Failed to load the strategy. Please ensure to add and run the strategy first.")
            return

        st.write(f"**Strategy Name:** {strategy_object['name']}")
        st.write(f"**Start Date:** {strategy_object['start_date']}")
        st.write(f"**End Date:** {strategy_object['end_date']}")
        st.write(f"**Initial Cash:** {strategy_object['initial_cash']}")

        # Load Conditions
        conditions_file = os.path.join(strategy_folder, 'conditions.json')
        if os.path.exists(conditions_file):
            conditions = load_conditions(conditions_file)
            st.subheader("Conditions")
            for condition in conditions:
                st.markdown(f"**{condition['node_name']}**")
                st.json(condition)
        else:
            st.info("No conditions found for this strategy.")

        # Load Actions
        actions_file = os.path.join(strategy_folder, 'actions.json')
        if os.path.exists(actions_file):
            actions = load_actions(actions_file)
            st.subheader("Actions")
            for action_name, alloc in actions.items():
                st.markdown(f"**{action_name}**")
                st.json(alloc)
        else:
            st.info("No actions found for this strategy.")

        # Visualize Decision Tree
        if conditions and actions:
            st.subheader("Decision Tree Visualization")
            dot = generate_dot(conditions, actions)
            st.graphviz_chart(dot)

        # Plot the performance
        performance = strategy_object['performance']

        # Ensure the index is datetime
        performance.index = pd.to_datetime(performance.index)

        # Get the dynamic column name
        performance_column = performance.columns[0]

        # Create a Matplotlib figure and axis
        fig, ax = plt.subplots(figsize=(10, 6))

        # Plot the performance data using the dynamic column name
        ax.plot(performance.index, performance[performance_column], label=performance_column, color='blue')

        # Set axis labels and title
        ax.set_xlabel('Date')
        ax.set_ylabel('Strategy NAV')
        ax.set_title('Strategy Performance Over Time')

        # Adjust x-axis date formatting
        ax.xaxis.set_major_locator(plt.MaxNLocator(10))  # Limit number of x-axis ticks
        plt.xticks(rotation=45)  # Rotate x-axis labels for readability

        # Adjust y-axis scaling to enhance fluctuations
        y_min = performance[performance_column].min() * 0.99  # Slightly lower than min value
        y_max = performance[performance_column].max() * 1.01  # Slightly higher than max value
        ax.set_ylim([y_min, y_max])

        # Enable grid
        ax.grid(True)

        # Tight layout to prevent clipping
        plt.tight_layout()

        # Display the plot in Streamlit
        st.pyplot(fig)
