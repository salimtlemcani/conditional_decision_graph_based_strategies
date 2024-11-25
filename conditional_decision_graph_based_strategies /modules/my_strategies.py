
import streamlit as st
import datetime as dtm
import os
import pickle
from matplotlib import pyplot as plt
import pandas as pd

import sigtech.framework as sig
from utils.data_utils import load_conditions, load_actions
from utils.plotting_utils import plot_performance
from utils.strategy_utils import run_strategy, list_saved_strategies, load_strategy


# File paths
CONDITIONS_FILE = 'conditions.json'
ACTIONS_FILE = 'actions.json'

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

    if submitted:
        if not strategy_name:
            st.error("Strategy name cannot be empty.")
            return

        # Check if strategy with the same name exists
        strategy_file = os.path.join(STRATEGY_DIR, f"{strategy_name}.pkl")
        if os.path.exists(strategy_file):
            st.error("Strategy name already exists. Please choose a different name.")
            return

        with st.spinner("Running strategy..."):
            try:
                # Initialize SigTech environment
                sig.init()

                # Load conditions and actions
                conditions = load_conditions(CONDITIONS_FILE)
                actions = load_actions(ACTIONS_FILE)

                # Validate specifications
                from strategy_builder import validate_specs
                if not validate_specs(conditions, actions):
                    st.error("Invalid condition or action specifications. Strategy build aborted.")
                    return

                # Build the decision tree
                from strategy_builder import build_decision_tree_from_specs

                decision_tree = build_decision_tree_from_specs(conditions, actions)
                if decision_tree is None:
                    st.error("Failed to build the decision tree.")
                    return

                # Define ETFs
                etf_names = [
                    'TLT US EQUITY',
                    'TQQQ US EQUITY',
                    'SVXY US EQUITY',
                    'VIXY US EQUITY',
                    'QQQ UP EQUITY',
                    'SPY UP EQUITY',
                    'BND UP EQUITY',
                    'BIL UP EQUITY',
                    'GLD UP EQUITY',
                ]
                etfs = {name: sig.obj.get(name) for name in etf_names}

                # Retrieve ETF histories
                etf_histories = {name: etfs[name].history() for name in etf_names}

                # Prepare additional parameters
                additional_parameters = {
                    'example_dates': etf_histories[next(iter(etf_histories))].index.tolist(),
                    'etf_histories': etf_histories,
                    'etfs': etfs,
                    'conditions_file': CONDITIONS_FILE,
                    'actions_file': ACTIONS_FILE,
                }

                # Import basket_creation_method
                from strategy_execution import basket_creation_method

                # Initialize the Dynamic Strategy
                strat = sig.DynamicStrategy(
                    currency='USD',
                    start_date=start_date,
                    end_date=end_date,
                    trade_frequency='1BD',
                    basket_creation_method=basket_creation_method,
                    basket_creation_kwargs=additional_parameters,
                    initial_cash=initial_cash,
                )

                # Build the strategy
                strat.build(progress=True)

                # Get performance data
                performance = strat.history()
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
                }

                # Save the strategy object
                with open(strategy_file, 'wb') as f:
                    pickle.dump(strategy_object, f)

                st.success(f"Strategy '{strategy_name}' has been saved.")

            except Exception as e:
                st.error(f"An error occurred while running the strategy: {e}")


def view_saved_strategies():

    st.subheader("Saved Strategies")

    # List all saved strategy files
    strategy_files = [f for f in os.listdir(STRATEGY_DIR) if f.endswith('.pkl')]
    strategy_names = [os.path.splitext(f)[0] for f in strategy_files]

    if not strategy_names:
        st.info("No strategies have been saved yet.")
        return

    selected_strategy_name = st.selectbox("Select a Strategy", strategy_names)

    if selected_strategy_name:
        # Load the strategy object
        strategy_file = os.path.join(STRATEGY_DIR, f"{selected_strategy_name}.pkl")
        with open(strategy_file, 'rb') as f:
            strategy_object = pickle.load(f)

        st.write(f"**Strategy Name:** {strategy_object['name']}")
        st.write(f"**Start Date:** {strategy_object['start_date']}")
        st.write(f"**End Date:** {strategy_object['end_date']}")
        st.write(f"**Initial Cash:** {strategy_object['initial_cash']}")

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

        # # Show legend
        # ax.legend()

        # Tight layout to prevent clipping
        plt.tight_layout()

        # Display the plot in Streamlit
        st.pyplot(fig)
