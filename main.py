import pandas as pd
# Import necessary functions from other files
from signals import (
    compute_macd, compute_bollinger_bands, compute_rsi, compute_vwap, compute_dca, generate_vwap_signals, generate_dca_signals,
    generate_macd_signals, generate_bollinger_signals, generate_rsi_signals, generate_combined_signals
)
from backtest import trading_simulation, generate_all_signals, test_combinations
from pricedata import fetch_kucoin_data


def main():
    symbols = ['ETH-USDT', 'BTC-USDT']
    for symbol in symbols:
        df = fetch_kucoin_data(symbol)

        # Compute Indicators
        df['macd'], df['signal'] = compute_macd(df)
        df['upper_band'], df['lower_band'] = compute_bollinger_bands(df)
        df['rsi'] = compute_rsi(df)
        df['vwap'] = compute_vwap(df)
        df['dca'] = compute_dca(df)

        # Generate Signals
        df = generate_all_signals(df)

        # Test all combinations and get results
        results_df = test_combinations(df)

        print(f"\nResults for {symbol}:")
        print(results_df.head(10))  # Display top 10 strategies


if __name__ == "__main__":
    main()
