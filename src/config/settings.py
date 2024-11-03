from pathlib import Path

# נתיבים
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
CACHE_DIR = DATA_DIR / "cache"
EXPORT_DIR = DATA_DIR / "exports"
LOG_DIR = BASE_DIR / "logs"

# הגדרות Cache
CACHE_EXPIRY_HOURS = 24
MAX_CACHE_ITEMS = 1000

# הגדרות API
API_RATE_LIMIT = 5  # requests per second
API_TIMEOUT = 30    # seconds

# הגדרות ניתוח
ANALYSIS_SETTINGS = {
    'technical': {
        'rsi_periods': 14,
        'macd_fast': 12,
        'macd_slow': 26,
        'macd_signal': 9,
        'bollinger_periods': 20,
        'bollinger_std': 2
    },
    'risk': {
        'var_confidence': 0.95,
        'risk_free_rate': 0.04,
        'beta_market_index': '^TA125.TA'
    },
    'fundamental': {
        'pe_ratio_threshold': 25,
        'pb_ratio_threshold': 3,
        'min_current_ratio': 1.5,
        'min_profit_margin': 0.1
    },
    'alerts': {
        'check_interval': 300,  # seconds
        'price_change_threshold': 0.02,
        'volume_change_threshold': 1.5
    }
}

# הגדרות GUI
GUI_SETTINGS = {
    'window_size': '1400x900',
    'chart_dpi': 100,
    'theme': 'clam',
    'colors': {
        'background': '#f0f0f0',
        'foreground': '#000000',
        'accent': '#007bff',
        'warning': '#ffc107',
        'error': '#dc3545'
    },
    'fonts': {
        'default': ('Helvetica', 10),
        'heading': ('Helvetica', 12, 'bold'),
        'small': ('Helvetica', 8)
    }
}

# הגדרות לוגים
LOGGING_CONFIG = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'standard': {
            'format': '%(asctime)s [%(levelname)s] %(name)s: %(message)s'
        },
    },
    'handlers': {
        'file': {
            'level': 'INFO',
            'formatter': 'standard',
            'class': 'logging.FileHandler',
            'filename': LOG_DIR / 'app.log',
            'mode': 'a',
        },
    },
    'loggers': {
        '': {
            'handlers': ['file'],
            'level': 'INFO',
            'propagate': True
        }
    }
}