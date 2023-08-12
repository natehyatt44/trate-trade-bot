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
    df = pd.DataFrame(response.json()['data'], columns=columns)
    df['timestamp'] = pd.to_datetime(df['timestamp'].astype(int), unit='s')
    df.set_index('timestamp', inplace=True)
    df = df.astype(float)
    return df
