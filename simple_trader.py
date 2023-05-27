import binance
import time
from typing import Union
from portfolio_rebalancing import strategy


class SpotTrader:
    def __init__(self, api_key: str, api_secret: str, asset_buy: str, asset_sell: str, testnet: bool = False):
        self.client = binance.Client(api_key, api_secret, testnet=testnet)
        self.asset_buy = asset_buy
        self.asset_sell = asset_sell
        self.symbol = f'{asset_buy}{asset_sell}'
        self.balances = self.update_spot_balance(update=False)
        self.starting_balance = self.balances
        self.current_time, self.current_ticker = self.update_ticker(update=False)
        self.input = {}
        self.start_time = 0
        self.order_history = {}

    def run(self, custom_function, custom_input=None, refresh_rate: float = 5, run_time=10, time_keep=60 * 60,
            historic_interval=False, historic_limit=False):
        print('running, orders will appear below when they are placed')
        self.input['time_series'] = self.get_historic_data(historic_interval, historic_limit)
        self.start_time = time.time()
        while time.time() - self.start_time < run_time:
            self.input['balances'] = self.balances
            self.input['time_series'][self.current_time] = {'ticker': self.current_ticker}
            self.input['time_series'] = {dict_key: value for dict_key, value in self.input['time_series'].items() if
                                         self.current_time - dict_key < time_keep}
            self.input['price'] = self.current_ticker
            self.input['open_orders'] = self.get_open_orders()
            self.input['order_history'] = self.order_history
            actions, params, custom_input = custom_function(self.input, custom_input)
            self.handle_response(actions, params)
            time.sleep(refresh_rate)
            self.update_ticker()

    def handle_response(self, actions: str, params: dict):
        """
        execute the order specified from the response
        :param actions: list of actions to take "MARKET" , "LIMIT" or "PASS"
        :param params: list of dictionaries of accompanying parameters
        """
        for i in range(len(actions)):
            action = actions[i]
            param = params[i]
            if action == "PASS":
                print('.')
                pass
            elif action == "MARKET":
                order = self.place_market_order(param['side'], round(param['quantity'], 4))
                self.order_history[param['name']] = order['orderId']
                print(f'order placed: {order}')
                print(f'{self.update_spot_balance()}')
            elif action == "LIMIT":
                order = self.place_limit_order(param['side'], round(param['quantity'], 4), round(param['price'], 2))
                self.order_history[param['name']] = order['orderId']
                print(f'order placed: {order}')
                print(f'{self.update_spot_balance()}')
            elif action == "CANCEL":
                self.cancel_order(self.order_history[param['name']])
                print(f'cancelled order {param["name"]} : {self.order_history[param["name"]]}')
            elif action == "OCO":
                order = self.place_oco_order(param['side'], round(param['quantity'], 4), round(param['price'], 2),
                                             round(param['stop'], 2))
                print(f'order placed {order}')
            else:
                print('?')
                pass

    def place_market_order(self, side: str, quantity: float):
        if side == "BUY":
            response = self.client.order_market_buy(symbol=self.symbol, quantity=quantity)
        elif side == "SELL":
            response = self.client.order_market_sell(symbol=self.symbol, quantity=quantity)
        else:
            response = {}
        return response

    def place_limit_order(self, side: str, quantity: float, price: float):
        if side == "BUY":
            response = self.client.order_limit_buy(symbol=self.symbol, quantity=quantity, price=price)
        elif side == "SELL":
            response = self.client.order_limit_sell(symbol=self.symbol, quantity=quantity, price=price)
        else:
            response = {}
        return response

    def place_oco_order(self, side: str, quantity: float, price: float, stop: float):
        from binance.enums import TIME_IN_FORCE_GTC, SIDE_SELL, SIDE_BUY
        if side == "BUY":
            response = self.client.create_oco_order(
                symbol=self.symbol,
                side=SIDE_BUY,
                stopLimitTimeInForce=TIME_IN_FORCE_GTC,
                quantity=quantity,
                stopPrice=stop,
                price=price)
        elif side == "SELL":
            response = self.client.create_oco_order(
                symbol=self.symbol,
                side=SIDE_SELL,
                stopLimitTimeInForce=TIME_IN_FORCE_GTC,
                quantity=quantity,
                stopPrice=stop,
                price=price)
        else:
            response = {}

        return response

    def cancel_order(self, order_id):
        response = self.client.cancel_order(symbol=self.symbol, orderId=order_id)
        return response

    def get_open_orders(self):
        response = self.client.get_open_orders(symbol=self.symbol)
        return response

    def get_all_orders(self):
        response = self.client.get_all_orders(symbol=self.symbol)
        return response

    def get_historic_data(self, interval: Union[str, bool], limit: Union[int, bool]) -> dict:
        """
        :param interval: interval to collect data over must be  "1m", "3m", "5m", "15m",
                        "30m", "1h", "2h", "4h", "6h", "8h", "12h", "1d", "3d", "1w", or "1M"
        :param limit: number of intervals to collect, max 1000
        :return:
        """
        if interval:
            historic_data = self.client.get_klines(symbol=self.symbol, interval=interval, limit=limit)
        else:
            historic_data = []
        return {x[0] / 1000: {'ticker': x[1]} for x in historic_data}

    def update_spot_balance(self, update: bool = True) -> dict:
        """
        :param update: update the SpotTrader object balances attribute or not
        :return:current spot balances of both the assets in the trading pair
        {
            asset1:free_balance,
            asset2:free_balance
        }
        """
        asset1_balance = self.client.get_asset_balance(self.asset_buy)
        asset2_balance = self.client.get_asset_balance(self.asset_sell)
        spot_balances = {
            self.asset_buy: {'free': float(asset1_balance['free']), 'locked': float(asset1_balance['locked'])},
            self.asset_sell: {'free': float(asset2_balance['free']), 'locked': float(asset2_balance['locked'])}
        }
        if update:
            self.balances = spot_balances
        return spot_balances

    def update_ticker(self, update: bool = True) -> tuple[float, float]:
        """
        :param update: update the SpotTrader object ticker attribute or not
        :return: current time, current price of the market
        """
        ticker = float(self.client.get_symbol_ticker(symbol=self.symbol)['price'])
        current_time = time.time()
        if update:
            self.current_ticker = ticker
            self.current_time = current_time
        return current_time, ticker


def pass_function(input, x):
    return 'Pass', {}, {}


if __name__ == "__main__":
    # Test Net APR keys and Secret
    key = "hYVuz4furbR4EfkOiVqKQObReKMAyHlg40pPiLkxk9UhDVSZ48CX7qbrsPrn1sU0"
    secret = "6frzZyGogpsCacXwhKq8mzEWKYUp7xVDT8JyHgN82SpBdUZmRgHF2AFkkxqzf0fJ"
    trader = SpotTrader(key, secret, 'BTC', 'USDT', testnet=True)
    open_orders = trader.get_open_orders()
    for open_order in open_orders:
        trader.cancel_order(open_order['orderId'])
    trader.run(strategy, custom_input=[50, 0.1, True], run_time=60 * 60 * 8, refresh_rate=30)
