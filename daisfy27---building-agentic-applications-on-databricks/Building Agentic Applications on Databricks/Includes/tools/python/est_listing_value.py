def est_listing_value(
    my_param: float,
    param2: float,
    param3: str
) -> str:
    """
    This is my calculation function.

    Args:
        my_param: a number
        param2: a number
        param3: a string

    Returns:
        str: result
    """
    base_value = my_param * 365 * 0.7  # assume 70% occupancy
    bedroom_factor = 1 + (param2 - 1) * 0.15
    if param3.lower() == 'entire home/apt':
        multiplier = 1.2
    elif param3.lower() == 'private room':
        multiplier = 0.8
    else:
        multiplier = 0.5
    estimated = base_value * bedroom_factor * multiplier
    return f"Estimated annual revenue: ${estimated:,.2f}"