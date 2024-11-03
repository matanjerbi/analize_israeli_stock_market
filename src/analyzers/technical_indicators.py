import pandas as pd


class TechnicalIndicators:
    @staticmethod
    def RSI(close_prices, periods=14):
        """Calculate Relative Strength Index"""
        delta = close_prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=periods).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=periods).mean()
        rs = gain / loss
        return 100 - (100 / (1 + rs))

    @staticmethod
    def MACD(close_prices, fast=12, slow=26, signal=9):
        """Calculate MACD, Signal line, and MACD histogram"""
        exp1 = close_prices.ewm(span=fast, adjust=False).mean()
        exp2 = close_prices.ewm(span=slow, adjust=False).mean()
        macd = exp1 - exp2
        signal_line = macd.ewm(span=signal, adjust=False).mean()
        histogram = macd - signal_line
        return macd, signal_line, histogram

    @staticmethod
    def BBANDS(close_prices, periods=20, num_std=2):
        """Calculate Bollinger Bands"""
        middle_band = close_prices.rolling(window=periods).mean()
        std_dev = close_prices.rolling(window=periods).std()
        upper_band = middle_band + (std_dev * num_std)
        lower_band = middle_band - (std_dev * num_std)
        return upper_band, middle_band, lower_band

    @staticmethod
    def ATR(high, low, close, periods=14):
        """Calculate Average True Range"""
        tr1 = high - low
        tr2 = abs(high - close.shift())
        tr3 = abs(low - close.shift())
        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        return tr.rolling(window=periods).mean()

    @staticmethod
    def ADX(high, low, close, periods=14):
        """Calculate Average Directional Index"""
        tr = TechnicalIndicators.ATR(high, low, close, periods=1)
        up_move = high - high.shift()
        down_move = low.shift() - low

        pos_dm = up_move.where((up_move > down_move) & (up_move > 0), 0)
        neg_dm = down_move.where((down_move > up_move) & (down_move > 0), 0)

        pos_di = 100 * (pos_dm.rolling(periods).mean() / tr.rolling(periods).mean())
        neg_di = 100 * (neg_dm.rolling(periods).mean() / tr.rolling(periods).mean())

        dx = 100 * abs(pos_di - neg_di) / (pos_di + neg_di)
        adx = dx.rolling(periods).mean()
        return adx

    @staticmethod
    def OBV(close, volume):
        """Calculate On Balance Volume"""
        obv = volume.copy()
        obv[close < close.shift()] *= -1
        return obv.cumsum()

    @staticmethod
    def AROON(high, low, periods=25):
        """Calculate Aroon Indicator"""
        high_periods = pd.Series(range(len(high))).rolling(periods + 1, min_periods=periods + 1).apply(
            lambda x: x.argmax())
        low_periods = pd.Series(range(len(low))).rolling(periods + 1, min_periods=periods + 1).apply(
            lambda x: x.argmin())
        aroon_up = ((periods - high_periods) / periods) * 100
        aroon_down = ((periods - low_periods) / periods) * 100
        return aroon_up, aroon_down

    @staticmethod
    def RSI(close_prices, periods=14):
        """Calculate Relative Strength Index with performance optimization"""
        import numpy as np

        delta = np.diff(close_prices)
        gains = np.where(delta > 0, delta, 0)
        losses = np.where(delta < 0, -delta, 0)

        # Using exponential moving average for more accurate RSI
        alpha = 1 / periods
        gains_ema = pd.Series(gains).ewm(alpha=alpha, adjust=False).mean()
        losses_ema = pd.Series(losses).ewm(alpha=alpha, adjust=False).mean()

        rs = gains_ema / losses_ema
        rsi = 100 - (100 / (1 + rs))
        return pd.Series(rsi, index=close_prices.index[1:])

    # הוספת מדדים חדשים
    @staticmethod
    def CMF(high, low, close, volume, periods=20):
        """Calculate Chaikin Money Flow"""
        mfm = ((close - low) - (high - close)) / (high - low)
        mfv = mfm * volume
        return mfv.rolling(window=periods).sum() / volume.rolling(window=periods).sum()

    @staticmethod
    def ROC(close_prices, periods=12):
        """Calculate Rate of Change"""
        return (close_prices - close_prices.shift(periods)) / close_prices.shift(periods) * 100
