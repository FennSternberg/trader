import numpy as np


def get_asset_names(input: dict) -> [str, str]:
    """
    :param input: SpotTrade input dictionary
    :return: (buy asset name, sell asset name)
    """
    names = list(input['balances'].keys())
    return names[0], names[1]


def get_price_time_series(input: dict) -> [np.array, np.array]:
    times = np.array([x for x in input['time_series'].keys()])
    prices = np.array([val['ticker'] for key, val in input['time_series'].items()])
    return times, prices


if __name__ == "__main__":
    eg_input = {'balances': {'BTC': {'free': 1.0, 'locked': 0.0}, 'USDT': {'free': 9001.1136, 'locked': 1000.0}},
                'time_series': {1676824627.6407883: {'ticker': 24905.18}, 1676824646.8884954: {'ticker': 24925.73}},
                'open_orders': [{'symbol': 'BTCUSDT', 'orderId': 8513562, 'orderListId': -1,
                                 'clientOrderId': 'tPya9OAOWQvpKnIUOzoyhr', 'price': '20000.00000000',
                                 'origQty': '0.05000000', 'executedQty': '0.00000000',
                                 'cummulativeQuoteQty': '0.00000000', 'status': 'NEW', 'timeInForce': 'GTC',
                                 'type': 'LIMIT', 'side': 'BUY', 'stopPrice': '0.00000000', 'icebergQty': '0.00000000',
                                 'time': 1676821232966, 'updateTime': 1676821232966, 'isWorking': True,
                                 'workingTime': 1676821232966, 'origQuoteOrderQty': '0.00000000',
                                 'selfTradePreventionMode': 'NONE'}]}
