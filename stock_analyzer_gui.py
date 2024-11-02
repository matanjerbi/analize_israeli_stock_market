import tkinter as tk
from tkinter import ttk, messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from advanced_stock_analyzer import AdvancedStockAnalyzer  # הקובץ המקורי שלך


class StockAnalyzerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("מנתח המניות המתקדם")
        self.root.geometry("1200x800")
        self.root.configure(bg='#f0f0f0')

        # יצירת Frame ראשי
        self.main_frame = ttk.Frame(self.root)
        self.main_frame.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        # חלוקת המסך ל-2
        self.left_frame = ttk.Frame(self.main_frame)
        self.left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.right_frame = ttk.Frame(self.main_frame)
        self.right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # אזור הקלט
        self.create_input_area()

        # אזור התוצאות
        self.create_results_area()

        # אזור הגרפים
        self.create_charts_area()

        # משתנים לשמירת נתונים
        self.analyzer = None
        self.analysis_results = None

    def create_input_area(self):
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

        # כפתור הרצת הניתוח
        analyze_btn = ttk.Button(input_frame, text="הרץ ניתוח", command=self.run_analysis)
        analyze_btn.pack(pady=10)

    def create_results_area(self):
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

        # סרגל גלילה
        scrollbar = ttk.Scrollbar(results_frame, orient=tk.VERTICAL,
                                  command=self.results_tree.yview)
        self.results_tree.configure(yscrollcommand=scrollbar.set)

        self.results_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    def create_charts_area(self):
        charts_frame = ttk.LabelFrame(self.right_frame, text="גרפים")
        charts_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # יצירת Figure לגרפים
        self.fig = plt.Figure(figsize=(8, 10))

        # יצירת תתי-גרפים
        self.ax1 = self.fig.add_subplot(311)  # מחיר
        self.ax2 = self.fig.add_subplot(312)  # RSI
        self.ax3 = self.fig.add_subplot(313)  # MACD

        self.canvas = FigureCanvasTkAgg(self.fig, charts_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def run_analysis(self):
        try:
            # ניקוי גרפים קודמים
            self.ax1.clear()
            self.ax2.clear()
            self.ax3.clear()

            symbol = self.symbol_entry.get()
            market_index = self.market_entry.get()
            period = self.period_var.get()

            # הרצת הניתוח
            self.analyzer = AdvancedStockAnalyzer(symbol, market_index)
            self.analysis_results = self.analyzer.run_analysis(period)

            # הצגת התוצאות
            self.display_results()
            self.plot_charts()

            messagebox.showinfo("הצלחה", "הניתוח הושלם בהצלחה!")

        except Exception as e:
            messagebox.showerror("שגיאה", f"שגיאה בהרצת הניתוח: {str(e)}")

    def display_results(self):
        # ניקוי טבלת התוצאות
        for item in self.results_tree.get_children():
            self.results_tree.delete(item)

        if self.analysis_results:
            # הוספת התוצאות העיקריות
            self.results_tree.insert("", tk.END, values=("המלצה", self.analysis_results['המלצה']))
            self.results_tree.insert("", tk.END, values=("ציון סופי", f"{self.analysis_results['ציון_סופי']:.2f}"))

            # הוספת ציונים חלקיים
            for category, score in self.analysis_results['ציונים_חלקיים'].items():
                self.results_tree.insert("", tk.END, values=(f"ציון {category}", f"{score:.2f}"))

            # הוספת סיבות
            for reason in self.analysis_results['סיבות']:
                self.results_tree.insert("", tk.END, values=("סיבה", reason))

    def plot_charts(self):
        if self.analyzer and hasattr(self.analyzer, 'hist'):
            # גרף מחיר
            self.ax1.plot(self.analyzer.hist.index, self.analyzer.hist['Close'])
            self.ax1.set_title('מחיר המניה')
            self.ax1.set_xlabel('תאריך')
            self.ax1.set_ylabel('מחיר')

            # גרף RSI
            self.ax2.plot(self.analyzer.hist.index, self.analyzer.hist['RSI'])
            self.ax2.set_title('RSI')
            self.ax2.axhline(y=70, color='r', linestyle='--')
            self.ax2.axhline(y=30, color='g', linestyle='--')

            # גרף MACD
            self.ax3.plot(self.analyzer.hist.index, self.analyzer.hist['MACD'], label='MACD')
            self.ax3.plot(self.analyzer.hist.index, self.analyzer.hist['MACD_Signal'],
                          label='Signal Line')
            self.ax3.set_title('MACD')
            self.ax3.legend()

            # התאמת המרווחים בין הגרפים
            self.fig.tight_layout()

            # עדכון הגרפים
            self.canvas.draw()


def main():
    root = tk.Tk()
    app = StockAnalyzerGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()