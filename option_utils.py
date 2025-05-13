def get_atm_strike_price(price: float, step=50) -> int:
    """
    Round price to nearest ATM strike based on step (default 50).
    """
    return round(price / step) * step


def get_option_symbol(symbol, expiry_str, strike_price, option_type):
    """
    Construct Angel One option symbol format.
    Example: RELIANCE 13MAY24 2800CE -> RELIANCE13MAY24C2800
    """
    option_type_letter = "C" if option_type.upper() == "CE" else "P"
    return f"{symbol}{expiry_str}{option_type_letter}{int(strike_price)}"
