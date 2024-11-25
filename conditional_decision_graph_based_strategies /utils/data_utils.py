
import json
import os
import pickle

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