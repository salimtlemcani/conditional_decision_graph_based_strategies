from utils.strategy_utils import load_strategy
import pprint

if __name__ == '__main__':
    o = load_strategy(strategy_name='strat1')
    pprint.pprint(o)

