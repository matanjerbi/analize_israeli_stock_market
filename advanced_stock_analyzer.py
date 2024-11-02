import yfinance as yf
import numpy as np


from technical_indicators import TechnicalIndicators


class AdvancedStockAnalyzer:
    def __init__(self, symbol, market_index="^TA125.TA", risk_free_rate=0.04):
        """
        מאתחל את המנתח עם הפרמטרים הבסיסיים

        Parameters:
        -----------
        symbol : str
            סימול המניה
        market_index : str
            סימול מדד הייחוס
        risk_free_rate : float
            ריבית חסרת סיכון שנתית
        """
        if not isinstance(risk_free_rate, (int, float)) or risk_free_rate < 0:
            raise ValueError("risk_free_rate חייב להיות מספר חיובי")

        self.symbol = symbol
        self.market_index = market_index
        self.risk_free_rate = risk_free_rate
        self.stock = yf.Ticker(symbol)
        self.market = yf.Ticker(market_index)

    def fetch_data(self, period="1y"):
        """מושך את כל הנתונים הנדרשים לניתוח"""
        try:
            # משיכת נתוני המניה והמדד
            self.hist = self.stock.history(period=period)
            self.market_hist = self.market.history(period=period)

            if len(self.hist) == 0:
                raise ValueError(f"לא נמצאו נתונים עבור המניה {self.symbol}")
            if len(self.market_hist) == 0:
                raise ValueError(f"לא נמצאו נתונים עבור המדד {self.market_index}")

            # יישור התאריכים
            common_dates = self.hist.index.intersection(self.market_hist.index)
            if len(common_dates) == 0:
                raise ValueError("אין תאריכים משותפים בין המניה למדד")

            self.hist = self.hist.loc[common_dates]
            self.market_hist = self.market_hist.loc[common_dates]

            # חישוב תשואות
            self.hist['Returns'] = self.hist['Close'].pct_change()
            self.market_hist['Returns'] = self.market_hist['Close'].pct_change()

            try:
                self.info = self.stock.info
            except:
                self.info = {}
                print("לא ניתן למשוך מידע בסיסי על המניה")

        except Exception as e:
            raise Exception(f"שגיאה במשיכת נתונים: {str(e)}")

    def calculate_technical_indicators(self):
        """מחשב מדדים טכניים מתקדמים"""
        try:
            close_prices = self.hist['Close']
            high_prices = self.hist['High']
            low_prices = self.hist['Low']
            volume = self.hist['Volume']

            # מדדי מומנטום
            self.hist['RSI'] = TechnicalIndicators.RSI(close_prices)
            self.hist['MACD'], self.hist['MACD_Signal'], self.hist['MACD_Hist'] = \
                TechnicalIndicators.MACD(close_prices)

            # מדדי תנודתיות
            self.hist['ATR'] = TechnicalIndicators.ATR(high_prices, low_prices, close_prices)
            self.hist['BBANDS_Upper'], self.hist['BBANDS_Middle'], self.hist['BBANDS_Lower'] = \
                TechnicalIndicators.BBANDS(close_prices)

            # מדדי מגמה
            self.hist['ADX'] = TechnicalIndicators.ADX(high_prices, low_prices, close_prices)
            self.hist['AROON_Up'], self.hist['AROON_Down'] = \
                TechnicalIndicators.AROON(high_prices, low_prices)

            # מדדי נפח
            self.hist['OBV'] = TechnicalIndicators.OBV(close_prices, volume)

        except Exception as e:
            print(f"שגיאה בחישוב אינדיקטורים טכניים: {str(e)}")
            # מילוי ערכי ברירת מחדל
            for col in ['RSI', 'MACD', 'MACD_Signal', 'MACD_Hist', 'ATR',
                        'BBANDS_Upper', 'BBANDS_Middle', 'BBANDS_Lower',
                        'ADX', 'AROON_Up', 'AROON_Down', 'OBV']:
                self.hist[col] = np.nan

    def calculate_risk_metrics(self):
        """מחשב מדדי סיכון מתקדמים"""
        try:
            # מסנכרן את התאריכים בין המניה למדד
            common_dates = self.hist.index.intersection(self.market_hist.index)
            stock_returns = self.hist.loc[common_dates, 'Returns']
            market_returns = self.market_hist.loc[common_dates, 'Returns']

            # בטא
            if len(stock_returns.dropna()) < 2 or len(market_returns.dropna()) < 2:
                raise ValueError("אין מספיק נתונים לחישוב מדדי סיכון")

            covariance = np.cov(stock_returns.dropna(),
                                market_returns.dropna())[0][1]
            market_variance = np.var(market_returns.dropna())
            self.beta = covariance / market_variance if market_variance != 0 else np.nan

            # אלפא
            risk_free_daily = (1 + self.risk_free_rate) ** (1 / 252) - 1
            market_return = market_returns.mean()
            stock_return = stock_returns.mean()
            self.alpha = stock_return - (risk_free_daily + self.beta * (market_return - risk_free_daily))

            # יחס שארפ
            excess_returns = stock_returns - risk_free_daily
            self.sharpe = np.sqrt(
                252) * excess_returns.mean() / excess_returns.std() if excess_returns.std() != 0 else np.nan

            # מדד טריינור
            if not np.isnan(self.beta) and self.beta != 0:
                self.treynor = np.sqrt(252) * (stock_return - risk_free_daily) / self.beta
            else:
                self.treynor = np.nan

            # Value at Risk (VaR)
            self.var_95 = np.percentile(stock_returns.dropna(), 5)

            # Maximum Drawdown
            cum_returns = (1 + stock_returns).cumprod()
            rolling_max = cum_returns.expanding().max()
            drawdowns = cum_returns / rolling_max - 1
            self.max_drawdown = drawdowns.min()

        except Exception as e:
            print(f"שגיאה בחישוב מדדי סיכון: {str(e)}")
            self.beta = np.nan
            self.alpha = np.nan
            self.sharpe = np.nan
            self.treynor = np.nan
            self.var_95 = np.nan
            self.max_drawdown = np.nan

    def calculate_fundamental_metrics(self):
        """מחשב מדדים פונדמנטליים"""
        try:
            # מכפילים
            self.pe_ratio = self.info.get('trailingPE', np.nan)
            self.pb_ratio = self.info.get('priceToBook', np.nan)
            self.ps_ratio = self.info.get('priceToSalesTrailing12Months', np.nan)

            # צמיחה
            self.revenue_growth = self.info.get('revenueGrowth', np.nan)
            self.earnings_growth = self.info.get('earningsGrowth', np.nan)

            # רווחיות
            self.profit_margins = self.info.get('profitMargins', np.nan)
            self.operating_margins = self.info.get('operatingMargins', np.nan)

            # יציבות פיננסית
            self.debt_to_equity = self.info.get('debtToEquity', np.nan)
            self.current_ratio = self.info.get('currentRatio', np.nan)

        except Exception as e:
            print(f"שגיאה בחישוב מדדים פונדמנטליים: {str(e)}")
            self.pe_ratio = np.nan
            self.pb_ratio = np.nan
            self.ps_ratio = np.nan
            self.revenue_growth = np.nan
            self.earnings_growth = np.nan
            self.profit_margins = np.nan
            self.operating_margins = np.nan
            self.debt_to_equity = np.nan
            self.current_ratio = np.nan

    def analyze_market_sentiment(self):
        """מנתח סנטימנט שוק"""
        try:
            # מדדי סנטימנט טכניים
            self.technical_sentiment = {
                'oversold': self.hist['RSI'].iloc[-1] < 30 if not np.isnan(self.hist['RSI'].iloc[-1]) else False,
                'overbought': self.hist['RSI'].iloc[-1] > 70 if not np.isnan(self.hist['RSI'].iloc[-1]) else False,
                'golden_cross': (self.hist['BBANDS_Middle'].iloc[-1] >
                                 self.hist['BBANDS_Middle'].iloc[-20]) if not np.isnan(
                    self.hist['BBANDS_Middle'].iloc[-1]) else False,
                'death_cross': (self.hist['BBANDS_Middle'].iloc[-1] <
                                self.hist['BBANDS_Middle'].iloc[-20]) if not np.isnan(
                    self.hist['BBANDS_Middle'].iloc[-1]) else False,
                'volume_trend': (self.hist['Volume'].tail(10).mean() /
                                 self.hist['Volume'].tail(30).mean() - 1) if not self.hist['Volume'].empty else 0
            }

            # עוצמת מגמה
            self.trend_strength = {
                'adx_strength': float(self.hist['ADX'].iloc[-1]) if not np.isnan(self.hist['ADX'].iloc[-1]) else 0,
                'aroon_trend': float(self.hist['AROON_Up'].iloc[-1] - self.hist['AROON_Down'].iloc[-1]) if not np.isnan(
                    self.hist['AROON_Up'].iloc[-1]) else 0,
                'macd_trend': float(self.hist['MACD_Hist'].iloc[-1]) if not np.isnan(
                    self.hist['MACD_Hist'].iloc[-1]) else 0
            }

        except Exception as e:
            print(f"שגיאה בניתוח סנטימנט: {str(e)}")
            self.technical_sentiment = {
                'oversold': False,
                'overbought': False,
                'golden_cross': False,
                'death_cross': False,
                'volume_trend': 0
            }
            self.trend_strength = {
                'adx_strength': 0,
                'aroon_trend': 0,
                'macd_trend': 0
            }


    def calculate_final_score(self):
        """מחשב ציון סופי ומגבש המלצה"""
        try:
            scores = {}
            reasons = []

            # === ציון טכני (30%) ===
            technical_score = 0

            # RSI (5%)
            rsi = self.hist['RSI'].iloc[-1]
            if not np.isnan(rsi):
                if 40 <= rsi <= 60:
                    technical_score += 5
                    reasons.append(f"RSI באזור מאוזן ({rsi:.1f})")
                elif 30 <= rsi <= 70:
                    technical_score += 3
                else:
                    technical_score += 1

            # MACD (10%)
            if not np.isnan(self.hist['MACD'].iloc[-1]) and not np.isnan(self.hist['MACD_Signal'].iloc[-1]):
                if self.hist['MACD'].iloc[-1] > self.hist['MACD_Signal'].iloc[-1]:
                    technical_score += 10
                    reasons.append("איתות MACD חיובי")

            # Bollinger Bands (5%)
            last_close = self.hist['Close'].iloc[-1]
            if (not np.isnan(self.hist['BBANDS_Lower'].iloc[-1]) and
                    not np.isnan(self.hist['BBANDS_Upper'].iloc[-1])):
                if (self.hist['BBANDS_Lower'].iloc[-1] < last_close <
                        self.hist['BBANDS_Upper'].iloc[-1]):
                    technical_score += 5
                    reasons.append("מחיר בתוך רצועות Bollinger")

            # מגמה (10%)
            if not np.isnan(self.trend_strength['adx_strength']):
                if self.trend_strength['adx_strength'] > 25:
                    if self.trend_strength['aroon_trend'] > 0:
                        technical_score += 10
                        reasons.append("מגמה חיובית חזקה")
                    else:
                        technical_score -= 10
                        reasons.append("מגמה שלילית חזקה")

            scores['technical'] = technical_score / 30

            # === ציון סיכון (25%) ===
            risk_score = 0

            # בטא (10%)
            if not np.isnan(self.beta):
                if 0.7 <= self.beta <= 1.3:
                    risk_score += 10
                    reasons.append(f"בטא מאוזנת ({self.beta:.2f})")
                elif self.beta < 0.7:
                    risk_score += 5
                    reasons.append("סיכון נמוך יחסית לשוק")

            # שארפ (10%)
            if not np.isnan(self.sharpe):
                if self.sharpe > 1:
                    risk_score += 10
                    reasons.append(f"יחס שארפ חיובי ({self.sharpe:.2f})")
                elif self.sharpe > 0:
                    risk_score += 5

            # Maximum Drawdown (5%)
            if not np.isnan(self.max_drawdown):
                if self.max_drawdown > -0.2:
                    risk_score += 5
                    reasons.append("ירידה מקסימלית מתונה")

            scores['risk'] = risk_score / 25

            # === ציון פונדמנטלי (25%) ===
            fundamental_score = 0

            # מכפילים (10%)
            if not np.isnan(self.pe_ratio) and 5 < self.pe_ratio < 25:
                fundamental_score += 5
                reasons.append(f"מכפיל רווח סביר ({self.pe_ratio:.1f})")
            if not np.isnan(self.pb_ratio) and 0.5 < self.pb_ratio < 3:
                fundamental_score += 5
                reasons.append(f"מכפיל הון סביר ({self.pb_ratio:.1f})")

            # צמיחה (10%)
            if not np.isnan(self.revenue_growth) and self.revenue_growth > 0.1:
                fundamental_score += 5
                reasons.append(f"צמיחה בהכנסות ({self.revenue_growth * 100:.1f}%)")
            if not np.isnan(self.earnings_growth) and self.earnings_growth > 0.1:
                fundamental_score += 5
                reasons.append(f"צמיחה ברווחים ({self.earnings_growth * 100:.1f}%)")

            # יציבות פיננסית (5%)
            if not np.isnan(self.current_ratio) and self.current_ratio > 1.5:
                fundamental_score += 5
                reasons.append("יציבות פיננסית טובה")

            scores['fundamental'] = fundamental_score / 25

            # === ציון סנטימנט (20%) ===
            sentiment_score = 0

            # מדדי סנטימנט טכניים (10%)
            if not self.technical_sentiment['oversold'] and \
                    not self.technical_sentiment['overbought']:
                sentiment_score += 5
            if self.technical_sentiment['volume_trend'] > 0.1:
                sentiment_score += 5
                reasons.append("עלייה בנפח המסחר")

            # עוצמת מגמה (10%)
            if self.trend_strength['adx_strength'] > 25 and \
                    self.trend_strength['aroon_trend'] > 50:
                sentiment_score += 10
                reasons.append("מגמה חזקה וחיובית")

            scores['sentiment'] = sentiment_score / 20

            # === חישוב ציון סופי ===
            self.final_score = (
                    scores['technical'] * 0.3 +
                    scores['risk'] * 0.25 +
                    scores['fundamental'] * 0.25 +
                    scores['sentiment'] * 0.2
            )

            # === קביעת המלצה ===
            if self.final_score > 0.7:
                recommendation = "קנייה חזקה"
            elif self.final_score > 0.6:
                recommendation = "קנייה"
            elif self.final_score < 0.3:
                recommendation = "מכירה"
            elif self.final_score < 0.4:
                recommendation = "החזק"
            else:
                recommendation = "מעקב"

            return {
                'המלצה': recommendation,
                'ציון_סופי': self.final_score,
                'ציונים_חלקיים': scores,
                'סיבות': reasons,
                'מדדים_טכניים': {
                    'RSI': float(self.hist['RSI'].iloc[-1]) if not np.isnan(self.hist['RSI'].iloc[-1]) else None,
                    'MACD': float(self.hist['MACD'].iloc[-1]) if not np.isnan(self.hist['MACD'].iloc[-1]) else None,
                    'ATR': float(self.hist['ATR'].iloc[-1]) if not np.isnan(self.hist['ATR'].iloc[-1]) else None
                },
                'מדדי_סיכון': {
                    'בטא': float(self.beta) if not np.isnan(self.beta) else None,
                    'שארפ': float(self.sharpe) if not np.isnan(self.sharpe) else None,
                    'דרודאון_מקסימלי': float(self.max_drawdown) if not np.isnan(self.max_drawdown) else None
                },
                'מדדים_פונדמנטליים': {
                    'מכפיל_רווח': float(self.pe_ratio) if not np.isnan(self.pe_ratio) else None,
                    'מכפיל_הון': float(self.pb_ratio) if not np.isnan(self.pb_ratio) else None,
                    'צמיחת_הכנסות': float(self.revenue_growth) if not np.isnan(self.revenue_growth) else None
                }
            }

        except Exception as e:
            print(f"שגיאה בחישוב ציון סופי: {str(e)}")
            return {
                'המלצה': "לא ניתן לחשב",
                'ציון_סופי': np.nan,
                'ציונים_חלקיים': {},
                'סיבות': ["שגיאה בחישוב הציון הסופי"],
                'מדדים_טכניים': {},
                'מדדי_סיכון': {},
                'מדדים_פונדמנטליים': {}
            }

    def run_analysis(self, period="1y"):
        """מריץ את כל הניתוח"""
        self.fetch_data(period)
        self.calculate_technical_indicators()
        self.calculate_risk_metrics()
        self.calculate_fundamental_metrics()
        self.analyze_market_sentiment()
        return self.calculate_final_score()
