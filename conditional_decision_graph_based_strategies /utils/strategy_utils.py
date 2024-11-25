
import os
import pickle
import sigtech.framework as sig

STRATEGY_DIR = 'strategies'

def save_strategy(strategy_object, strategy_name):
    strategy_file = os.path.join(STRATEGY_DIR, f"{strategy_name}.pkl")
    with open(strategy_file, 'wb') as f:
        pickle.dump(strategy_object, f)

def load_strategy(strategy_name):
    strategy_file = os.path.join(STRATEGY_DIR, f"{strategy_name}.pkl")
    with open(strategy_file, 'rb') as f:
        return pickle.load(f)

def list_saved_strategies():
    if not os.path.exists(STRATEGY_DIR):
        os.makedirs(STRATEGY_DIR)
    strategy_files = [f for f in os.listdir(STRATEGY_DIR) if f.endswith('.pkl')]
    strategy_names = [os.path.splitext(f)[0] for f in strategy_files]
    return strategy_names

def run_strategy(strategy_name, start_date, end_date, initial_cash, conditions_file, actions_file):
    # ... (logic from your run_new_strategy function)
    # Return the strategy_object
    return strategy_object
