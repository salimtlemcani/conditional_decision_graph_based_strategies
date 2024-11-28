import os
from strategy_builder import build_decision_tree_from_specs
from helper import allocate_values
import logging
import pandas as pd
import json

import sigtech.framework as sig


def basket_creation_method(strategy, dt, positions, **additional_parameters):
    size_date = pd.Timestamp(strategy.size_date_from_decision_dt(dt))
    midnight_dt = dt.replace(hour=0, minute=0, second=0, microsecond=0, tzinfo=None)
    example_dates = additional_parameters.get('example_dates', [])
    order = {}

    if midnight_dt not in example_dates:
        return {}

    # Build the context for the decision tree
    context = {
        'strategy': strategy,
        'dt': dt,
        'positions': positions,
        'additional_parameters': additional_parameters,
        'size_date': size_date,
        'midnight_dt': midnight_dt,
        'initial_cash': strategy.initial_cash,
        'etf_histories': additional_parameters.get('etf_histories', {}),
        'etfs': additional_parameters.get('etfs', {}),
    }

    # Retrieve condition and action specifications from JSON files
    conditions_file = additional_parameters.get('conditions_file', 'conditions.json')
    actions_file = additional_parameters.get('actions_file', 'actions.json')

    with open(conditions_file, 'r') as f:
        condition_specs = json.load(f)

    with open(actions_file, 'r') as f:
        action_specs = json.load(f)

    # Validate specifications
    from strategy_builder import validate_specs
    if not validate_specs(condition_specs, action_specs):
        logging.error("Invalid condition or action specifications. Aborting order generation.")
        return {}

    # Build and evaluate the decision tree
    try:
        decision_tree = build_decision_tree_from_specs(condition_specs, action_specs)
        if decision_tree is None:
            logging.error("Decision tree could not be built.")
            return {}
        order = decision_tree.evaluate(context)
        logging.info(f"Decision Tree Evaluation Result: {order}")
    except Exception as e:
        logging.error(f"Error evaluating decision tree: {e}")
        return {}

    # Convert allocations to orders
    try:
        orders = {context['etfs'][symbol]: weight for symbol, weight in allocate_values(context['etfs'], order).items()}
        logging.info(f"Generated Orders: {orders}")
        return orders
    except Exception as e:
        logging.error(f"Error during order allocation: {e}")
        return {}


def run_strategy(start_date, end_date, initial_cash, conditions_file, actions_file):
    print('\n')
    print('*'*30)
    print('\n')

    print(f'DEBUG [run_strategy] start_date {start_date}, end_date {end_date}, initial_cash {initial_cash}, conditions_file {conditions_file}, actions_file {actions_file}')
    # Initialize SigTech environment
    sig.init()

    # Define ETFs
    etf_names = [
        'TLT US EQUITY',
        'TQQQ US EQUITY',
        'SVXY US EQUITY',
        'VIXY US EQUITY',
        'QQQ UP EQUITY',
        'SPY UP EQUITY',
        'BND UP EQUITY',
        'BIL UP EQUITY',
        'GLD UP EQUITY',
    ]
    etfs = {name: sig.obj.get(name) for name in etf_names}
    print(f'DEBUG [run_strategy] etfs: {etfs}')
    # Retrieve ETF histories
    etf_histories = {name: etfs[name].history() for name in etf_names}

    # Prepare additional parameters
    additional_parameters = {
        'example_dates': etf_histories[next(iter(etf_histories))].index.tolist(),
        'etf_histories': etf_histories,
        'etfs': etfs,
        'conditions_file': conditions_file,
        'actions_file': actions_file,
    }

    # Initialize the Dynamic Strategy
    sig_strategy_object = sig.DynamicStrategy(
        currency='USD',
        start_date=start_date,
        end_date=end_date,
        trade_frequency='1BD',
        basket_creation_method=basket_creation_method,
        basket_creation_kwargs=additional_parameters,
        initial_cash=initial_cash,
    )

    # Build the strategy
    sig_strategy_object.build(progress=True)
    return sig_strategy_object
