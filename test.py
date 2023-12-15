import pandas as pd
from ta.volatility import KeltnerChannel
from ta.trend import MACD
from assistant_methods import get_historical_bars


class KeltnerMACDStrategy():
    def __init__(self):
        self.data = get_historical_bars(symbols='MMM', timeframe='1min', start='2023-01-01')
        self.high = pd.Series(self.data.High)
        self.close = pd.Series(self.data.Close)
        self.low = pd.Series(self.data.Low)

        self.keltner_channel = KeltnerChannel(high=self.high, low=self.low,
                                              close=self.close, window=20,
                                              window_atr=10, fillna=False)

        self.macd = MACD(self.close, window_slow=26, window_fast=12,
                         window_sign=9, fillna=False)

    def next(self, i):
        # Check conditions at the i-th point in time
        if self.close.iloc[i] > self.keltner_channel.keltner_channel_hband().iloc[i] and \
                self.macd.macd_diff().iloc[i] > 0:
            return 'buy'
        elif self.close.iloc[i] < self.keltner_channel.keltner_channel_lband().iloc[i] and \
                self.macd.macd_diff().iloc[i] < 0:
            return 'sell'
        else:
            return 'hold'

    def decisions(self):
        decisions = []
        for i in range(len(self.close)):
            decision = self.next(i)
            decisions.append(decision)
        return decisions


# Initialize and run backtest
strategy = KeltnerMACDStrategy()
backtest_results = strategy.decisions()
print(backtest_results)
