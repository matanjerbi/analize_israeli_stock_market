import tkinter as tk
from tkinter import ttk, messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import pandas as pd
import numpy as np
from ..analyzers.enhanced_stock_analyzer import EnhancedStockAnalyzer
import logging
from datetime import datetime


class ComparisonTab(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.logger = logging.getLogger(__name__)
        self.analyzers = {}  # מילון של מנתחים לכל מניה
        self.setup_ui()

    def setup_ui(self):
        """הגדרת ממשק המשתמש"""
        # יצירת מסגרות
        self.create_input_frame()
        self.create_comparison_frame()
        self.create_charts_frame()

    def create_input_frame(self):
        """יצירת אזור הקלט"""
        input_frame = ttk.LabelFrame(self, text="הוספת מניות להשוואה")
        input_frame.pack(fill=tk.X, padx=5, pady=5)

        # שדה להזנת סימול
        ttk.Label(input_frame, text="סימול מניה:").pack(pady=2)
        self.symbol_entry = ttk.Entry(input_frame)
        self.symbol_entry.pack(pady=2)

        # תקופת השוואה
        ttk.Label(input_frame, text="תקופת השוואה:").pack(pady=2)
        self.period_var = tk.StringVar(value="1y")
        period_choices = ["1mo", "3mo", "6mo", "1y", "2y", "5y"]
        period_menu = ttk.OptionMenu(input_frame, self.period_var, *period_choices)
        period_menu.pack(pady=2)

        # כפתורים
        buttons_frame = ttk.Frame(input_frame)
        buttons_frame.pack(fill=tk.X, pady=5)

        ttk.Button(buttons_frame, text="הוסף מניה",
                   command=self.add_stock).pack(side=tk.LEFT, padx=5)
        ttk.Button(buttons_frame, text="הסר מניה",
                   command=self.remove_stock).pack(side=tk.LEFT, padx=5)
        ttk.Button(buttons_frame, text="נקה הכל",
                   command=self.clear_all).pack(side=tk.LEFT, padx=5)

        # רשימת מניות להשוואה
        ttk.Label(input_frame, text="מניות בהשוואה:").pack(pady=2)
        self.stocks_listbox = tk.Listbox(input_frame, height=5)
        self.stocks_listbox.pack(fill=tk.X, pady=2)

    def create_comparison_frame(self):
        """יצירת אזור טבלת ההשוואה"""
        comparison_frame = ttk.LabelFrame(self, text="טבלת השוואה")
        comparison_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # טבלת השוואה
        self.comparison_tree = ttk.Treeview(comparison_frame,
                                            show="headings",
                                            height=10)

        # הגדרת עמודות
        columns = [
            "symbol", "last_price", "change_percent", "volume",
            "rsi", "beta", "sharpe", "volatility"
        ]
        self.comparison_tree["columns"] = columns

        # כותרות עמודות
        column_names = {
            "symbol": "סימול",
            "last_price": "מחיר אחרון",
            "change_percent": "שינוי %",
            "volume": "מחזור",
            "rsi": "RSI",
            "beta": "בטא",
            "sharpe": "שארפ",
            "volatility": "תנודתיות"
        }

        for col in columns:
            self.comparison_tree.heading(col, text=column_names[col])
            self.comparison_tree.column(col, width=100)

        # סרגל גלילה
        scrollbar = ttk.Scrollbar(comparison_frame, orient=tk.VERTICAL,
                                  command=self.comparison_tree.yview)
        self.comparison_tree.configure(yscrollcommand=scrollbar.set)

        self.comparison_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    def create_charts_frame(self):
        """יצירת אזור הגרפים"""
        charts_frame = ttk.LabelFrame(self, text="השוואה גרפית")
        charts_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # יצירת לשוניות לגרפים שונים
        self.charts_notebook = ttk.Notebook(charts_frame)
        self.charts_notebook.pack(fill=tk.BOTH, expand=True)

        # גרף מחירים
        self.price_frame = ttk.Frame(self.charts_notebook)
        self.charts_notebook.add(self.price_frame, text="מחירים")

        self.fig_price = plt.Figure(figsize=(10, 6))
        self.ax_price = self.fig_price.add_subplot(111)
        self.canvas_price = FigureCanvasTkAgg(self.fig_price, self.price_frame)
        self.canvas_price.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        # גרף תשואות
        self.returns_frame = ttk.Frame(self.charts_notebook)
        self.charts_notebook.add(self.returns_frame, text="תשואות")

        self.fig_returns = plt.Figure(figsize=(10, 6))
        self.ax_returns = self.fig_returns.add_subplot(111)
        self.canvas_returns = FigureCanvasTkAgg(self.fig_returns, self.returns_frame)
        self.canvas_returns.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    async def add_stock(self):
        """הוספת מניה להשוואה"""
        symbol = self.symbol_entry.get().strip()
        if not symbol:
            messagebox.showwarning("שגיאה", "נא להזין סימול מניה")
            return

        if symbol in self.analyzers:
            messagebox.showwarning("שגיאה", "המניה כבר נמצאת בהשוואה")
            return

        try:
            # יצירת מנתח חדש
            analyzer = EnhancedStockAnalyzer(symbol)
            await analyzer.fetch_all_data()

            # שמירת המנתח
            self.analyzers[symbol] = analyzer

            # הוספה לרשימת המניות
            self.stocks_listbox.insert(tk.END, symbol)

            # עדכון טבלה וגרפים
            self.update_comparison()
            self.update_charts()

            self.symbol_entry.delete(0, tk.END)

        except Exception as e:
            messagebox.showerror("שגיאה", f"שגיאה בהוספת המניה: {str(e)}")
            self.logger.error(f"Error adding stock {symbol}: {str(e)}")

    def remove_stock(self):
        """הסרת מניה מההשוואה"""
        selection = self.stocks_listbox.curselection()
        if not selection:
            messagebox.showwarning("שגיאה", "נא לבחור מניה להסרה")
            return

        symbol = self.stocks_listbox.get(selection[0])
        if symbol in self.analyzers:
            del self.analyzers[symbol]
            self.stocks_listbox.delete(selection[0])
            self.update_comparison()
            self.update_charts()

    def clear_all(self):
        """ניקוי כל ההשוואה"""
        self.analyzers.clear()
        self.stocks_listbox.delete(0, tk.END)
        self.update_comparison()
        self.update_charts()

    def update_comparison(self):
        """עדכון טבלת ההשוואה"""
        # ניקוי טבלה
        for item in self.comparison_tree.get_children():
            self.comparison_tree.delete(item)

        # עדכון נתונים
        for symbol, analyzer in self.analyzers.items():
            if analyzer.hist is None:
                continue

            last_price = analyzer.hist['Close'].iloc[-1]
            change = (analyzer.hist['Close'].iloc[-1] / analyzer.hist['Close'].iloc[-2] - 1) * 100
            volume = analyzer.hist['Volume'].iloc[-1]

            # חישוב מדדים
            risk_metrics = analyzer.calculate_risk_metrics()
            rsi = analyzer.hist['RSI'].iloc[-1] if 'RSI' in analyzer.hist else np.nan

            self.comparison_tree.insert("", tk.END, values=(
                symbol,
                f"{last_price:.2f}",
                f"{change:.1f}%",
                f"{volume:,.0f}",
                f"{rsi:.1f}" if not np.isnan(rsi) else "N/A",
                f"{risk_metrics.get('beta', np.nan):.2f}",
                f"{risk_metrics.get('sharpe', np.nan):.2f}",
                f"{risk_metrics.get('volatility', np.nan):.2f}"
            ))

    def update_charts(self):
        """עדכון הגרפים"""
        # ניקוי גרפים
        self.ax_price.clear()
        self.ax_returns.clear()

        # עדכון גרף מחירים
        for symbol, analyzer in self.analyzers.items():
            if analyzer.hist is None:
                continue

            # נרמול מחירים ל-100
            prices = analyzer.hist['Close']
            normalized_prices = prices / prices.iloc[0] * 100

            self.ax_price.plot(analyzer.hist.index, normalized_prices,
                               label=symbol)

        self.ax_price.set_title('השוואת מחירים (מנורמל)')
        self.ax_price.legend()
        self.ax_price.grid(True)

        # עדכון גרף תשואות
        for symbol, analyzer in self.analyzers.items():
            if analyzer.hist is None:
                continue

            returns = analyzer.hist['Close'].pct_change().cumsum() * 100
            self.ax_returns.plot(analyzer.hist.index, returns,
                                 label=symbol)

        self.ax_returns.set_title('תשואה מצטברת')
        self.ax_returns.legend()
        self.ax_returns.grid(True)

        # רענון הגרפים
        self.canvas_price.draw()
        self.canvas_returns.draw()

    def calculate_correlations(self):
        """חישוב מטריצת קורלציות"""
        returns_data = {}

        for symbol, analyzer in self.analyzers.items():
            if analyzer.hist is not None:
                returns_data[symbol] = analyzer.hist['Close'].pct_change()

        if returns_data:
            return pd.DataFrame(returns_data).corr()
        return pd.DataFrame()