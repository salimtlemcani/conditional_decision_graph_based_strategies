
import streamlit as st
from utils.data_utils import load_conditions, save_conditions, load_actions
from utils.decision_tree_utils import generate_dot


def manage_conditions():
    # File paths
    CONDITIONS_FILE = 'conditions.json'
    ACTIONS_FILE = 'actions.json'

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
