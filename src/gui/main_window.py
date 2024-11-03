import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from datetime import datetime
from .analysis_tab import AnalysisTab
from .comparison_tab import ComparisonTab
from .alerts_tab import AlertsTab
import logging


class MainWindow:
    def __init__(self, root):
        self.root = root
        self.logger = logging.getLogger(__name__)
        self.setup_main_window()
        self.create_notebook()
        self.initialize_tabs()
        self.setup_menu()

    def setup_main_window(self):
        """הגדרת החלון הראשי"""
        self.root.title("מנתח המניות המתקדם")
        self.root.geometry("1600x900")  # הגדלת החלון הראשי
        self.root.configure(bg='#f0f0f0')

        # הגדרת גודל מינימלי
        self.root.minsize(1200, 700)

    def create_notebook(self):
        """יצירת מחברת עם טאבים"""
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

    def initialize_tabs(self):
        """אתחול כל הטאבים"""
        # הגדרת סגנון
        style = ttk.Style()
        style.configure('Tab', padding=[20, 10])  # הגדלת הטאבים

        self.analysis_tab = AnalysisTab(self.notebook)
        self.comparison_tab = ComparisonTab(self.notebook)
        self.alerts_tab = AlertsTab(self.notebook)

        self.notebook.add(self.analysis_tab, text="ניתוח")
        self.notebook.add(self.comparison_tab, text="השוואה")
        self.notebook.add(self.alerts_tab, text="התראות")

    def setup_menu(self):
        """יצירת תפריט"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)

        # תפריט קובץ
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="קובץ", menu=file_menu)
        file_menu.add_command(label="ייצא לאקסל", command=self.export_to_excel)
        file_menu.add_command(label="שמור ניתוח", command=self.save_analysis)
        file_menu.add_command(label="טען ניתוח", command=self.load_analysis)
        file_menu.add_separator()
        file_menu.add_command(label="יציאה", command=self.root.quit)

        # תפריט תצוגה
        view_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="תצוגה", menu=view_menu)
        self.dark_mode = tk.BooleanVar(value=False)
        view_menu.add_checkbutton(label="מצב כהה",
                                  variable=self.dark_mode,
                                  command=self.toggle_theme)

        # תפריט עזרה
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="עזרה", menu=help_menu)
        help_menu.add_command(label="מדריך", command=self.show_help)
        help_menu.add_command(label="אודות", command=self.show_about)

    def toggle_theme(self):
        """החלפת ערכת נושא"""
        if self.dark_mode.get():
            style = ttk.Style()
            style.configure(".",
                            background='#2d2d2d',
                            foreground='white',
                            fieldbackground='#3d3d3d')
            self.root.configure(bg='#2d2d2d')
        else:
            style = ttk.Style()
            style.configure(".",
                            background='#f0f0f0',
                            foreground='black',
                            fieldbackground='white')
            self.root.configure(bg='#f0f0f0')

    def export_to_excel(self):
        if hasattr(self.analysis_tab, 'analyzer') and self.analysis_tab.analyzer:
            try:
                filename = filedialog.asksaveasfilename(
                    defaultextension=".xlsx",
                    filetypes=[("Excel files", "*.xlsx")],
                    title="שמור קובץ אקסל"
                )
                if filename:
                    self.analysis_tab.analyzer.export_to_excel(filename)
                    messagebox.showinfo("הצלחה", "הקובץ נוצר בהצלחה!")
            except Exception as e:
                messagebox.showerror("שגיאה", f"שגיאה בייצוא: {str(e)}")
        else:
            messagebox.showwarning("שגיאה", "אנא בצע ניתוח לפני הייצוא")

    def save_analysis(self):
        if hasattr(self.analysis_tab, 'analyzer') and self.analysis_tab.analyzer:
            try:
                filename = filedialog.asksaveasfilename(
                    defaultextension=".json",
                    filetypes=[("JSON files", "*.json")],
                    title="שמור ניתוח"
                )
                if filename:
                    self.analysis_tab.analyzer.save_analysis(filename)
                    messagebox.showinfo("הצלחה", "הניתוח נשמר בהצלחה!")
            except Exception as e:
                messagebox.showerror("שגיאה", f"שגיאה בשמירה: {str(e)}")
        else:
            messagebox.showwarning("שגיאה", "אנא בצע ניתוח לפני השמירה")

    def load_analysis(self):
        try:
            filename = filedialog.askopenfilename(
                filetypes=[("JSON files", "*.json")],
                title="טען ניתוח"
            )
            if filename:
                self.analysis_tab.analyzer.load_analysis(filename)
                self.analysis_tab.update_display()
                messagebox.showinfo("הצלחה", "הניתוח נטען בהצלחה!")
        except Exception as e:
            messagebox.showerror("שגיאה", f"שגיאה בטעינה: {str(e)}")

    def show_help(self):
        help_text = """
        מנתח המניות המתקדם

        תכונות עיקריות:
        - ניתוח טכני מתקדם
        - השוואת מניות
        - מערכת התראות
        - ייצוא דוחות

        לעזרה נוספת, בקרו באתר שלנו.
        """
        messagebox.showinfo("עזרה", help_text)

    def show_about(self):
        about_text = """
        מנתח המניות המתקדם
        גרסה 1.0

        כל הזכויות שמורות © 2024
        """
        messagebox.showinfo("אודות", about_text)