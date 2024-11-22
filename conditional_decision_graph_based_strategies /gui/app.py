import streamlit as st
import json
import os
import base64

# File paths
CONDITIONS_FILE = '../conditions.json'  # Adjust path as needed
ACTIONS_FILE = '../actions.json'        # Adjust path as needed


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


def main():
    st.title("Trading Strategy Builder")

    # Sidebar for navigation
    st.sidebar.header("Options")
    app_mode = st.sidebar.selectbox("Choose Option", ["Manage Conditions", "Manage Actions", "View Specifications"])

    if app_mode == "Manage Conditions":
        manage_conditions()
    elif app_mode == "Manage Actions":
        manage_actions()
    elif app_mode == "View Specifications":
        view_specs()


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
                dyn_window = st.number_input("Dynamic Window Size", min_value=1, step=1, help="Time window for the dynamic comparison.")
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
                                            index=["RSI", "Volatility", "Cumulative Return"].index(condition['indicator']))
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
                            value=float(condition['threshold']) if isinstance(condition['threshold'], (int, float)) else 0.0,
                            format="%.2f",
                            help="Numeric threshold value."
                        )
                    else:
                        st.info("Define dynamic threshold based on another comparison.")
                        dyn_indicator = st.selectbox("Dynamic Indicator", ["RSI", "Volatility", "Cumulative Return"],
                                                    index=["RSI", "Volatility", "Cumulative Return"].index(condition['threshold']['indicator']))
                        dyn_etf1 = st.text_input("Dynamic ETF 1 (e.g., BND UP EQUITY)", value=condition['threshold'].get('etf1', ''))
                        dyn_etf2 = st.text_input("Dynamic ETF 2 (e.g., BIL UP EQUITY)", value=condition['threshold'].get('etf2', ''))
                        dyn_window = st.number_input("Dynamic Window Size", min_value=1, step=1,
                                                    value=condition['threshold'].get('window', 1))
                        dyn_operator = st.selectbox("Dynamic Operator", [">", "<", ">=", "<=", "=="],
                                                    index=[">", "<", ">=", "<=", "=="].index(condition['threshold'].get('operator', '>')))
                        threshold = {
                            "indicator": dyn_indicator,
                            "etf1": dyn_etf1,
                            "etf2": dyn_etf2,
                            "window": dyn_window,
                            "operator": dyn_operator
                        }

                    true_branch = st.selectbox("True Branch (Action/Condition Node Name)", options=all_node_names,
                                               index=all_node_names.index(condition['true_branch']) if condition['true_branch'] in all_node_names else 0)
                    false_branch = st.selectbox("False Branch (Action/Condition Node Name)", options=all_node_names,
                                                index=all_node_names.index(condition['false_branch']) if condition['false_branch'] in all_node_names else 0)

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


if __name__ == "__main__":
    main()
