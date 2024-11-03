import pickle
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Optional
import logging
from ..config.settings import CACHE_DIR, CACHE_EXPIRY_HOURS, MAX_CACHE_ITEMS

class CacheManager:
    def __init__(self):
        self.cache_dir = CACHE_DIR
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.logger = logging.getLogger(__name__)

    def get(self, key: str) -> Optional[Any]:
        """קבלת ערך מהמטמון"""
        try:
            cache_file = self.cache_dir / f"{key}.pickle"
            if not cache_file.exists():
                return None

            with open(cache_file, 'rb') as f:
                data = pickle.load(f)

            # בדיקת תפוגה
            if datetime.now() > data['expiry']:
                self.delete(key)
                return None

            return data['value']

        except Exception as e:
            self.logger.error(f"Error getting from cache: {str(e)}")
            return None

    def set(self, key: str, value: Any, expiry_hours: int = CACHE_EXPIRY_HOURS):
        """שמירת ערך במטמון"""
        try:
            # בדיקת גודל המטמון
            if len(list(self.cache_dir.glob('*.pickle'))) >= MAX_CACHE_ITEMS:
                self.cleanup()

            cache_file = self.cache_dir / f"{key}.pickle"
            data = {
                'value': value,
                'expiry': datetime.now() + timedelta(hours=expiry_hours),
                'created': datetime.now()
            }

            with open(cache_file, 'wb') as f:
                pickle.dump(data, f)

        except Exception as e:
            self.logger.error(f"Error setting cache: {str(e)}")

    def delete(self, key: str):
        """מחיקת ערך מהמטמון"""
        try:
            cache_file = self.cache_dir / f"{key}.pickle"
            if cache_file.exists():
                cache_file.unlink()
        except Exception as e:
            self.logger.error(f"Error deleting from cache: {str(e)}")

    def cleanup(self):
        """ניקוי ערכים ישנים מהמטמון"""
        try:
            cache_files = list(self.cache_dir.glob('*.pickle'))
            cache_files.sort(key=lambda x: x.stat().st_mtime)

            # מחיקת 20% מהקבצים הישנים ביותר
            files_to_delete = cache_files[:int(len(cache_files) * 0.2)]
            for file in files_to_delete:
                file.unlink()

        except Exception as e:
            self.logger.error(f"Error in cache cleanup: {str(e)}")

    def clear(self):
        """ניקוי כל המטמון"""
        try:
            for cache_file in self.cache_dir.glob('*.pickle'):
                cache_file.unlink()
        except Exception as e:
            self.logger.error(f"Error clearing cache: {str(e)}")