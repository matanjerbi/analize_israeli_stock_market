import yfinance as yf
import numpy as np
import pandas as pd
from dataclasses import dataclass
from typing import Dict, List, Optional
import asyncio
import aiohttp
import json
import logging
from pathlib import Path
from datetime import datetime, timedelta
from .technical_indicators import TechnicalIndicators


@dataclass
class StockAlert:
    """מחלקה לייצוג התראה"""
    symbol: str
    condition: str
    target_value: float
    current_value: float
    alert_type: str
    created_at: datetime
    triggered: bool = False


@dataclass
class TechnicalPattern:
    """מחלקה לייצוג תבנית טכנית"""
    pattern_type: str
    start_date: datetime
    end_date: datetime
    confidence: float
    description: str


class EnhancedStockAnalyzer:
    def __init__(self, symbol: str, market_index: str = "^TA125.TA", risk_free_rate: float = 0.04):
        """אתחול המנתח"""
        self.symbol = symbol
        self.market_index = market_index
        self.risk_free_rate = risk_free_rate

        # הגדרת נתיבים
        self.data_dir = Path("data")
        self.data_dir.mkdir(exist_ok=True)

        # הגדרת logging
        self.setup_logging()

        # מערכת Cache
        self.cache = {}
        self.cache_expiry = {}

        # מערכת התראות
        self.alerts: List[StockAlert] = []

        # אתחול מבני נתונים
        self.initialize_data_structures()

    def setup_logging(self):
        """הגדרת מערכת הלוגים"""
        logging.basicConfig(
            filename=f'logs/stock_analyzer_{datetime.now().strftime("%Y%m%d")}.log',
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(f"StockAnalyzer_{self.symbol}")

    def initialize_data_structures(self):
        """אתחול כל מבני הנתונים"""
        self.technical_patterns: List[TechnicalPattern] = []
        self.support_resistance_levels = {"support": [], "resistance": []}
        self.sector_comparison = {}
        self.price_predictions = {}

        # נתונים היסטוריים
        self.hist = None
        self.market_hist = None
        self.sector_data = None

    async def fetch_all_data(self):
        """משיכת כל הנתונים הנדרשים"""
        tasks = [
            self.fetch_stock_data(),
            self.fetch_market_data(),
            self.fetch_sector_data(),
            self.fetch_financial_statements()
        ]
        await asyncio.gather(*tasks)

    async def fetch_stock_data(self):
        """משיכת נתוני המניה"""
        cache_key = f"{self.symbol}_data"
        if self.is_cache_valid(cache_key):
            self.logger.info(f"Using cached data for {self.symbol}")
            return self.cache[cache_key]

        try:
            stock = yf.Ticker(self.symbol)
            self.hist = stock.history(period="2y")
            self.cache[cache_key] = self.hist
            self.update_cache_expiry(cache_key)
            self.logger.info(f"Successfully fetched data for {self.symbol}")
        except Exception as e:
            self.logger.error(f"Error fetching stock data: {str(e)}")
            raise

    async def fetch_market_data(self):
        """משיכת נתוני השוק"""
        try:
            market = yf.Ticker(self.market_index)
            self.market_hist = market.history(period="2y")
        except Exception as e:
            self.logger.error(f"Error fetching market data: {str(e)}")
            raise

    async def fetch_sector_data(self):
        """משיכת נתוני הסקטור"""
        try:
            stock = yf.Ticker(self.symbol)
            sector = stock.info.get('sector')
            if sector:
                # TODO: להוסיף לוגיקה למשיכת נתוני סקטור
                pass
        except Exception as e:
            self.logger.error(f"Error fetching sector data: {str(e)}")

    async def fetch_financial_statements(self):
        """משיכת דוחות כספיים"""
        try:
            stock = yf.Ticker(self.symbol)
            # TODO: להוסיף ניתוח דוחות כספיים
            pass
        except Exception as e:
            self.logger.error(f"Error fetching financial statements: {str(e)}")

    def identify_technical_patterns(self):
        """זיהוי תבניות טכניות"""
        patterns = []
        if self.hist is None:
            return patterns

        try:
            # Double Bottom
            double_bottom = self.find_double_bottom()
            if double_bottom:
                patterns.append(double_bottom)

            # Head and Shoulders
            head_shoulders = self.find_head_shoulders()
            if head_shoulders:
                patterns.append(head_shoulders)

            # Breakouts
            breakouts = self.find_breakouts()
            if breakouts:
                patterns.extend(breakouts)

            self.technical_patterns = patterns
        except Exception as e:
            self.logger.error(f"Error identifying patterns: {str(e)}")

        return patterns

    def find_double_bottom(self) -> Optional[TechnicalPattern]:
        """זיהוי תבנית Double Bottom"""
        if self.hist is None or len(self.hist) < 40:
            return None

        try:
            prices = self.hist['Low'].values
            for i in range(20, len(prices) - 20):
                # בדיקת מינימום מקומי
                if (prices[i] < prices[i - 1] and prices[i] < prices[i + 1] and
                        prices[i] < prices[i - 10:i].min() and
                        prices[i] < prices[i + 1:i + 11].min()):

                    # חיפוש מינימום שני דומה
                    for j in range(i + 10, len(prices) - 10):
                        if (abs(prices[i] - prices[j]) / prices[i] < 0.02 and
                                prices[j] < prices[j - 1] and prices[j] < prices[j + 1]):
                            return TechnicalPattern(
                                pattern_type="Double Bottom",
                                start_date=self.hist.index[i],
                                end_date=self.hist.index[j],
                                confidence=0.8,
                                description="נמצאה תבנית Double Bottom"
                            )
        except Exception as e:
            self.logger.error(f"Error in double bottom detection: {str(e)}")

        return None

    def find_head_shoulders(self) -> Optional[TechnicalPattern]:
        """זיהוי תבנית Head and Shoulders"""
        # TODO: להוסיף לוגיקה לזיהוי תבנית
        return None

    def find_breakouts(self) -> List[TechnicalPattern]:
        """זיהוי פריצות"""
        breakouts = []
        if self.hist is None:
            return breakouts

        try:
            closes = self.hist['Close']
            volumes = self.hist['Volume']

            # חישוב ממוצע נע
            ma20 = closes.rolling(window=20).mean()
            vol_ma20 = volumes.rolling(window=20).mean()

            # חיפוש פריצות
            for i in range(20, len(closes)):
                if (closes[i] > ma20[i] * 1.02 and  # פריצה של 2% מעל הממוצע
                        volumes[i] > vol_ma20[i] * 1.5):  # נפח מסחר גבוה

                    breakouts.append(TechnicalPattern(
                        pattern_type="Breakout",
                        start_date=closes.index[i - 1],
                        end_date=closes.index[i],
                        confidence=0.7,
                        description="פריצה כלפי מעלה בנפח מסחר גבוה"
                    ))
        except Exception as e:
            self.logger.error(f"Error finding breakouts: {str(e)}")

        return breakouts

    def find_support_resistance(self):
        """מציאת רמות תמיכה והתנגדות"""
        if self.hist is None:
            return

        try:
            prices = self.hist['Close'].values
            window = 20

            for i in range(window, len(prices)):
                window_prices = prices[i - window:i]
                local_min = np.min(window_prices)
                local_max = np.max(window_prices)

                # בדיקת רמות תמיכה
                if prices[i] == local_min:
                    self.support_resistance_levels["support"].append({
                        "price": prices[i],
                        "date": self.hist.index[i]
                    })

                # בדיקת רמות התנגדות
                if prices[i] == local_max:
                    self.support_resistance_levels["resistance"].append({
                        "price": prices[i],
                        "date": self.hist.index[i]
                    })
        except Exception as e:
            self.logger.error(f"Error finding support/resistance: {str(e)}")

    def predict_prices(self):
        """חיזוי מחירים עתידיים"""
        if self.hist is None:
            return

        try:
            # חישוב ממוצעים נעים
            self.hist['MA20'] = self.hist['Close'].rolling(window=20).mean()
            self.hist['MA50'] = self.hist['Close'].rolling(window=50).mean()

            # חישוב תנודתיות
            self.hist['Volatility'] = self.hist['Close'].rolling(window=20).std()

            # חיזוי בסיסי למחר
            last_price = self.hist['Close'].iloc[-1]
            volatility = self.hist['Volatility'].iloc[-1]

            self.price_predictions = {
                "next_day": {
                    "lower": last_price - volatility,
                    "prediction": last_price,
                    "upper": last_price + volatility
                }
            }
        except Exception as e:
            self.logger.error(f"Error predicting prices: {str(e)}")

    def add_price_alert(self, target_price: float, condition: str = "above"):
        """הוספת התראת מחיר"""
        if condition not in ["above", "below"]:
            raise ValueError("Condition must be 'above' or 'below'")

        alert = StockAlert(
            symbol=self.symbol,
            condition=condition,
            target_value=target_price,
            current_value=self.hist['Close'].iloc[-1] if self.hist is not None else 0,
            alert_type="price",
            created_at=datetime.now()
        )

        self.alerts.append(alert)
        self.logger.info(f"Added price alert for {self.symbol}: {condition} {target_price}")

    def check_alerts(self):
        """בדיקת התראות פעילות"""
        if self.hist is None:
            return []

        current_price = self.hist['Close'].iloc[-1]
        triggered_alerts = []

        for alert in self.alerts:
            if alert.triggered:
                continue

            if alert.alert_type == "price":
                if (alert.condition == "above" and current_price > alert.target_value) or \
                        (alert.condition == "below" and current_price < alert.target_value):
                    alert.triggered = True
                    triggered_alerts.append(alert)

        return triggered_alerts

    def is_cache_valid(self, key: str) -> bool:
        """בדיקת תקפות המטמון"""
        if key not in self.cache_expiry:
            return False
        return datetime.now() < self.cache_expiry[key]

    def update_cache_expiry(self, key: str, hours: int = 24):
        """עדכון תפוגת המטמון"""
        self.cache_expiry[key] = datetime.now() + timedelta(hours=hours)

    def export_to_excel(self, filename: str):
        """ייצוא הניתוח לאקסל"""
        try:
            self.logger.info(f"Starting export to {filename}")

            if self.hist is None:
                raise ValueError("No historical data available for export")

            # יצירת DataFrames לייצוא
            export_data = {}

            # נתונים היסטוריים - הסרת אזורי זמן
            hist_data = self.hist.copy()
            hist_data.index = hist_data.index.tz_localize(None)  # הסרת אזור זמן
            export_data['Historical Data'] = hist_data
            self.logger.info("Historical data prepared")

            # אינדיקטורים טכניים
            tech_columns = ['RSI', 'MACD', 'MACD_Signal', 'ATR']
            tech_data = hist_data[[col for col in tech_columns if col in hist_data.columns]].copy()
            export_data['Technical Indicators'] = tech_data
            self.logger.info("Technical indicators prepared")

            # סיכום והמלצות
            results = self.calculate_final_score()
            summary_data = pd.DataFrame({
                'Metric': ['המלצה', 'ציון סופי'] +
                          [f'ציון {k}' for k in results['ציונים_חלקיים'].keys()] +
                          ['סיבה ' + str(i + 1) for i in range(len(results['סיבות']))],
                'Value': [results['המלצה'],
                          f"{results['ציון_סופי']:.2f}"] +
                         [f"{v:.2f}" for v in results['ציונים_חלקיים'].values()] +
                         results['סיבות']
            })
            export_data['Summary'] = summary_data
            self.logger.info("Summary data prepared")

            # ייצוא כל הדפים
            with pd.ExcelWriter(filename, engine='openpyxl') as writer:
                for sheet_name, data in export_data.items():
                    self.logger.info(f"Exporting sheet: {sheet_name}")
                    data.to_excel(writer, sheet_name=sheet_name)
                    self.logger.info(f"Successfully exported {sheet_name}")

            return True

        except Exception as e:
            self.logger.error(f"Error in export_to_excel: {str(e)}")
            raise ValueError(f"שגיאה בייצוא לאקסל: {str(e)}")


    def save_analysis(self):
        """שמירת תוצאות הניתוח"""
        analysis_data = {
            "timestamp": datetime.now().isoformat(),
            "symbol": self.symbol,
            "technical_patterns": [
                {
                    "type": p.pattern_type,
                    "start_date": p.start_date.isoformat(),
                    "end_date": p.end_date.isoformat(),
                    "confidence": p.confidence,
                    "description": p.description
                }
                for p in self.technical_patterns
            ],
            "support_resistance": self.support_resistance_levels,
            "predictions": self.price_predictions
        }

        filename = self.data_dir / f"analysis_{self.symbol}_{datetime.now().strftime('%Y%m%d')}.json"
        with open(filename, 'w') as f:
            json.dump(analysis_data, f, indent=4)

        self.logger.info(f"Analysis saved to {filename}")

    def load_analysis(self, filename: str):
        """טעינת ניתוח קודם"""
        try:
            with open(filename, 'r') as f:
                data = json.load(f)

            self.technical_patterns = [
                TechnicalPattern(
                    pattern_type=p["type"],
                    start_date=datetime.fromisoformat(p["start_date"]),
                    end_date=datetime.fromisoformat(p["end_date"]),
                    confidence=p["confidence"],
                    description=p["description"]
                )
                for p in data["technical_patterns"]
            ]

            self.support_resistance_levels = data["support_resistance"]
            self.price_predictions = data["predictions"]

            self.logger.info(f"Successfully loaded analysis from {filename}")

        except Exception as e:
            self.logger.error(f"Error loading analysis: {str(e)}")
            raise

    def analyze_sentiment(self):
        """ניתוח סנטימנט בסיסי"""
        if self.hist is None:
            return {}

        try:
            # חישוב מדדי מומנטום
            rsi = TechnicalIndicators.RSI(self.hist['Close'])
            macd, signal, _ = TechnicalIndicators.MACD(self.hist['Close'])

            # ניתוח נפח מסחר
            volume_trend = self.hist['Volume'].tail(10).mean() / self.hist['Volume'].tail(30).mean() - 1

            # ניתוח מגמה
            price_trend = (self.hist['Close'].iloc[-1] / self.hist['Close'].iloc[-20]) - 1

            sentiment = {
                'rsi_signal': 'oversold' if rsi.iloc[-1] < 30 else 'overbought' if rsi.iloc[-1] > 70 else 'neutral',
                'macd_signal': 'bullish' if macd.iloc[-1] > signal.iloc[-1] else 'bearish',
                'volume_signal': 'high' if volume_trend > 0.1 else 'low' if volume_trend < -0.1 else 'normal',
                'trend_signal': 'up' if price_trend > 0.02 else 'down' if price_trend < -0.02 else 'sideways'
            }

            return sentiment

        except Exception as e:
            self.logger.error(f"Error analyzing sentiment: {str(e)}")
            return {}

    def calculate_risk_metrics(self):
        """חישוב מדדי סיכון"""
        if self.hist is None or self.market_hist is None:
            return {}

        try:
            # חישוב תשואות
            stock_returns = self.hist['Close'].pct_change().dropna()
            market_returns = self.market_hist['Close'].pct_change().dropna()

            # חישוב בטא
            covariance = stock_returns.cov(market_returns)
            market_variance = market_returns.var()
            beta = covariance / market_variance

            # חישוב שארפ
            excess_returns = stock_returns - self.risk_free_rate / 252
            sharpe = np.sqrt(252) * excess_returns.mean() / excess_returns.std()

            # חישוב מקסימום דרודאון
            cum_returns = (1 + stock_returns).cumprod()
            rolling_max = cum_returns.expanding().max()
            drawdowns = cum_returns / rolling_max - 1
            max_drawdown = drawdowns.min()

            # חישוב Value at Risk
            var_95 = np.percentile(stock_returns, 5)

            risk_metrics = {
                'beta': beta,
                'sharpe': sharpe,
                'max_drawdown': max_drawdown,
                'var_95': var_95
            }

            return risk_metrics

        except Exception as e:
            self.logger.error(f"Error calculating risk metrics: {str(e)}")
            return {}

    def calculate_technical_indicators(self):
        """מחשב מדדים טכניים"""
        if self.hist is None:
            raise ValueError("No historical data available")

        try:
            close_prices = self.hist['Close']
            high_prices = self.hist['High']
            low_prices = self.hist['Low']
            volume = self.hist['Volume']

            # מדדי מומנטום
            self.hist['RSI'] = TechnicalIndicators.RSI(close_prices)
            macd, signal, hist = TechnicalIndicators.MACD(close_prices)
            self.hist['MACD'] = macd
            self.hist['MACD_Signal'] = signal
            self.hist['MACD_Hist'] = hist

            # מדדי תנודתיות
            self.hist['ATR'] = TechnicalIndicators.ATR(high_prices, low_prices, close_prices)
            upper, middle, lower = TechnicalIndicators.BBANDS(close_prices)
            self.hist['BBANDS_Upper'] = upper
            self.hist['BBANDS_Middle'] = middle
            self.hist['BBANDS_Lower'] = lower

            # מדדי מגמה
            self.hist['ADX'] = TechnicalIndicators.ADX(high_prices, low_prices, close_prices)
            aroon_up, aroon_down = TechnicalIndicators.AROON(high_prices, low_prices)
            self.hist['AROON_Up'] = aroon_up
            self.hist['AROON_Down'] = aroon_down

            # מדדי נפח
            self.hist['OBV'] = TechnicalIndicators.OBV(close_prices, volume)

            self.logger.info("Technical indicators calculated successfully")

        except Exception as e:
            error_msg = f"Error calculating technical indicators: {str(e)}"
            self.logger.error(error_msg)
            raise ValueError(error_msg)

    def generate_report(self) -> dict:
        """יצירת דוח מסכם"""
        report = {
            'timestamp': datetime.now().isoformat(),
            'symbol': self.symbol,
            'analysis_period': {
                'start': self.hist.index[0].isoformat() if self.hist is not None else None,
                'end': self.hist.index[-1].isoformat() if self.hist is not None else None
            },
            'technical_analysis': {
                'patterns': [
                    {
                        'type': pattern.pattern_type,
                        'confidence': pattern.confidence,
                        'description': pattern.description
                    }
                    for pattern in self.technical_patterns
                ],
                'support_resistance': self.support_resistance_levels
            },
            'predictions': self.price_predictions,
            'sentiment': self.analyze_sentiment(),
            'risk_metrics': self.calculate_risk_metrics()
        }

        return report

    async def auto_analyze(self):
        """הרצת ניתוח אוטומטי מלא"""
        try:
            # משיכת נתונים
            await self.fetch_all_data()

            # ניתוח טכני
            self.identify_technical_patterns()
            self.find_support_resistance()

            # תחזיות
            self.predict_prices()

            # בדיקת התראות
            triggered_alerts = self.check_alerts()

            # יצירת דוח
            report = self.generate_report()

            # שמירת הניתוח
            self.save_analysis()

            return {
                'report': report,
                'triggered_alerts': triggered_alerts
            }

        except Exception as e:
            self.logger.error(f"Error in auto analysis: {str(e)}")
            raise

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
            adx = self.hist['ADX'].iloc[-1] if 'ADX' in self.hist else np.nan
            if not np.isnan(adx):
                if adx > 25:
                    if self.hist['AROON_Up'].iloc[-1] > self.hist['AROON_Down'].iloc[-1]:
                        technical_score += 10
                        reasons.append("מגמה חיובית חזקה")
                    else:
                        technical_score -= 10
                        reasons.append("מגמה שלילית חזקה")

            scores['technical'] = technical_score / 30

            # === ציון מומנטום (25%) ===
            momentum_score = 0

            # נפח מסחר (10%)
            volume_trend = (self.hist['Volume'].tail(5).mean() /
                            self.hist['Volume'].tail(20).mean() - 1)
            if volume_trend > 0.1:
                momentum_score += 10
                reasons.append("עלייה בנפח מסחר")

            # מגמת מחיר (15%)
            price_trend = (self.hist['Close'].iloc[-1] /
                           self.hist['Close'].iloc[-20] - 1) * 100
            if price_trend > 2:
                momentum_score += 15
                reasons.append(f"מגמת מחיר חיובית ({price_trend:.1f}%)")
            elif price_trend > 0:
                momentum_score += 7

            scores['momentum'] = momentum_score / 25

            # === ציון טכני מתקדם (25%) ===
            advanced_score = 0

            # ADX trend strength (15%)
            if not np.isnan(adx):
                if adx > 25:
                    advanced_score += 15
                    reasons.append("מגמה חזקה")
                elif adx > 20:
                    advanced_score += 7

            # OBV trend (10%)
            if 'OBV' in self.hist:
                obv_trend = (self.hist['OBV'].iloc[-1] >
                             self.hist['OBV'].iloc[-5])
                if obv_trend:
                    advanced_score += 10
                    reasons.append("מגמת נפח חיובית")

            scores['advanced'] = advanced_score / 25

            # === ציון סנטימנט (20%) ===
            sentiment_score = 0

            sentiment = self.analyze_sentiment()
            if sentiment.get('rsi_signal') == 'neutral':
                sentiment_score += 7
            if sentiment.get('macd_signal') == 'bullish':
                sentiment_score += 7
            if sentiment.get('volume_signal') == 'high':
                sentiment_score += 6

            scores['sentiment'] = sentiment_score / 20

            # === חישוב ציון סופי ===
            final_score = (
                    scores['technical'] * 0.3 +
                    scores['momentum'] * 0.25 +
                    scores['advanced'] * 0.25 +
                    scores['sentiment'] * 0.2
            )

            # === קביעת המלצה ===
            if final_score > 0.7:
                recommendation = "קנייה חזקה"
            elif final_score > 0.6:
                recommendation = "קנייה"
            elif final_score < 0.3:
                recommendation = "מכירה"
            elif final_score < 0.4:
                recommendation = "מכירה חלשה"
            else:
                recommendation = "החזק"

            return {
                'המלצה': recommendation,
                'ציון_סופי': final_score,
                'ציונים_חלקיים': scores,
                'סיבות': reasons,
                'מדדים_טכניים': {
                    'RSI': float(self.hist['RSI'].iloc[-1]) if not np.isnan(self.hist['RSI'].iloc[-1]) else None,
                    'MACD': float(self.hist['MACD'].iloc[-1]) if not np.isnan(self.hist['MACD'].iloc[-1]) else None,
                    'ATR': float(self.hist['ATR'].iloc[-1]) if not np.isnan(self.hist['ATR'].iloc[-1]) else None
                }
            }

        except Exception as e:
            self.logger.error(f"Error calculating final score: {str(e)}")
            return {
                'המלצה': "לא ניתן לחשב",
                'ציון_סופי': np.nan,
                'ציונים_חלקיים': {},
                'סיבות': ["שגיאה בחישוב הציון הסופי"],
                'מדדים_טכניים': {}
            }