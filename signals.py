import pandas as pd

class Signals:

    def __init__(self, df):
        self.df = df
# VWAP Calculation
    def compute_vwap(self):
        self.df['cum_vol'] = self.df['volume'].cumsum()
        self.df['cum_vol_price'] = (self.df['volume'] * self.df['close']).cumsum()
        vwap = self.df['cum_vol_price'] / self.df['cum_vol']
        return vwap

    # DCA Calculation
    def compute_dca(self, dca_period):
        # For simplicity, we'll simulate DCA as buying the asset at regular intervals.
        # We'll take a period of 24 hours for this hourly data.
        self.df['dca'] = self.df['close'].rolling(window=dca_period).mean()
        return self.df['dca']


    # Generate VWAP signals
    def generate_vwap_signals(self):
        self.df['vwap_signal'] = 0
        self.df.loc[self.df['close'] < self.df['vwap'], 'vwap_signal'] = 1
        self.df.loc[self.df['close'] > self.df['vwap'], 'vwap_signal'] = -1
        return self.df


    # Generate DCA signals
    def generate_dca_signals(self):
        self.df['dca_signal'] = 0
        self.df.loc[self.df['close'] < self.df['dca'], 'dca_signal'] = 1
        return self.df


    def compute_macd(self, short_window=12, long_window=26, signal_window=9):
        """
        Compute the MACD (Moving Average Convergence Divergence) to use as a trading signal.
        """
        short_ema = self.df['close'].ewm(span=short_window, adjust=False).mean()
        long_ema = self.df['close'].ewm(span=long_window, adjust=False).mean()
        macd = short_ema - long_ema
        signal = macd.ewm(span=signal_window, adjust=False).mean()
        return macd, signal


    def compute_bollinger_bands(self, window=20, num_std=2):
        """
        Compute the Bollinger Bands.
        """
        rolling_mean = self.df['close'].rolling(window=window).mean()
        rolling_std = self.df['close'].rolling(window=window).std()
        upper_band = rolling_mean + (rolling_std * num_std)
        lower_band = rolling_mean - (rolling_std * num_std)
        return upper_band, lower_band


    def compute_rsi(self, window=14):
        """
        Compute the RSI (Relative Strength Index).
        """
        delta = self.df['close'].diff()
        gain = (delta.where(delta > 0, 0)).fillna(0)
        loss = (-delta.where(delta < 0, 0)).fillna(0)
        avg_gain = gain.rolling(window=window, min_periods=1).mean()
        avg_loss = loss.rolling(window=window, min_periods=1).mean()
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        return rsi


    def generate_macd_signals(self):
        """
        Generate trading signals based on MACD.
        """
        self.df['macd_signal'] = 0
        self.df.loc[self.df['macd'] > self.df['signal'], 'macd_signal'] = 1
        self.df.loc[self.df['macd'] < self.df['signal'], 'macd_signal'] = -1
        return self.df


    def generate_bollinger_signals(self):
        """
        Generate trading signals based on Bollinger Bands.
        """
        self.df['bollinger_signal'] = 0
        self.df.loc[self.df['close'] < self.df['lower_band'], 'bollinger_signal'] = 1
        self.df.loc[self.df['close'] > self.df['upper_band'], 'bollinger_signal'] = -1
        return self.df


    def generate_rsi_signals(self, oversold_threshold=30, overbought_threshold=70):
        """
        Generate trading signals based on RSI.
        """
        self.df['rsi_signal'] = 0
        self.df.loc[self.df['rsi'] < oversold_threshold, 'rsi_signal'] = 1
        self.df.loc[self.df['rsi'] > overbought_threshold, 'rsi_signal'] = -1
        return self.df


    def generate_combined_signals(self):
        self.df['combined_signal'] = 0
        # Require at least two concurrent signals for a combined buy/sell signal
        self.df.loc[((self.df['macd_signal'] + self.df['bollinger_signal'] + self.df['rsi_signal']) >= 2), 'combined_signal'] = 1
        self.df.loc[((self.df['macd_signal'] + self.df['bollinger_signal'] + self.df['rsi_signal']) <= -2), 'combined_signal'] = -1
        return self.df

    def generate_all_signals(self):
        self.df = self.generate_macd_signals(self.df)
        self.df = self.generate_bollinger_signals(self.df)
        self.df = self.generate_rsi_signals(self.df)
        self.df = self.generate_vwap_signals(self.df)
        self.df = self.generate_dca_signals(self.df)
        return self.df
