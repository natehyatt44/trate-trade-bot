import requests
import pandas as pd
from datetime import datetime, timedelta


def fetch_kucoin_data(symbol, interval, max_records=1500, latest_date=None):
    """
    Fetch historical price data from Kucoin's API.
    """
    base_url = "https://api.kucoin.com/api/v1/market/candles"
    end_time = int(datetime.utcnow().timestamp())

    # If a latest_date is provided, set start_time to the day after. If not, set to one day ago.
    if latest_date:
        start_time = int((latest_date + timedelta(days=1)).timestamp())
    else:
        start_time = int((datetime.utcnow() - timedelta(days=365)).timestamp())

    columns = ["timestamp", "open", "close", "high", "low", "volume", "turnover"]
    all_data = []

    while end_time > start_time:
        response = requests.get(base_url, params={
            'symbol': symbol,
            'type': interval,
            'startAt': start_time,
            'endAt': end_time
        })

        data = response.json()['data']

        if not data:
            break

        all_data.extend(data)

        # Set the end time for the next request to be the timestamp of the oldest record from the current request
        end_time = int(data[-1][0])

        # If less than the maximum records are fetched, it means we've retrieved all available data
        if len(data) < max_records:
            break

    df = pd.DataFrame(all_data, columns=columns)
    df['timestamp'] = pd.to_datetime(df['timestamp'].astype(int), unit='s')
    df.set_index('timestamp', inplace=True)
    df = df.astype(float)
    return df



