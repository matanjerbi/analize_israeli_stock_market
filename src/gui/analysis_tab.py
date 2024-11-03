import tkinter as tk
from tkinter import ttk, messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from ..analyzers.enhanced_stock_analyzer import EnhancedStockAnalyzer
import logging
from datetime import datetime
import yfinance as yf
import numpy as np
import pandas as pd


class AnalysisTab(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.logger = logging.getLogger(__name__)
        self.analyzer = None

        # יצירת המסגרות הראשיות
        self.create_frames()

        # יצירת האזורים השונים
        self.create_input_frame()
        self.create_results_frame()
        self.create_charts_frame()

        # הגדרת משקולות לחלוקת המסך
        self.pack(fill=tk.BOTH, expand=True)

    def create_frames(self):
        """יצירת מסגרות ראשיות"""
        # מסגרת שמאלית (פקדים ותוצאות)
        self.left_frame = ttk.Frame(self)
        self.left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=False, padx=5, pady=5)

        # מסגרת ימנית (גרפים)
        self.right_frame = ttk.Frame(self)
        self.right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5, pady=5)

    def create_input_frame(self):
        """יצירת אזור הקלט"""
        input_frame = ttk.LabelFrame(self.left_frame, text="הגדרות ניתוח")
        input_frame.pack(fill=tk.X, padx=5, pady=5)

        # סימול מניה
        ttk.Label(input_frame, text="סימול מניה:").pack(pady=2)
        self.symbol_entry = ttk.Entry(input_frame)
        self.symbol_entry.pack(pady=2)

        # מדד ייחוס
        ttk.Label(input_frame, text="מדד ייחוס:").pack(pady=2)
        self.market_entry = ttk.Entry(input_frame)
        self.market_entry.insert(0, "^TA125.TA")
        self.market_entry.pack(pady=2)

        # תקופת ניתוח
        ttk.Label(input_frame, text="תקופת ניתוח:").pack(pady=2)
        self.period_var = tk.StringVar(value="1y")
        period_choices = ["1mo", "3mo", "6mo", "1y", "2y", "5y", "max"]
        period_menu = ttk.OptionMenu(input_frame, self.period_var, *period_choices)
        period_menu.pack(pady=2)

        # כפתורים
        buttons_frame = ttk.Frame(input_frame)
        buttons_frame.pack(fill=tk.X, pady=5)

        ttk.Button(buttons_frame, text="הרץ ניתוח",
                   command=self.run_analysis).pack(side=tk.LEFT, padx=5)
        ttk.Button(buttons_frame, text="נקה נתונים",
                   command=self.clear_data).pack(side=tk.LEFT, padx=5)

        # לוג
        self.create_log_area(input_frame)

    def create_log_area(self, parent):
        """יצירת אזור הלוג"""
        log_frame = ttk.LabelFrame(parent, text="לוג")
        log_frame.pack(fill=tk.X, padx=5, pady=5)

        self.log_text = tk.Text(log_frame, height=4, width=50)
        self.log_text.pack(side=tk.LEFT, fill=tk.X, expand=True)

        scrollbar = ttk.Scrollbar(log_frame, orient=tk.VERTICAL,
                                  command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    def create_results_frame(self):
        """יצירת אזור התוצאות"""
        results_frame = ttk.LabelFrame(self.left_frame, text="תוצאות הניתוח")
        results_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # טבלת תוצאות
        self.results_tree = ttk.Treeview(results_frame,
                                         columns=("category", "value"),
                                         show="headings",
                                         height=20)

        self.results_tree.heading("category", text="קטגוריה")
        self.results_tree.heading("value", text="ערך")
        self.results_tree.column("category", width=150)
        self.results_tree.column("value", width=150)

        scrollbar = ttk.Scrollbar(results_frame, orient=tk.VERTICAL,
                                  command=self.results_tree.yview)
        self.results_tree.configure(yscrollcommand=scrollbar.set)

        self.results_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    def create_charts_frame(self):
        """יצירת אזור הגרפים"""
        charts_frame = ttk.LabelFrame(self.right_frame, text="גרפים")
        charts_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # יצירת Figure לגרפים
        self.fig = plt.Figure(figsize=(12, 8))  # הגדלת הגודל של הגרפים

        # יצירת תתי-גרפים
        self.ax1 = self.fig.add_subplot(411)  # מחיר
        self.ax2 = self.fig.add_subplot(412)  # RSI
        self.ax3 = self.fig.add_subplot(413)  # MACD
        self.ax4 = self.fig.add_subplot(414)  # נפח מסחר

        # הוספת Canvas
        self.canvas = FigureCanvasTkAgg(self.fig, charts_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def log_message(self, message):
        """הוספת הודעה ללוג"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_text.insert(tk.END, f"[{timestamp}] {message}\n")
        self.log_text.see(tk.END)

    def clear_data(self):
        """ניקוי כל הנתונים המוצגים"""
        # ניקוי טבלת תוצאות
        for item in self.results_tree.get_children():
            self.results_tree.delete(item)

        # ניקוי גרפים
        for ax in [self.ax1, self.ax2, self.ax3, self.ax4]:
            ax.clear()
        self.canvas.draw()

        # ניקוי לוג
        self.log_text.delete(1.0, tk.END)
        self.log_message("הנתונים נוקו")

    def run_analysis(self):
        """הרצת הניתוח"""
        try:
            symbol = self.symbol_entry.get()
            if not symbol:
                raise ValueError("נא להזין סימול מניה")

            self.log_message(f"מתחיל ניתוח עבור {symbol}")

            market_index = self.market_entry.get()
            period = self.period_var.get()

            # יצירת מנתח חדש
            self.analyzer = EnhancedStockAnalyzer(symbol, market_index)
            self.log_message("נוצר מנתח חדש")

            try:
                # משיכת נתונים
                self.log_message("מושך נתונים...")
                ticker = yf.Ticker(symbol)
                self.analyzer.hist = ticker.history(period=period)

                if len(self.analyzer.hist) == 0:
                    raise ValueError(f"לא נמצאו נתונים עבור {symbol}")

                self.log_message(f"נמצאו {len(self.analyzer.hist)} נתונים היסטוריים")

                # חישוב אינדיקטורים טכניים
                self.log_message("מחשב אינדיקטורים טכניים...")
                self.analyzer.calculate_technical_indicators()

                # זיהוי תבניות
                self.log_message("מזהה תבניות טכניות...")
                self.analyzer.identify_technical_patterns()

                # מציאת רמות תמיכה והתנגדות
                self.log_message("מחשב רמות תמיכה והתנגדות...")
                self.analyzer.find_support_resistance()

                # חיזוי מחירים
                self.log_message("מחשב תחזיות...")
                self.analyzer.predict_prices()

                # הצגת התוצאות
                self.log_message("מציג תוצאות...")
                self.update_display()

                self.log_message("הניתוח הושלם בהצלחה")
                messagebox.showinfo("הצלחה", "הניתוח הושלם בהצלחה!")

            except Exception as e:
                error_msg = f"שגיאה בניתוח: {str(e)}"
                self.log_message(error_msg)
                messagebox.showerror("שגיאה", error_msg)
                self.logger.error(error_msg)

        except Exception as e:
            error_msg = f"שגיאה כללית: {str(e)}"
            self.log_message(error_msg)
            messagebox.showerror("שגיאה", error_msg)
            self.logger.error(error_msg)

    def update_display(self):
        """עדכון תצוגת התוצאות"""
        if not self.analyzer:
            return

        # ניקוי תצוגה קודמת
        self.clear_data()

        # חישוב המלצה
        results = self.analyzer.calculate_final_score()

        # הצגת המלצה וציון סופי
        self.results_tree.insert("", tk.END, values=(
            "המלצה",
            results['המלצה']
        ))
        self.results_tree.insert("", tk.END, values=(
            "ציון סופי",
            f"{results['ציון_סופי']:.2f}"
        ))

        # הצגת ציונים חלקיים
        for category, score in results['ציונים_חלקיים'].items():
            self.results_tree.insert("", tk.END, values=(
                f"ציון {category}",
                f"{score:.2f}"
            ))

        # הצגת סיבות
        for reason in results['סיבות']:
            self.results_tree.insert("", tk.END, values=(
                "סיבה",
                reason
            ))

        # הצגת תבניות טכניות
        for pattern in self.analyzer.technical_patterns:
            self.results_tree.insert("", tk.END, values=(
                "תבנית טכנית",
                f"{pattern.pattern_type} ({pattern.confidence:.1f}%)"
            ))

        # הצגת רמות תמיכה והתנגדות
        for level in self.analyzer.support_resistance_levels["support"]:
            self.results_tree.insert("", tk.END, values=(
                "רמת תמיכה",
                f"{level['price']:.2f}"
            ))

        for level in self.analyzer.support_resistance_levels["resistance"]:
            self.results_tree.insert("", tk.END, values=(
                "רמת התנגדות",
                f"{level['price']:.2f}"
            ))

        # עדכון גרפים
        self.update_charts()

    def update_charts(self):
        """עדכון הגרפים"""
        if not self.analyzer or self.analyzer.hist is None:
            return

        # מחיקת הגרפים הקודמים
        for ax in [self.ax1, self.ax2, self.ax3, self.ax4]:
            ax.clear()

        # גרף מחיר
        self.ax1.plot(self.analyzer.hist.index, self.analyzer.hist['Close'], label='מחיר סגירה')
        if 'BBANDS_Upper' in self.analyzer.hist.columns:
            self.ax1.plot(self.analyzer.hist.index, self.analyzer.hist['BBANDS_Upper'], 'r--', label='Bollinger Upper')
            self.ax1.plot(self.analyzer.hist.index, self.analyzer.hist['BBANDS_Lower'], 'r--', label='Bollinger Lower')
        self.ax1.set_title('מחיר המניה', fontsize=12, pad=10)
        self.ax1.legend()
        self.ax1.grid(True)

        # גרף RSI
        self.ax2.plot(self.analyzer.hist.index, self.analyzer.hist['RSI'])
        self.ax2.axhline(y=70, color='r', linestyle='--')
        self.ax2.axhline(y=30, color='g', linestyle='--')
        self.ax2.set_title('RSI', fontsize=12, pad=10)
        self.ax2.grid(True)

        # גרף MACD
        self.ax3.plot(self.analyzer.hist.index, self.analyzer.hist['MACD'], label='MACD')
        self.ax3.plot(self.analyzer.hist.index, self.analyzer.hist['MACD_Signal'], label='Signal Line')
        self.ax3.bar(self.analyzer.hist.index, self.analyzer.hist['MACD_Hist'],
                     color=['g' if x > 0 else 'r' for x in self.analyzer.hist['MACD_Hist']],
                     alpha=0.3)
        self.ax3.set_title('MACD', fontsize=12, pad=10)
        self.ax3.legend()
        self.ax3.grid(True)

        # גרף נפח מ
        # גרף נפח מסחר
        self.ax4.bar(self.analyzer.hist.index, self.analyzer.hist['Volume'], alpha=0.5)
        self.ax4.set_title('נפח מסחר', fontsize=12, pad=10)
        self.ax4.grid(True)

        # התאמת המרווחים
        self.fig.tight_layout(pad=3.0)  # הגדלת המרווח בין הגרפים

        # רוטציה של התאריכים בציר X
        for ax in [self.ax1, self.ax2, self.ax3, self.ax4]:
            ax.tick_params(axis='x', rotation=45)

        # עדכון הגרפים
        self.canvas.draw()
