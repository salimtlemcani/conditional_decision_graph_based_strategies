
import streamlit as st
import os

from utils.data_utils import load_actions, save_actions


def manage_actions(strategy_name):
    STRATEGY_DIR = 'strategies'

    strategy_folder = os.path.join(STRATEGY_DIR, strategy_name)
    actions_file = os.path.join(strategy_folder, 'actions.json')

    actions = load_actions(actions_file)

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
                        save_actions(actions_file, actions)
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
                        save_actions(actions_file, actions)
                        st.success(f"Action '{selected_action}' updated successfully!")
