import tkinter as tk
from tkinter import ttk
from src.gui.main_window import MainWindow
import logging
from pathlib import Path
from datetime import datetime
import sys


def setup_directories():
    """יצירת תיקיות נדרשות"""
    directories = ['data/cache', 'data/exports', 'logs']
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)


def setup_logging():
    """הגדרת מערכת הלוגים"""
    log_dir = Path("logs")
    log_file = log_dir / f'app_{datetime.now().strftime("%Y%m%d")}.log'

    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler(sys.stdout)
        ]
    )


def main():
    try:
        # הגדרת תיקיות ולוגים
        setup_directories()
        setup_logging()

        logger = logging.getLogger(__name__)
        logger.info("Starting Stock Analyzer Application")

        # יצירת חלון ראשי
        root = tk.Tk()
        root.title("מנתח המניות המתקדם")

        # הגדרת סגנון
        style = ttk.Style()
        style.theme_use('clam')

        # יצירת האפליקציה
        app = MainWindow(root)

        # הרצת לולאת האירועים
        root.mainloop()

    except Exception as e:
        logger.error(f"Error starting application: {str(e)}")
        raise


if __name__ == "__main__":
    main()