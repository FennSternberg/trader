from helper_functions import get_asset_names
import json
import os


def strategy(default_input, custom_input):
    target_buy_balance_percent = custom_input[0]
    deviation_reset_percent = custom_input[1]
    startup = custom_input[2]  # TRUE on first call to market buy to correct portfolio balance
    buy_name, sell_name = get_asset_names(default_input)
    buy_balance = default_input['balances'][buy_name]['free'] + default_input['balances'][buy_name]['locked']
    sell_balance = default_input['balances'][sell_name]['free'] + default_input['balances'][sell_name]['locked']
    open_orders = default_input['open_orders']
    open_order_ids = [a['orderId'] for a in open_orders]
    order_history = default_input['order_history']
    price = default_input['price']
    if os.path.isfile('history.json'):
        with open('history.json') as json_file:
            history = json.load(json_file)
        history[buy_name] += [buy_balance]
        history[sell_name] += [sell_balance]
        history['Price'] += [price]
    else:
        history = {buy_name: [buy_balance], sell_name: [sell_balance], "Price": [price]}

    with open('history.json', 'w') as json_file:
        json.dump(history, json_file)

    if startup:
        custom_input[2] = False
        quantity = get_order_quantity(price, target_buy_balance_percent, buy_balance, sell_balance)
        if quantity != 0:
            if quantity < 0:
                quantity *= -1
                side = 'SELL'
            else:
                side = 'BUY'
            return ['MARKET'], [{"name": "initial_rebalance", "side": side, "quantity": quantity}], custom_input
    else:
        if 'balancer_buy' in list(order_history.keys()) and 'balancer_sell' in list(order_history.keys()):
            if (order_history['balancer_buy'] in open_order_ids) and (order_history['balancer_sell'] in open_order_ids):
                return ['PASS'], [{}], custom_input
            elif (order_history['balancer_buy'] in open_order_ids) and not (
                    order_history['balancer_sell'] in open_order_ids):
                return ['CANCEL'], [{'name': 'balancer_buy'}], custom_input
            elif not (order_history['balancer_buy'] in open_order_ids) and (
                    order_history['balancer_sell'] in open_order_ids):
                return ['CANCEL'], [{'name': 'balancer_sell'}], custom_input

    order = []
    action = []
    price_sell, price_buy = get_rebalance_prices(buy_balance, sell_balance, target_buy_balance_percent,
                                                 deviation_reset_percent)
    quantity_sell = -get_order_quantity(price_sell, target_buy_balance_percent, buy_balance, sell_balance)
    quantity_buy = get_order_quantity(price_buy, target_buy_balance_percent, buy_balance, sell_balance)

    action += ["LIMIT"]
    order += [{"name": "balancer_sell", "side": "SELL", "quantity": quantity_sell, "price": price_sell}]
    action += ["LIMIT"]
    order += [{"name": "balancer_buy", "side": "BUY", "quantity": quantity_buy, "price": price_buy}]
    return action, order, custom_input


def get_rebalance_prices(buy_balance: float, sell_balance: float, target_buy_balance_percent: float,
                         deviation_reset_percent: float):
    p_plus = sell_balance / buy_balance * (target_buy_balance_percent + deviation_reset_percent) / (
            100 - (target_buy_balance_percent + deviation_reset_percent))
    p_minus = sell_balance / buy_balance * (target_buy_balance_percent - deviation_reset_percent) / (
            100 - (target_buy_balance_percent - deviation_reset_percent))
    return p_plus, p_minus


def get_order_quantity(price: float, target_buy_balance_percent: float, buy_balance: float, sell_balance: float):
    return (target_buy_balance_percent * (price * buy_balance + sell_balance) - 100 * price * buy_balance) / (
            100 * price)


if __name__ == "__main__":
    eg_input = {'time_series': {1677183004.8279603: {'ticker': 23997.05}, 1677183032.3507125: {'ticker': 24008.22}},
                'balances': {'BTC': {'free': 0.70571, 'locked': 0.0}, 'USDT': {'free': 17183.30583882, 'locked': 0.0}},
                'price': 24008.22, 'open_orders': []}
