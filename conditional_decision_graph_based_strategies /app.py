import streamlit as st
import json
import os
import base64
import pickle
import datetime as dtm
import pandas as pd
import matplotlib.pyplot as plt

import sigtech.framework as sig
from strategy_builder import build_decision_tree_from_specs


# File paths
CONDITIONS_FILE = 'conditions.json'
ACTIONS_FILE = 'actions.json'

# Directory to store strategy objects
STRATEGY_DIR = 'strategies'

# Ensure the directory exists
if not os.path.exists(STRATEGY_DIR):
    os.makedirs(STRATEGY_DIR)


def load_conditions(file_path):
    if os.path.exists(file_path):
        with open(file_path, 'r') as f:
            return json.load(f)
    return []


def save_conditions(file_path, data):
    with open(file_path, 'w') as f:
        json.dump(data, f, indent=4)


def load_actions(file_path):
    if os.path.exists(file_path):
        with open(file_path, 'r') as f:
            return json.load(f)
    return {}


def save_actions(file_path, data):
    with open(file_path, 'w') as f:
        json.dump(data, f, indent=4)


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
            "My Strategies"  # New Option
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


def manage_conditions():
    st.header("Manage Conditions")
    conditions = load_conditions(CONDITIONS_FILE)
    actions = load_actions(ACTIONS_FILE)  # Load actions to get branch names

    # Combine condition and action node names for branch selection
    condition_names = [cond['node_name'] for cond in conditions]
    action_names = list(actions.keys())
    all_node_names = condition_names + action_names

    # Tabs for Adding and Editing Conditions
    tab1, tab2 = st.tabs(["Add New Condition", "Edit Existing Conditions"])

    with tab1:
        st.subheader("Add New Condition")
        with st.form("add_condition"):
            node_name = st.text_input("Node Name", help="Unique identifier for the condition node.")
            indicator = st.selectbox("Indicator", ["RSI", "Volatility", "Cumulative Return"])
            etf = st.text_input("ETF Name (e.g., QQQ UP EQUITY)", help="Name of the ETF involved in the condition.")
            window = st.number_input("Window Size", min_value=1, step=1, help="Time window for the indicator.")
            operator = st.selectbox("Operator", [">", "<", ">=", "<=", "=="])

            threshold_type = st.selectbox("Threshold Type", ["Static Value", "Dynamic Comparison"])

            if threshold_type == "Static Value":
                threshold = st.number_input(
                    "Threshold Value",
                    step=0.01,
                    value=0.0,  # Ensure float
                    format="%.2f",
                    help="Numeric threshold value."
                )
            else:
                st.info("Define dynamic threshold based on another comparison.")
                dyn_indicator = st.selectbox("Dynamic Indicator", ["RSI", "Volatility", "Cumulative Return"])
                dyn_etf1 = st.text_input("Dynamic ETF 1 (e.g., BND UP EQUITY)", help="First ETF for comparison.")
                dyn_etf2 = st.text_input("Dynamic ETF 2 (e.g., BIL UP EQUITY)", help="Second ETF for comparison.")
                dyn_window = st.number_input("Dynamic Window Size", min_value=1, step=1,
                                             help="Time window for the dynamic comparison.")
                dyn_operator = st.selectbox("Dynamic Operator", [">", "<", ">=", "<=", "=="])
                threshold = {
                    "indicator": dyn_indicator,
                    "etf1": dyn_etf1,
                    "etf2": dyn_etf2,
                    "window": dyn_window,
                    "operator": dyn_operator
                }

            true_branch = st.selectbox("True Branch (Action/Condition Node Name)", options=all_node_names)
            false_branch = st.selectbox("False Branch (Action/Condition Node Name)", options=all_node_names)

            submitted = st.form_submit_button("Add Condition")
            if submitted:
                if any(cond['node_name'] == node_name for cond in conditions):
                    st.error("Node name already exists. Choose a unique name.")
                elif not node_name:
                    st.error("Node name cannot be empty.")
                else:
                    new_condition = {
                        "node_name": node_name,
                        "indicator": indicator,
                        "etf": etf,
                        "window": window,
                        "operator": operator,
                        "threshold": threshold,
                        "true_branch": true_branch,
                        "false_branch": false_branch
                    }
                    conditions.append(new_condition)
                    save_conditions(CONDITIONS_FILE, conditions)
                    st.success(f"Condition '{node_name}' added successfully!")

    with tab2:
        st.subheader("Edit Existing Conditions")
        if not conditions:
            st.info("No conditions available to edit.")
        else:
            condition_names = [cond['node_name'] for cond in conditions]
            selected_condition = st.selectbox("Select Condition to Edit", condition_names)

            condition = next((cond for cond in conditions if cond['node_name'] == selected_condition), None)

            if condition:
                with st.form("edit_condition"):
                    node_name = st.text_input("Node Name", value=condition['node_name'], disabled=True)
                    indicator = st.selectbox("Indicator", ["RSI", "Volatility", "Cumulative Return"],
                                             index=["RSI", "Volatility", "Cumulative Return"].index(
                                                 condition['indicator']))
                    etf = st.text_input("ETF Name (e.g., QQQ UP EQUITY)", value=condition['etf'])
                    window = st.number_input("Window Size", min_value=1, step=1, value=condition['window'])
                    operator = st.selectbox("Operator", [">", "<", ">=", "<=", "=="],
                                            index=[">", "<", ">=", "<=", "=="].index(condition['operator']))

                    if isinstance(condition['threshold'], (int, float)):
                        threshold_type = "Static Value"
                    else:
                        threshold_type = "Dynamic Comparison"

                    threshold_type = st.selectbox("Threshold Type", ["Static Value", "Dynamic Comparison"],
                                                  index=["Static Value", "Dynamic Comparison"].index(threshold_type))

                    if threshold_type == "Static Value":
                        threshold = st.number_input(
                            "Threshold Value",
                            step=0.01,
                            value=float(condition['threshold']) if isinstance(condition['threshold'],
                                                                              (int, float)) else 0.0,
                            format="%.2f",
                            help="Numeric threshold value."
                        )
                    else:
                        st.info("Define dynamic threshold based on another comparison.")
                        dyn_indicator = st.selectbox("Dynamic Indicator", ["RSI", "Volatility", "Cumulative Return"],
                                                     index=["RSI", "Volatility", "Cumulative Return"].index(
                                                         condition['threshold']['indicator']))
                        dyn_etf1 = st.text_input("Dynamic ETF 1 (e.g., BND UP EQUITY)",
                                                 value=condition['threshold'].get('etf1', ''))
                        dyn_etf2 = st.text_input("Dynamic ETF 2 (e.g., BIL UP EQUITY)",
                                                 value=condition['threshold'].get('etf2', ''))
                        dyn_window = st.number_input("Dynamic Window Size", min_value=1, step=1,
                                                     value=condition['threshold'].get('window', 1))
                        dyn_operator = st.selectbox("Dynamic Operator", [">", "<", ">=", "<=", "=="],
                                                    index=[">", "<", ">=", "<=", "=="].index(
                                                        condition['threshold'].get('operator', '>')))
                        threshold = {
                            "indicator": dyn_indicator,
                            "etf1": dyn_etf1,
                            "etf2": dyn_etf2,
                            "window": dyn_window,
                            "operator": dyn_operator
                        }

                    true_branch = st.selectbox("True Branch (Action/Condition Node Name)", options=all_node_names,
                                               index=all_node_names.index(condition['true_branch']) if condition[
                                                                                                           'true_branch'] in all_node_names else 0)
                    false_branch = st.selectbox("False Branch (Action/Condition Node Name)", options=all_node_names,
                                                index=all_node_names.index(condition['false_branch']) if condition[
                                                                                                             'false_branch'] in all_node_names else 0)

                    submitted = st.form_submit_button("Save Changes")
                    if submitted:
                        # Update the condition
                        condition['indicator'] = indicator
                        condition['etf'] = etf
                        condition['window'] = window
                        condition['operator'] = operator
                        condition['threshold'] = threshold
                        condition['true_branch'] = true_branch
                        condition['false_branch'] = false_branch

                        save_conditions(CONDITIONS_FILE, conditions)
                        st.success(f"Condition '{node_name}' updated successfully!")



def manage_actions():
    st.header("Manage Actions")
    actions = load_actions(ACTIONS_FILE)

    # Tabs for Adding and Editing Actions
    tab1, tab2 = st.tabs(["Add New Action", "Edit Existing Actions"])

    with tab1:
        st.subheader("Add New Action")
        with st.form("add_action"):
            action_name = st.text_input("Action Node Name", help="Unique identifier for the action node.")
            st.write("Define allocations:")

            etf_list = st.text_input("ETFs (comma-separated)", "SPY UP EQUITY, TLT US EQUITY",
                                     help="List of ETFs to allocate, separated by commas.")
            allocation_values = st.text_input("Allocations (comma-separated, in decimals)", "0.5, 0.5",
                                              help="Corresponding allocation percentages (in decimals) separated by commas.")

            submitted = st.form_submit_button("Save Action")
            if submitted:
                if not action_name:
                    st.error("Action node name cannot be empty.")
                elif action_name in actions:
                    st.error("Action node name already exists. Choose a unique name.")
                else:
                    etfs = [etf.strip() for etf in etf_list.split(",") if etf.strip()]
                    try:
                        allocations_vals = [float(val.strip()) for val in allocation_values.split(",") if val.strip()]
                    except ValueError:
                        st.error("Allocations must be numeric.")
                        allocations_vals = []

                    if len(etfs) != len(allocations_vals):
                        st.error("Number of ETFs and allocations must match.")
                    elif not etfs or not allocations_vals:
                        st.error("ETFs and allocations cannot be empty.")
                    else:
                        allocations = {etf: alloc for etf, alloc in zip(etfs, allocations_vals)}
                        if abs(sum(allocations_vals) - 1.0) > 1e-6:
                            st.warning("Allocations do not sum to 1.0. Please adjust accordingly.")
                        actions[action_name] = allocations
                        save_actions(ACTIONS_FILE, actions)
                        st.success(f"Action '{action_name}' saved successfully!")

    with tab2:
        st.subheader("Edit Existing Actions")
        if not actions:
            st.info("No actions available to edit.")
        else:
            action_names = list(actions.keys())
            selected_action = st.selectbox("Select Action to Edit", action_names)

            allocation_etfs = list(actions[selected_action].keys())
            allocation_vals = list(actions[selected_action].values())

            with st.form("edit_action"):
                st.text_input("Action Node Name", value=selected_action, disabled=True)
                st.write("Define allocations:")

                etf_list = st.text_input("ETFs (comma-separated)", ", ".join(allocation_etfs))
                allocation_values = st.text_input("Allocations (comma-separated, in decimals)",
                                                  ", ".join([f"{val:.2f}" for val in allocation_vals]))

                submitted = st.form_submit_button("Save Changes")
                if submitted:
                    etfs = [etf.strip() for etf in etf_list.split(",") if etf.strip()]
                    try:
                        allocations_vals = [float(val.strip()) for val in allocation_values.split(",") if val.strip()]
                    except ValueError:
                        st.error("Allocations must be numeric.")
                        allocations_vals = []

                    if len(etfs) != len(allocations_vals):
                        st.error("Number of ETFs and allocations must match.")
                    elif not etfs or not allocations_vals:
                        st.error("ETFs and allocations cannot be empty.")
                    else:
                        allocations = {etf: alloc for etf, alloc in zip(etfs, allocations_vals)}
                        if abs(sum(allocations_vals) - 1.0) > 1e-6:
                            st.warning("Allocations do not sum to 1.0. Please adjust accordingly.")
                        actions[selected_action] = allocations
                        save_actions(ACTIONS_FILE, actions)
                        st.success(f"Action '{selected_action}' updated successfully!")


def view_specs():
    st.header("View Specifications")

    # Load specifications
    conditions = load_conditions(CONDITIONS_FILE)
    actions = load_actions(ACTIONS_FILE)

    # Display Conditions
    st.subheader("Conditions")
    if not conditions:
        st.info("No conditions defined.")
    else:
        for condition in conditions:
            st.markdown(f"**{condition['node_name']}**")
            st.json(condition)

    # Display Actions
    st.subheader("Actions")
    if not actions:
        st.info("No actions defined.")
    else:
        for action_name, alloc in actions.items():
            st.markdown(f"**{action_name}**")
            st.json(alloc)

    # Download specifications
    st.subheader("Download Specifications")

    # Function to create download links
    def download_json(data, filename):
        json_str = json.dumps(data, indent=4)
        b64 = base64.b64encode(json_str.encode()).decode()  # some strings
        href = f'<a href="data:file/json;base64,{b64}" download="{filename}">Download {filename}</a>'
        return href

    if st.button("Download Conditions JSON"):
        st.markdown(download_json(conditions, 'conditions.json'), unsafe_allow_html=True)

    if st.button("Download Actions JSON"):
        st.markdown(download_json(actions, 'actions.json'), unsafe_allow_html=True)


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


if __name__ == "__main__":
    main()
