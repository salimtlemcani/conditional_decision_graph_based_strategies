import streamlit as st
import json
import os

# File paths
CONDITIONS_FILE = '../conditions.json'
ACTIONS_FILE = '../actions.json'


def load_specs(file_path):
    if os.path.exists(file_path):
        with open(file_path, 'r') as f:
            return json.load(f)
    return []


def save_specs(file_path, data):
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
    conditions = load_specs(CONDITIONS_FILE)

    # Form to add a new condition
    with st.form("add_condition"):
        st.subheader("Add New Condition")
        node_name = st.text_input("Node Name")
        indicator = st.selectbox("Indicator", ["RSI", "Volatility", "Cumulative Return"])
        etf = st.text_input("ETF Name (e.g., QQQ UP EQUITY)")
        window = st.number_input("Window Size", min_value=1, step=1)
        operator = st.selectbox("Operator", [">", "<", ">=", "<=", "=="])

        threshold_type = st.selectbox("Threshold Type", ["Static Value", "Dynamic Comparison"])

        if threshold_type == "Static Value":
            threshold = st.number_input("Threshold Value", step=0.01)
        else:
            st.info("Define dynamic threshold based on another comparison.")
            dyn_indicator = st.selectbox("Dynamic Indicator", ["RSI", "Volatility", "Cumulative Return"])
            dyn_etf1 = st.text_input("Dynamic ETF 1 (e.g., BND UP EQUITY)")
            dyn_etf2 = st.text_input("Dynamic ETF 2 (e.g., BIL UP EQUITY)")
            dyn_window = st.number_input("Dynamic Window Size", min_value=1, step=1)
            dyn_operator = st.selectbox("Dynamic Operator", [">", "<", ">=", "<=", "=="])
            threshold = {
                "indicator": dyn_indicator,
                "etf1": dyn_etf1,
                "etf2": dyn_etf2,
                "window": dyn_window,
                "operator": dyn_operator
            }

        true_branch = st.text_input("True Branch (Action Node Name)")
        false_branch = st.text_input("False Branch (Action Node Name or Another Condition Node)")

        submitted = st.form_submit_button("Add Condition")
        if submitted:
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
            save_specs(CONDITIONS_FILE, conditions)
            st.success("Condition added successfully!")

    # Display existing conditions
    st.subheader("Existing Conditions")
    for condition in conditions:
        st.markdown(f"**{condition['node_name']}**")
        st.json(condition)


def manage_actions():
    st.header("Manage Actions")
    actions = {}
    if os.path.exists(ACTIONS_FILE):
        with open(ACTIONS_FILE, 'r') as f:
            actions = json.load(f)

    # Form to add/edit an action
    with st.form("add_action"):
        st.subheader("Add/Edit Action")
        action_name = st.text_input("Action Node Name")
        st.write("Define allocations:")

        allocations = {}
        etf_list = st.text_input("ETFs (comma-separated)", "SPY UP EQUITY, TLT US EQUITY")
        allocation_values = st.text_input("Allocations (comma-separated, in decimals)", "0.5, 0.5")

        submitted = st.form_submit_button("Save Action")
        if submitted:
            etfs = [etf.strip() for etf in etf_list.split(",")]
            allocations_vals = [float(val.strip()) for val in allocation_values.split(",")]
            if len(etfs) != len(allocations_vals):
                st.error("Number of ETFs and allocations must match.")
            else:
                allocations = {etf: alloc for etf, alloc in zip(etfs, allocations_vals)}
                actions[action_name] = allocations
                save_specs(ACTIONS_FILE, actions)
                st.success("Action saved successfully!")

    # Display existing actions
    st.subheader("Existing Actions")
    for action_name, alloc in actions.items():
        st.markdown(f"**{action_name}**")
        st.json(alloc)


def view_specs():
    st.header("View Specifications")

    # Load and display conditions
    st.subheader("Conditions")
    conditions = load_specs(CONDITIONS_FILE)
    for condition in conditions:
        st.markdown(f"**{condition['node_name']}**")
        st.json(condition)

    # Load and display actions
    st.subheader("Actions")
    actions = {}
    if os.path.exists(ACTIONS_FILE):
        with open(ACTIONS_FILE, 'r') as f:
            actions = json.load(f)
    for action_name, alloc in actions.items():
        st.markdown(f"**{action_name}**")
        st.json(alloc)


if __name__ == "__main__":
    main()
