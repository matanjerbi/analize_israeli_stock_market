import tkinter as tk
from tkinter import ttk, messagebox
import pandas as pd
from datetime import datetime
import logging
from ..analyzers.enhanced_stock_analyzer import StockAlert


class AlertsTab(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.logger = logging.getLogger(__name__)
        self.alerts = {}  # מילון של התראות לפי סימול
        self.setup_ui()

    def setup_ui(self):
        """הגדרת ממשק המשתמש"""
        self.create_alert_creation_frame()
        self.create_active_alerts_frame()
        self.create_alerts_history_frame()

    def create_alert_creation_frame(self):
        """יצירת אזור הגדרת התראות חדשות"""
        creation_frame = ttk.LabelFrame(self, text="הגדרת התראה חדשה")
        creation_frame.pack(fill=tk.X, padx=5, pady=5)

        # שורה ראשונה
        row1 = ttk.Frame(creation_frame)
        row1.pack(fill=tk.X, pady=5)

        # סימול מניה
        ttk.Label(row1, text="סימול מניה:").pack(side=tk.LEFT, padx=5)
        self.symbol_entry = ttk.Entry(row1, width=10)
        self.symbol_entry.pack(side=tk.LEFT, padx=5)

        # סוג התראה
        ttk.Label(row1, text="סוג התראה:").pack(side=tk.LEFT, padx=5)
        self.alert_type_var = tk.StringVar(value="price")
        alert_types = {
            "price": "מחיר",
            "volume": "מחזור מסחר",
            "rsi": "RSI",
            "macd": "MACD"
        }
        self.alert_type_menu = ttk.OptionMenu(row1, self.alert_type_var,
                                              "price", *alert_types.keys(),
                                              command=self.update_condition_options)
        self.alert_type_menu.pack(side=tk.LEFT, padx=5)

        # שורה שנייה
        row2 = ttk.Frame(creation_frame)
        row2.pack(fill=tk.X, pady=5)

        # תנאי
        ttk.Label(row2, text="תנאי:").pack(side=tk.LEFT, padx=5)
        self.condition_var = tk.StringVar(value="above")
        self.condition_menu = ttk.OptionMenu(row2, self.condition_var,
                                             "above", "above", "below")
        self.condition_menu.pack(side=tk.LEFT, padx=5)

        # ערך
        ttk.Label(row2, text="ערך:").pack(side=tk.LEFT, padx=5)
        self.value_entry = ttk.Entry(row2, width=10)
        self.value_entry.pack(side=tk.LEFT, padx=5)

        # כפתור יצירת התראה
        ttk.Button(creation_frame, text="צור התראה",
                   command=self.create_alert).pack(pady=5)

    def create_active_alerts_frame(self):
        """יצירת אזור התראות פעילות"""
        active_frame = ttk.LabelFrame(self, text="התראות פעילות")
        active_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # טבלת התראות פעילות
        self.active_tree = ttk.Treeview(active_frame,
                                        columns=("symbol", "type", "condition", "value", "created"),
                                        show="headings",
                                        height=10)

        # הגדרת עמודות
        self.active_tree.heading("symbol", text="סימול")
        self.active_tree.heading("type", text="סוג")
        self.active_tree.heading("condition", text="תנאי")
        self.active_tree.heading("value", text="ערך")
        self.active_tree.heading("created", text="נוצר ב-")

        # רוחב עמודות
        for col in self.active_tree["columns"]:
            self.active_tree.column(col, width=100)

        # סרגל גלילה
        scrollbar = ttk.Scrollbar(active_frame, orient=tk.VERTICAL,
                                  command=self.active_tree.yview)
        self.active_tree.configure(yscrollcommand=scrollbar.set)

        self.active_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # כפתור הסרת התראה
        ttk.Button(active_frame, text="הסר התראה",
                   command=self.remove_alert).pack(pady=5)

    def create_alerts_history_frame(self):
        """יצירת אזור היסטוריית התראות"""
        history_frame = ttk.LabelFrame(self, text="היסטוריית התראות")
        history_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # טבלת היסטוריה
        self.history_tree = ttk.Treeview(history_frame,
                                         columns=("symbol", "type", "condition", "value", "triggered"),
                                         show="headings",
                                         height=10)

        # הגדרת עמודות
        self.history_tree.heading("symbol", text="סימול")
        self.history_tree.heading("type", text="סוג")
        self.history_tree.heading("condition", text="תנאי")
        self.history_tree.heading("value", text="ערך")
        self.history_tree.heading("triggered", text="הופעל ב-")

        # רוחב עמודות
        for col in self.history_tree["columns"]:
            self.history_tree.column(col, width=100)

        # סרגל גלילה
        scrollbar = ttk.Scrollbar(history_frame, orient=tk.VERTICAL,
                                  command=self.history_tree.yview)
        self.history_tree.configure(yscrollcommand=scrollbar.set)

        self.history_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    def update_condition_options(self, _=None):
        """עדכון אפשרויות התנאי בהתאם לסוג ההתראה"""
        alert_type = self.alert_type_var.get()

        conditions = {
            "price": ["above", "below"],
            "volume": ["above", ],
            "rsi": ["above", "below"],
            "macd": ["crossover", "crossunder"]
        }

        menu = self.condition_menu["menu"]
        menu.delete(0, tk.END)

        for condition in conditions.get(alert_type, []):
            menu.add_command(label=condition,
                             command=lambda value=condition: self.condition_var.set(value))

        self.condition_var.set(conditions[alert_type][0])

    def create_alert(self):
        """יצירת התראה חדשה"""
        try:
            symbol = self.symbol_entry.get().strip()
            if not symbol:
                raise ValueError("נא להזין סימול מניה")

            alert_type = self.alert_type_var.get()
            condition = self.condition_var.get()

            try:
                value = float(self.value_entry.get())
            except ValueError:
                raise ValueError("נא להזין ערך מספרי תקין")

            # יצירת התראה
            alert = StockAlert(
                symbol=symbol,
                condition=condition,
                target_value=value,
                current_value=0,  # יעודכן בהמשך
                alert_type=alert_type,
                created_at=datetime.now()
            )

            # שמירת ההתראה
            if symbol not in self.alerts:
                self.alerts[symbol] = []
            self.alerts[symbol].append(alert)

            # הוספה לטבלת התראות פעילות
            self.active_tree.insert("", tk.END, values=(
                symbol,
                alert_type,
                condition,
                f"{value:.2f}",
                alert.created_at.strftime("%Y-%m-%d %H:%M")
            ))

            # ניקוי שדות
            self.symbol_entry.delete(0, tk.END)
            self.value_entry.delete(0, tk.END)

            messagebox.showinfo("הצלחה", "ההתראה נוצרה בהצלחה")
            self.logger.info(f"Created alert for {symbol}: {alert_type} {condition} {value}")

        except Exception as e:
            messagebox.showerror("שגיאה", str(e))
            self.logger.error(f"Error creating alert: {str(e)}")

    def remove_alert(self):
        """הסרת התראה נבחרת"""
        selection = self.active_tree.selection()
        if not selection:
            messagebox.showwarning("שגיאה", "נא לבחור התראה להסרה")
            return

        item = selection[0]
        values = self.active_tree.item(item)['values']
        symbol = values[0]

        # הסרה מהמילון
        if symbol in self.alerts:
            # מוצאים את ההתראה המתאימה לפי הערכים
            for alert in self.alerts[symbol]:
                if (alert.alert_type == values[1] and
                        alert.condition == values[2] and
                        float(alert.target_value) == float(values[3])):
                    self.alerts[symbol].remove(alert)
                    break

        # הסרה מהטבלה
        self.active_tree.delete(item)
        self.logger.info(f"Removed alert for {symbol}")

    def check_alerts(self, symbol: str, current_price: float, current_volume: float,
                     rsi: float = None, macd: float = None):
        """בדיקת התראות עבור מניה מסוימת"""
        if symbol not in self.alerts:
            return

        triggered_alerts = []
        remaining_alerts = []

        for alert in self.alerts[symbol]:
            is_triggered = False

            if alert.alert_type == "price":
                is_triggered = (alert.condition == "above" and current_price > alert.target_value) or \
                               (alert.condition == "below" and current_price < alert.target_value)

            elif alert.alert_type == "volume":
                is_triggered = current_volume > alert.target_value

            elif alert.alert_type == "rsi" and rsi is not None:
                is_triggered = (alert.condition == "above" and rsi > alert.target_value) or \
                               (alert.condition == "below" and rsi < alert.target_value)

            elif alert.alert_type == "macd" and macd is not None:
                is_triggered = (alert.condition == "crossover" and macd > 0) or \
                               (alert.condition == "crossunder" and macd < 0)

            if is_triggered:
                triggered_alerts.append(alert)
                # העברה להיסטוריה
                self.add_to_history(alert)
            else:
                remaining_alerts.append(alert)

        # עדכון רשימת ההתראות
        self.alerts[symbol] = remaining_alerts

        # עדכון טבלת התראות פעילות
        self.update_active_alerts()

        return triggered_alerts

    def add_to_history(self, alert: StockAlert):
        """הוספת התראה להיסטוריה"""
        self.history_tree.insert("", 0, values=(
            alert.symbol,
            alert.alert_type,
            alert.condition,
            f"{alert.target_value:.2f}",
            datetime.now().strftime("%Y-%m-%d %H:%M")
        ))

    def update_active_alerts(self):
        """עדכון טבלת התראות פעילות"""
        # ניקוי טבלה
        for item in self.active_tree.get_children():
            self.active_tree.delete(item)

        # הוספת כל ההתראות הפעילות
        for symbol, alerts in self.alerts.items():
            for alert in alerts:
                self.active_tree.insert("", tk.END, values=(
                    symbol,
                    alert.alert_type,
                    alert.condition,
                    f"{alert.target_value:.2f}",
                    alert.created_at.strftime("%Y-%m-%d %H:%M")
                ))

    def save_alerts(self, filename: str):
        """שמירת התראות לקובץ"""
        try:
            data = []
            for symbol, alerts in self.alerts.items():
                for alert in alerts:
                    data.append({
                        'symbol': alert.symbol,
                        'type': alert.alert_type,
                        'condition': alert.condition,
                        'value': alert.target_value,
                        'created': alert.created_at.isoformat()
                    })

            pd.DataFrame(data).to_csv(filename, index=False)
            self.logger.info(f"Saved alerts to {filename}")

        except Exception as e:
            self.logger.error(f"Error saving alerts: {str(e)}")
            raise

    def load_alerts(self, filename: str):
        """טעינת התראות מקובץ"""
        try:
            df = pd.read_csv(filename)
            self.alerts.clear()

            for _, row in df.iterrows():
                alert = StockAlert(
                    symbol=row['symbol'],
                    alert_type=row['type'],
                    condition=row['condition'],
                    target_value=float(row['value']),
                    current_value=0,
                    created_at=datetime.fromisoformat(row['created'])
                )

                if alert.symbol not in self.alerts:
                    self.alerts[alert.symbol] = []
                self.alerts[alert.symbol].append(alert)

            self.update_active_alerts()
            self.logger.info(f"Loaded alerts from {filename}")

        except Exception as e:
            self.logger.error(f"Error loading alerts: {str(e)}")
            raise