import logging

def get_rsi(data, window):
    delta = data.diff()
    up = delta.clip(lower=0)
    down = -delta.clip(upper=0)
    avg_gain = up.ewm(com=window - 1, adjust=True).mean()
    avg_loss = down.ewm(com=window - 1, adjust=True).mean()
    rs = avg_gain / avg_loss
    rsi_series = 100 - (100 / (1 + rs))
    return rsi_series


def get_vol(data, window):
    returns = data.pct_change()
    return returns.rolling(window).std()


def get_cum_return(data, window):
    returns = data.pct_change()
    cumulative_returns = (returns + 1).rolling(window).apply(lambda x: x.prod(), raw=True) - 1
    return cumulative_returns.iloc[-1] if len(cumulative_returns) >= window else 0


def allocate_values(default_keys, allocations=None):
    """
    Allocates values to keys in a dictionary. Keys without specific allocations are set to 0.

    :param default_keys: List of keys that should be present in the dictionary.
    :param allocations: Dictionary of keys with their allocated values. If None, all keys will be set to 0.
    :return: Dictionary with allocated values.
    """
    # Initialize the dictionary with 0 for all keys
    result = {key: 0 for key in default_keys}

    # If allocations are provided, update the dictionary with those values
    if allocations:
        for key, value in allocations.items():
            if key in result:
                result[key] = value
            else:
                logging.warning(f"Allocation for unknown ETF '{key}' ignored.")
    return result



def create_comparison_function(indicator_name, etf1, etf2, window=60, operator='>'):
    """
    Creates a comparison function based on the provided parameters.

    :param indicator_name: Name of the indicator (e.g., 'cumulative return', 'rsi').
    :param etf1: The primary ETF to compare.
    :param etf2: The secondary ETF to use as a threshold.
    :param window: The window size for indicator calculation.
    :param operator: The comparison operator as a string ('>', '<', '>=', '<=', '==').
    :return: A function that takes context and returns the result of the comparison.
    """
    def comparison(context):
        # Retrieve indicator values for both ETFs
        value1 = get_indicator_value(context, {'name': indicator_name, 'etf': etf1}, window)
        value2 = get_indicator_value(context, {'name': indicator_name, 'etf': etf2}, window)
        
        # Perform the comparison based on the operator
        try:
            if operator == '>':
                return value1 > value2
            elif operator == '<':
                return value1 < value2
            elif operator == '>=':
                return value1 >= value2
            elif operator == '<=':
                return value1 <= value2
            elif operator == '==':
                return value1 == value2
            else:
                raise ValueError(f"Unsupported operator: {operator}")
        except Exception as e:
            logging.error(f"Error during comparison: {e}")
            return False
    
    # Assign a name for better logging/debugging
    comparison.__name__ = f"compare_{etf1}_to_{etf2}_{indicator_name}"
    return comparison
    

def get_indicator_value(context, indicator: dict, window: int) -> float:
    """
    Retrieves the indicator value from the ETF history.

    :param context: Dictionary containing ETF histories and other parameters.
    :param indicator: Dictionary with 'name' and 'etf' keys.
    :param window: Window size for the indicator (if applicable).
    :return: Indicator value.
    """
    etf = indicator['etf']
    name = indicator['name']

    if name.lower() == 'rsi':
        return get_rsi(context['etf_histories'][etf], window).loc[context['midnight_dt']]
    elif name.lower() == 'volatility':
        return get_vol(context['etf_histories'][etf], window).loc[context['midnight_dt']]
    elif name.lower() == 'cumulative return':
        return get_cum_return(context['etf_histories'][etf].loc[:context['midnight_dt']], window)
    else:
        raise ValueError(f"Unsupported indicator: {name}")
