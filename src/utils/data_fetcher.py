import aiohttp
import asyncio
from typing import Dict, Any, Optional
import logging
from ..config.settings import API_RATE_LIMIT, API_TIMEOUT
from .cache_manager import CacheManager

class DataFetcher:
    def __init__(self):
        self.cache = CacheManager()
        self.logger = logging.getLogger(__name__)
        self._semaphore = asyncio.Semaphore(API_RATE_LIMIT)

    async def fetch_with_cache(self, url: str, cache_key: str = None) -> Optional[Dict[str, Any]]:
        """משיכת נתונים עם תמיכה במטמון"""
        if cache_key is None:
            cache_key = url

        # בדיקה במטמון
        cached_data = self.cache.get(cache_key)
        if cached_data is not None:
            return cached_data

        # משיכת נתונים חדשים
        async with self._semaphore:
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(url, timeout=API_TIMEOUT) as response:
                        if response.status == 200:
                            data = await response.json()
                            self.cache.set(cache_key, data)
                            return data
                        else:
                            self.logger.error(f"HTTP {response.status} for URL: {url}")
                            return None

            except asyncio.TimeoutError:
                self.logger.error(f"Timeout fetching URL: {url}")
                return None
            except Exception as e:
                self.logger.error(f"Error fetching data: {str(e)}")
                return None

    async def fetch_stock_data(self, symbol: str) -> Optional[Dict[str, Any]]:
        """משיכת נתוני מניה"""
        url = f"https://api.example.com/stocks/{symbol}"  # תחליף עם ה-API האמיתי שלך
        return await self.fetch_with_cache(url, f"stock_{symbol}")

    async def fetch_market_data(self, market_index: str) -> Optional[Dict[str, Any]]:
        """משיכת נתוני שוק"""
        url = f"https://api.example.com/market/{market_index}"
        return await self.fetch_with_cache(url, f"market_{market_index}")

    async def fetch_batch_data(self, symbols: list[str]) -> Dict[str, Any]:
        """משיכת נתונים עבור מספר מניות במקביל"""
        tasks = [self.fetch_stock_data(symbol) for symbol in symbols]
        results = await asyncio.gather(*tasks)
        return {symbol: result for symbol, result in zip(symbols, results) if result is not None}

    async def fetch_historical_data(self, symbol: str, start_date: str, end_date: str) -> Optional[Dict[str, Any]]:
        """משיכת נתונים היסטוריים"""
        url = f"https://api.example.com/stocks/{symbol}/history?start={start_date}&end={end_date}"
        return await self.fetch_with_cache(url, f"history_{symbol}_{start_date}_{end_date}")

    async def fetch_financial_statements(self, symbol: str) -> Optional[Dict[str, Any]]:
        """משיכת דוחות כספיים"""
        url = f"https://api.example.com/stocks/{symbol}/financials"
        return await self.fetch_with_cache(url, f"financials_{symbol}")

    async def fetch_company_info(self, symbol: str) -> Optional[Dict[str, Any]]:
        """משיכת מידע על החברה"""
        url = f"https://api.example.com/stocks/{symbol}/info"
        return await self.fetch_with_cache(url, f"info_{symbol}")

    def clear_cache(self):
        """ניקוי המטמון"""
        self.cache.clear()