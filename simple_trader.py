import binance
from secret_key_method import key, secret
import time
from typing import Union


class SpotTrader:
    def __init__(self, api_key: str, api_secret: str, asset1: str, asset2: str):
        self.client = binance.Client(api_key, api_secret)
        self.asset1 = asset1
        self.asset2 = asset2
        self.balances = self.update_spot_balance(update=False)
        self.current_time, self.current_ticker = self.update_ticker(update=False)
        self.input = {}
        self.start_time = 0

    def run(self, refresh_rate: float = 1, historic_interval=False, historic_limit=False):
        self.input['balances'] = self.balances
        self.input['time_series'] = self.get_historic_data(historic_interval, historic_limit)
        self.start_time = time.time()
        while time.time() - self.start_time < 10:
            self.update_ticker()
            self.input['time_series'][self.current_time] = {'ticker': self.current_ticker}
            print(f'time:{self.current_time} price:{self.current_ticker}')
            time.sleep(refresh_rate)

    def get_historic_data(self, interval: Union[str, bool], limit: Union[int, bool]) -> dict:
        """
        :param interval: interval to collect data over must be  "1m", "3m", "5m", "15m",
                        "30m", "1h", "2h", "4h", "6h", "8h", "12h", "1d", "3d", "1w", or "1M"
        :param limit: number of intervals to collect, max 1000
        :return:
        """
        # returns [
        #           [
        #           open time, open, high, low, close, volume, close time, quote asset value,
        #           number of trades, taker buy asset volume, take buy quote asset volume, ignore
        #           ]..
        #         ]
        if interval:
            historic_data = self.client.get_klines(symbol=f'{self.asset1}{self.asset2}', interval=interval, limit=limit)
        else:
            historic_data = []
        return {x[0]: {'ticker': x[1]} for x in historic_data}

    def update_spot_balance(self, update: bool = True) -> dict:
        """
        :param update: update the SpotTrader object balances attribute or not
        :return:current spot balances of both the assets in the trading pair
        {
            asset1:free_balance,
            asset2:free_balance
        }
        """
        asset1_balance = self.client.get_asset_balance(self.asset1)
        asset2_balance = self.client.get_asset_balance(self.asset2)
        spot_balances = {
            self.asset1: asset1_balance['free'],
            self.asset2: asset2_balance['free']
        }
        if update:
            self.balances = spot_balances
        return spot_balances

    def update_ticker(self, update: bool = True) -> [float, float]:
        """
        :param update: update the SpotTrader object ticker attribute or not
        :return: current time, current price of the market
        """
        ticker = float(self.client.get_symbol_ticker(symbol=f'{self.asset1}{self.asset2}')['price'])
        current_time = time.time()
        if update:
            self.current_ticker = ticker
            self.current_time = current_time
        return current_time, ticker


if __name__ == "__main__":
    trader = SpotTrader(key, secret, 'LDO', 'USDT')
