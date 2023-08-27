import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import concurrent.futures
from itertools import combinations
from signals import (
    compute_macd, compute_bollinger_bands, compute_rsi, compute_vwap, generate_vwap_signals,
    generate_macd_signals, generate_bollinger_signals, generate_rsi_signals, generate_combined_signals
)

def trading_simulation(df, signal_column, initial_capital=1000, trade_percent=0.05, max_trades_per_day=2, stop_loss=0.10):
    capital = initial_capital
    portfolio = []
    open_positions = []
    trades_today = 0
    current_day = None

    for i, row in df.iterrows():
        date, price, signal_value = i, row['close'], row[signal_column]

        # Reset daily trades counter
        if current_day is None or current_day != date.date():
            current_day = date.date()
            trades_today = 0

        # Check for open positions and apply stop loss
        for position in open_positions:
            if price < (1 - stop_loss) * position['buy_price']:
                capital += position['amount'] * price
                portfolio.append({'date': date, 'action': 'sell (stop loss)', 'price': price, 'capital': capital})
                open_positions.remove(position)
                trades_today += 1

        # Execute trades based on the signal value
        if trades_today < max_trades_per_day:
            trade_value = capital * trade_percent

            if signal_value > 0 and trade_value <= capital:  # Buy signal
                asset_amount = trade_value / price
                capital -= trade_value
                # Record the current bullish signals for this trade
                current_signals = [signal for signal in df.loc[date][df.loc[date] > 0].index if "_signal" in signal]
                open_positions.append({
                    'buy_price': price,
                    'amount': asset_amount,
                    'trade_value': trade_value,
                    'bullish_signals': current_signals
                })
                portfolio.append({'date': date, 'action': 'buy', 'price': price, 'capital': capital})
                trades_today += 1

            elif signal_value <= 0:  # If the signal is bearish or neutral
                for position in open_positions:
                    # Check if any of the bullish signals for this trade have turned bearish or neutral
                    if any(signal not in df.loc[date][df.loc[date] > 0].index for signal in position['bullish_signals']):
                        capital += position['amount'] * price
                        portfolio.append({'date': date, 'action': 'sell', 'price': price, 'capital': capital})
                        open_positions.remove(position)
                        trades_today += 1

    # Sell remaining positions at the end
    for position in open_positions:
        capital += position['trade_value']
        portfolio.append({'date': date, 'action': 'sell (end)', 'price': price, 'capital': capital})

    portfolio_df = pd.DataFrame(portfolio)
    return capital, portfolio_df

def generate_all_signals(df):
    df = generate_macd_signals(df)
    df = generate_bollinger_signals(df)
    df = generate_rsi_signals(df)
    df = generate_vwap_signals(df)
    return df



def test_combinations(df, initial_capital=1000, trade_percent=0.05, max_trades_per_day=2, stop_loss=0.10):
    results = []

    start_trade_percent = 0.05
    end_trade_percent = 0.30
    step_size = 0.05

    trade_percent_values = [round(x, 2) for x in
                            list(np.arange(start_trade_percent, end_trade_percent + step_size, step_size))]

    stop_loss_values = [round(x, 2) for x in
                            list(np.arange(start_trade_percent, end_trade_percent + step_size, step_size))]

    # Test individual signals
    signal_columns = ['macd_signal', 'bollinger_signal', 'rsi_signal', 'vwap_signal']

    def simulate_strategy(signal, trade_percent, stop_loss):
        final_capital, _ = trading_simulation(df, signal, initial_capital, trade_percent, max_trades_per_day, stop_loss)
        return {
            'strategy': signal,
            'trade_percent': trade_percent,
            'stop_loss': stop_loss,
            'final_capital': final_capital
        }

    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = []
        for trade_percent in trade_percent_values:
            for stop_loss in stop_loss_values:
                for signal in signal_columns:
                    futures.append(executor.submit(simulate_strategy, signal, trade_percent, stop_loss))

        for future in concurrent.futures.as_completed(futures):
            results.append(future.result())

    # Test combinations of signals
    for i in range(2, len(signal_columns) + 1):
        for combination in combinations(signal_columns, i):
            combined_signal_name = '+'.join(combination)
            df['combined_signal'] = df[list(combination)].sum(axis=1)
            final_capital, _ = trading_simulation(df, 'combined_signal', initial_capital, trade_percent,
                                                  max_trades_per_day, stop_loss)
            results.append({
                'strategy': combined_signal_name,
                'trade_percent': trade_percent,
                'final_capital': final_capital
            })

    results_df = pd.DataFrame(results).sort_values(by='final_capital', ascending=False)
    return results_df


