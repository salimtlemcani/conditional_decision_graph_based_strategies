
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


def my_strategies():
    st.header("My Strategies")

    # Tabs for Running and Viewing Strategies
    tab1, tab2 = st.tabs(["Run New Strategy", "View Saved Strategies"])

    with tab1:
        run_new_strategy()
    with tab2:
        view_saved_strategies()


def run_new_strategy():
    st.subheader("Run New Strategy")

    # Input fields for strategy parameters
    with st.form("strategy_params"):
        strategy_name = st.text_input("Strategy Name", help="Provide a unique name for your strategy.")
        start_date = st.date_input("Start Date", value=dtm.date.today() - dtm.timedelta(days=365))
        end_date = st.date_input("End Date", value=dtm.date.today())
        initial_cash = st.number_input("Initial Cash", min_value=1000, step=100, value=100000)

        submitted = st.form_submit_button("Run Strategy")
        print('DEBUG [run_new_strategy]', {
            "Strategy Name": strategy_name,
            "Start Date": start_date,
            "End Date": end_date,
            "Initial Cash": initial_cash,
            "Submitted": submitted
        })
    if submitted:
        if not strategy_name:
            st.error("Strategy name cannot be empty.")
            return

        # Check if strategy with the same name exists
        strategy_folder = os.path.join(STRATEGY_DIR, strategy_name)
        print(f'DEBUG [run_new_strategy] strategy_folder: {strategy_folder}')
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
                print(f'DEBUG [run_new_strategy] actions_file: {actions_file}')
                print(f'DEBUG [run_new_strategy] conditions_file: {conditions_file}')

                # Load conditions and actions
                conditions = load_conditions(conditions_file)
                actions = load_actions(actions_file)
                print(f'DEBUG [run_new_strategy] conditions: {conditions}')
                print(f'DEBUG [run_new_strategy] actions: {actions}')

                # Validate specifications
                if not validate_specs(conditions, actions):
                    st.error("Invalid condition or action specifications. Strategy build aborted.")
                    return

                # Build the decision tree
                decision_tree = build_decision_tree_from_specs(conditions, actions)
                if decision_tree is None:
                    st.error("Failed to build the decision tree.")
                    return
                print(f'DEBUG [run_new_strategy] decision_tree: {decision_tree}')

                try:
                    sig_strategy_object = run_strategy(start_date, end_date, initial_cash, conditions_file, actions_file)
                except Exception as e:
                    st.error(e)

                print('*' * 50)
                print(f'DEBUG [run_new_strategy] new sig strategy object : {sig_strategy_object}')
                # Get performance data
                performance = sig_strategy_object.history()
                # Reset the Series name to a simple string
                performance.name = f'{strategy_name} NAV'
                # Convert to DataFrame
                performance = performance.to_frame()

                # Create a strategy object to save
                strategy_object = {
                    'name': strategy_name,
                    'start_date': start_date,
                    'end_date': end_date,
                    'initial_cash': initial_cash,
                    'performance': performance,
                    'conditions': conditions,
                    'actions': actions,
                }
                print('*' * 50)
                print(f'DEBUG [run_new_strategy] new strategy object : {strategy_object}')
                # Save the strategy object in the strategy folder
                print(f'DEBUG [run_new_strategy] Updating strategy {strategy_name}')
                strategy_file = os.path.join(strategy_folder, 'strategy.pkl')
                with open(strategy_file, 'wb') as f:
                    pickle.dump(strategy_object, f)
                print(f'DEBUG [run_new_strategy] strategy saved to {strategy_file}')
                print('*'*50)
                print(f'DEBUG [run_new_strategy] new strategy object : {strategy_object}')
                st.success(f"Strategy '{strategy_name}' has been saved.")

            except Exception as e:
                st.error(f"An error occurred while running the strategy: {e}")


def view_saved_strategies():
    st.subheader("Saved Strategies")

    # List all strategy folders
    strategy_names = [name for name in os.listdir(STRATEGY_DIR)
                      if os.path.isdir(os.path.join(STRATEGY_DIR, name))]
    print(f'DEBUG [view_saved_strategies] strategy_names: {strategy_names}')

    if not strategy_names:
        st.info("No strategies have been saved yet.")
        return

    selected_strategy_name = st.selectbox("Select a Strategy", strategy_names)
    print(f'DEBUG [view_saved_strategies] selected_strategy_name: {selected_strategy_name}')
    if selected_strategy_name:
        # Define the strategy folder path
        strategy_folder = os.path.join(STRATEGY_DIR, selected_strategy_name)

        # Load the strategy object
        strategy_object = load_strategy(selected_strategy_name)
        print(f'DEBUG [view_saved_strategies] strategy_object: {strategy_object}')
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
