import pandas as pd
# Import necessary functions from other files
from signals import (
    compute_macd, compute_bollinger_bands, compute_rsi, compute_vwap, generate_vwap_signals,
    generate_macd_signals, generate_bollinger_signals, generate_rsi_signals, generate_combined_signals
)
from backtest import trading_simulation, generate_all_signals, test_combinations
from pricedata import fetch_kucoin_data
import os
from datetime import datetime, timedelta


def main(days_to_use=30):
    symbols = ['ETH-USDT']
    interval = '1hour'

    for symbol in symbols:
        csv_filename = f"pricedata/{symbol}_{interval}.csv"

        # Check if CSV exists, if yes, load the latest date from it
        latest_date = None
        if os.path.exists(csv_filename):
            existing_df = pd.read_csv(csv_filename, parse_dates=['timestamp'])
            existing_df.set_index('timestamp', inplace=True)

            # Sort the DataFrame by the index to ensure the correct order
            existing_df.sort_index(inplace=True)
            latest_date = existing_df.index[-1]

        # Fetch data from Kucoin
        df = fetch_kucoin_data(symbol, interval=interval, latest_date=latest_date)

        # If CSV exists, merge the new data with existing data
        if os.path.exists(csv_filename):
            # Drop rows from new data that have timestamps already present in the existing data
            df = df[~df.index.isin(existing_df.index)]

            # Concatenate the new data with the existing data
            df = pd.concat([existing_df, df])

            # Drop any potential duplicates based on the timestamp
            df = df[~df.index.duplicated(keep='last')]

            # Sort the DataFrame in descending order based on the timestamp
            df.sort_index(ascending=False, inplace=True)

        # Save to CSV
        df.to_csv(csv_filename)

        # Filter dataframe to keep only the most recent days_to_use days
        cutoff_date = datetime.utcnow() - timedelta(days=days_to_use)
        df = df[df.index > cutoff_date]

        # Compute Indicators
        df['macd'], df['signal'] = compute_macd(df)
        df['upper_band'], df['lower_band'] = compute_bollinger_bands(df)
        df['rsi'] = compute_rsi(df)
        df['vwap'] = compute_vwap(df)

        # Generate Signals
        df = generate_all_signals(df)

        # Test all combinations and get results
        results_df = test_combinations(df)

        print(f"\nResults for {symbol}:")
        print(results_df.head(10))  # Display top 10 strategies


if __name__ == "__main__":
    main()
