import tkinter as tk
from tkinter import ttk, messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import yfinance as yf
import numpy as np
import logging
from ..analyzers.enhanced_stock_analyzer import EnhancedStockAnalyzer


class ComparisonTab(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.logger = logging.getLogger(__name__)
        self.analyzers = {}  # מילון של מנתחים לכל מניה
        self.setup_ui()

    def setup_ui(self):
        """הגדרת ממשק המשתמש"""
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

        # יצירת Figure לגרפים
        self.fig = plt.Figure(figsize=(10, 6))
        self.ax = self.fig.add_subplot(111)

        self.canvas = FigureCanvasTkAgg(self.fig, charts_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def add_stock(self):
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

            # משיכת נתונים
            period = self.period_var.get()
            stock = yf.Ticker(symbol)
            analyzer.hist = stock.history(period=period)

            if len(analyzer.hist) == 0:
                raise ValueError(f"לא נמצאו נתונים עבור {symbol}")

            # חישוב אינדיקטורים
            analyzer.calculate_technical_indicators()

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
            rsi = analyzer.hist['RSI'].iloc[-1] if 'RSI' in analyzer.hist else np.nan
            metrics = analyzer.calculate_risk_metrics()

            self.comparison_tree.insert("", tk.END, values=(
                symbol,
                f"{last_price:.2f}",
                f"{change:.1f}%",
                f"{volume:,.0f}",
                f"{rsi:.1f}" if not np.isnan(rsi) else "N/A",
                f"{metrics.get('beta', np.nan):.2f}",
                f"{metrics.get('sharpe', np.nan):.2f}",
                f"{metrics.get('volatility', np.nan):.2f}"
            ))

    def update_charts(self):
        """עדכון הגרפים"""
        self.ax.clear()

        for symbol, analyzer in self.analyzers.items():
            if analyzer.hist is None:
                continue

            # נרמול מחירים ל-100
            prices = analyzer.hist['Close']
            normalized_prices = prices / prices.iloc[0] * 100

            self.ax.plot(analyzer.hist.index, normalized_prices,
                         label=symbol)

        self.ax.set_title('השוואת מחירים (מנורמל)')
        self.ax.legend()
        self.ax.grid(True)

        # רוטציה של התאריכים בציר X
        self.ax.tick_params(axis='x', rotation=45)

        # עדכון הגרף
        self.canvas.draw()