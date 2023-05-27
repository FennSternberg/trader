import numpy as np
from helper_functions import get_price_time_series, get_asset_names


def constant_proportion_portfolio_rebalancing():
    return None


def get_rebalance_prices(Bb: float, Bs: float, Tb: float, db: float):
    p_plus = Bs / Bb * (Tb + db) / (100 - (Tb + db))
    p_minus = Bs / Bb * (Tb - db) / (100 - (Tb - db))
    return p_plus, p_minus

def get_order_quantity(p:float, Tb:float, Bb:float,Bs:float):
    return (Tb*(p*Bb + Bs)-100*p*Bb)/(100*p)

if __name__ == "__main__":
    eg_input = {'balances': {'BTC': {'free': 1.0, 'locked': 0.0}, 'USDT': {'free': 10001.1136, 'locked': 0.0}},
                'time_series': {1676826591.9559658: {'ticker': 24533.09}, 1676826624.2525887: {'ticker': 24540.66},
                                1676826656.3686666: {'ticker': 24488.79}, 1676826689.1315017: {'ticker': 24502.05}},
                'open_orders': []}
