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

    return result


def compare_cumulative_returns(context):
    """
    Computes the cumulative return of BND UP EQUITY and BIL UP EQUITY and returns BIL UP EQUITY's cumulative return as the threshold.

    :param context: Dictionary containing ETF histories and other parameters.
    :return: Cumulative return of BIL UP EQUITY.
    """
    cumul_bnd = get_cum_return(context['etf_histories']['BND UP EQUITY'].loc[:context['midnight_dt']], 60)
    cumul_bil = get_cum_return(context['etf_histories']['BIL UP EQUITY'].loc[:context['midnight_dt']], 60)
    return cumul_bil  # The threshold is BIL UP EQUITY's cumulative return


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
