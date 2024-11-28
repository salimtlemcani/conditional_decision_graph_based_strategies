import streamlit as st
import os

# Directory to store strategy objects
STRATEGY_DIR = 'strategies'


def add_strategy():
    st.title('Add or Select Strategy')

    # Ensure the base directory exists
    if not os.path.exists(STRATEGY_DIR):
        os.makedirs(STRATEGY_DIR)

    # Input field to add a strategy
    with st.form("strategy_params"):
        strategy_name = st.text_input("Strategy Name", help="Provide a unique name for your strategy.")
        submitted = st.form_submit_button("Add Strategy")

    if submitted:
        if not strategy_name:
            st.error("Strategy name cannot be empty.")
            return

        # Check if strategy with the same name exists
        strategy_folder = os.path.join(STRATEGY_DIR, strategy_name)
        if os.path.exists(strategy_folder):
            st.error("Strategy name already exists. Please choose another name.")
            return

        # Create a new folder for the strategy
        try:
            os.makedirs(strategy_folder)
            st.session_state['selected_strategy_name'] = strategy_name
            st.session_state['app_mode'] = 'Manage Conditions'  # Navigate to desired page
            print("DEBUG [add_strategy] rerunning the app")
            st.rerun()  # Trigger a rerun to refresh the app
        except Exception as e:
            st.error(f"An error occurred while creating the strategy folder: {e}")
