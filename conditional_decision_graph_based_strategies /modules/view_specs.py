import streamlit as st
import base64
import json
import os

from utils.data_utils import load_conditions, load_actions


# Directory to store strategy objects
STRATEGY_DIR = 'strategies'


def view_specs(strategy_name):
    st.header("View Specifications")

    strategy_folder = os.path.join(STRATEGY_DIR, strategy_name)
    conditions_file = os.path.join(strategy_folder, 'conditions.json')
    actions_file = os.path.join(strategy_folder, 'actions.json')

    conditions = load_conditions(conditions_file)
    actions = load_actions(actions_file)

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
