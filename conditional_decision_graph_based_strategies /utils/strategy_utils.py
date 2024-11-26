
import os
import pickle

STRATEGY_DIR = 'strategies'


def save_strategy(strategy_object, strategy_name):
    strategy_file = os.path.join(STRATEGY_DIR, f"{strategy_name}.pkl")
    with open(strategy_file, 'wb') as f:
        pickle.dump(strategy_object, f)


def load_strategy(strategy_name):
    strategy_folder = os.path.join(STRATEGY_DIR, strategy_name)
    if not os.path.exists(strategy_folder):
        return None  # Folder does not exist
    strategy_file = os.path.join(strategy_folder, 'strategy.pkl')
    if not os.path.exists(strategy_file):
        return None  # File does not exist
    with open(strategy_file, 'rb') as f:
        strategy_object = pickle.load(f)
    return strategy_object


def list_saved_strategies():
    if not os.path.exists(STRATEGY_DIR):
        os.makedirs(STRATEGY_DIR)
    strategy_files = [f for f in os.listdir(STRATEGY_DIR) if f.endswith('.pkl')]
    strategy_names = [os.path.splitext(f)[0] for f in strategy_files]
    return strategy_names
