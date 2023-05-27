import numpy as np
from helper_functions import get_asset_names
import time


def find_price_target(time, price_y, t_star):
    return np.interp(t_star, time, price_y)


def strategy(default_input, custom_input):
    current_time = time.time()
    f_t = default_input['time']
    f_buy_range = default_input['buy']['range']
    f_buy_stop = default_input['buy']['stop']
    f_sell_range = default_input['sell']['range']
    f_sell_stop = default_input['sell']['stop']
    open_orders = default_input['open_orders']
    buy_name, sell_name = get_asset_names(default_input)
    buy_balance = default_input['balances'][buy_name]['free'] * 0.99
    sell_balance = default_input['balances'][sell_name]['free'] * 0.99
    current_price = default_input['price']
    buy_range_price = find_price_target(f_t, f_buy_range, current_time)
    sell_range_price = find_price_target(f_t, f_sell_range, current_time)
    buy_stop_price = find_price_target(f_t, f_buy_stop, current_time)
    sell_stop_price = find_price_target(f_t, f_sell_stop, current_time)

    action = ['PASS']
    order = [{}]

    # what about if the orders don't exist??
    action += ['CANCEL']
    order += [{'name': 'buyer'}]

    action += ['CANCEL']
    order += [{'name': 'seller'}]

    # need to make it do a market order if the price has already passed the designated value(s)
    if buy_balance > 30:
        action += ['OCO']
        order += [
            {'name': 'buyer', 'side': 'BUY', 'quantity': buy_balance, 'price': buy_range_price, 'stop': buy_stop_price}]
    if sell_balance > 0.01:
        action += ['OCO']
        order += [{'name': 'seller', 'side': 'SELL', 'quantity': sell_balance, 'price': sell_range_price,
                   'stop': sell_stop_price}]

    return action, order, custom_input


if __name__ == "__main__":
    t = np.linspace(1, 10, 100)
    p = np.sin(t)
