import pandas as pd
# Import necessary functions from other files
from signals import Signals
from backtest import trading_simulation, generate_all_signals, test_combinations
from pricedata import fetch_kucoin_data


def main():
    symbols = ['ETH-USDT', 'BTC-USDT']

    for symbol in symbols:
        df = fetch_kucoin_data(symbol)

        signal = Signals(df)

        # Compute Indicators
        df['macd'], df['signal'] = signal.compute_macd(df)
        df['upper_band'], df['lower_band'] = signal.compute_bollinger_bands(df)
        df['rsi'] = signal.compute_rsi(df)
        df['vwap'] = signal.compute_vwap(df)
        df['dca'] = signal.compute_dca(df, 24)

        # Generate Signals
        df = generate_all_signals(df)

        # Test all combinations and get results
        results_df = test_combinations(df)

        print(f"\nResults for {symbol}:")
        print(results_df.head(10))  # Display top 10 strategies


if __name__ == "__main__":
    main()
