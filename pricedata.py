import requests
import pandas as pd
from datetime import datetime, timedelta

def fetch_kucoin_data(symbol, interval='1hour', lookback_period=365):
    """
    Fetch historical price data from Kucoin's API.
    """
    base_url = "https://api.kucoin.com/api/v1/market/candles"
    end_time = int(datetime.utcnow().timestamp())
    start_time = int((datetime.utcnow() - timedelta(days=lookback_period)).timestamp())
    response = requests.get(base_url, params={
        'symbol': symbol,
        'type': interval,
        'startAt': start_time,
        'endAt': end_time
    })
    columns = ["timestamp", "open", "close", "high", "low", "volume", "turnover"]

    if response.status_code == 200:
        try:
            df = pd.DataFrame(response.json()['data'], columns=columns)
            df['timestamp'] = pd.to_datetime(df['timestamp'].astype(int), unit='s')
            df.set_index('timestamp', inplace=True)
            df = df.astype(float)
            return df
        except Exception as e:
            raise Exception(f"Error getting kucoin data: {e} ")

    else:
        raise Exception(f"Error getting kucoin data as response code was : {response.status_code}")


"""
interval example = 1h
Need to figure out how to calculate turnover from binance.
Limit = number of data points to retrieve
Need binance api key if want to use it
"""
def fetch_binance_data(symbol, interval="1h", limit=1000):
    endpoint = "https://api.binance.com/api/v3/klines"

    params = {
        "symbol": symbol,
        "interval": interval,
        "limit": limit
    }

    response = requests.get(endpoint, params=params)
    data = response.json()

    if response.status_code == 200:
        df = pd.DataFrame(data, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume', 'close_time',
                                         'quote_asset_volume', 'number_of_trades', 'taker_buy_base_asset_volume',
                                         'taker_buy_quote_asset_volume', 'ignore'])
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        return df
    else:
        raise Exception(f"Error getting historical binance klines: {data}")