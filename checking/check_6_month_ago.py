from advanced_stock_analyzer import AdvancedStockAnalyzer
from datetime import datetime, timedelta


def backtest_with_our_algorithm(symbol, months_back=12):
    """
    בדיקת ביצועים של האלגוריתם שלנו
    """
    try:
        # המרת חודשים לתקופה תקינה
        period = "1y" if months_back <= 12 else "2y" if months_back <= 24 else "5y"
        print(f"מושך נתונים לתקופה של {period}...")

        # אתחול האנלייזר
        market_index = "^TA125.TA" if '.TA' in symbol else "^GSPC"
        analyzer = AdvancedStockAnalyzer(symbol, market_index)
        analyzer.fetch_data(period=period)

        trades = []
        position = None
        entry_price = 0

        print("מנתח את הנתונים...")

        # נדפיס את ההמלצות הראשונות לדיבוג
        print("\nבדיקת המלצות ראשונות:")
        for i in range(20, min(25, len(analyzer.hist))):
            data_until_now = analyzer.hist.iloc[:i + 1]
            temp_analyzer = AdvancedStockAnalyzer(symbol, market_index)
            temp_analyzer.hist = data_until_now.copy()
            temp_analyzer.market_hist = analyzer.market_hist.loc[:data_until_now.index[-1]].copy()
            analysis = temp_analyzer.run_analysis()
            print(f"תאריך: {data_until_now.index[-1]}, המלצה: {analysis['המלצה']}, ציון: {analysis['ציון_סופי']:.2f}")

        # עובר על כל יום מסחר
        for i in range(20, len(analyzer.hist)):
            current_date = analyzer.hist.index[i]
            current_price = analyzer.hist['Close'].iloc[i]

            # מנתח כל 5 ימי מסחר
            if i % 5 == 0:
                data_until_now = analyzer.hist.iloc[:i + 1]
                temp_analyzer = AdvancedStockAnalyzer(symbol, market_index)
                temp_analyzer.hist = data_until_now.copy()
                temp_analyzer.market_hist = analyzer.market_hist.loc[:data_until_now.index[-1]].copy()
                analysis = temp_analyzer.run_analysis()

                # החלטות מסחר
                if position is None:  # אם אין פוזיציה פתוחה
                    if analysis['המלצה'] in ["קנייה חזקה", "קנייה"] or analysis['ציון_סופי'] > 0.6:
                        position = "LONG"
                        entry_price = current_price
                        trades.append({
                            'date': current_date,
                            'action': 'ENTER',
                            'price': current_price,
                            'recommendation': analysis['המלצה'],
                            'score': analysis['ציון_סופי']
                        })
                        print(
                            f"\nכניסה לפוזיציה: מחיר {current_price:.2f}, המלצה: {analysis['המלצה']}, ציון: {analysis['ציון_סופי']:.2f}")

                elif position == "LONG":  # אם יש פוזיציה פתוחה
                    # בדיקת תנאי יציאה
                    current_return = (current_price / entry_price - 1) * 100
                    exit_conditions = [
                        analysis['המלצה'] == "מכירה",
                        analysis['ציון_סופי'] < 0.4,
                        current_return <= -5,  # הפסד של 5%
                        current_return >= 15  # רווח של 15%
                    ]
                    exit_reasons = [
                        "המלצת מכירה",
                        "ציון נמוך",
                        "הפסד מקסימלי",
                        "מימוש רווח"
                    ]

                    for condition, reason in zip(exit_conditions, exit_reasons):
                        if condition:
                            returns = current_return
                            position = None
                            trades.append({
                                'date': current_date,
                                'action': 'EXIT',
                                'price': current_price,
                                'returns': returns,
                                'recommendation': analysis['המלצה'],
                                'score': analysis['ציון_סופי'],
                                'reason': reason
                            })
                            print(f"\nיציאה מפוזיציה: מחיר {current_price:.2f}, תשואה {returns:.2f}%, סיבה: {reason}")
                            break

        print("\nמחשב סטטיסטיקות סופיות...")

        # חישוב סטטיסטיקות
        buy_and_hold_return = ((analyzer.hist['Close'].iloc[-1] / analyzer.hist['Close'].iloc[0]) - 1) * 100
        system_returns = [trade['returns'] for trade in trades if 'returns' in trade]
        total_system_return = sum(system_returns) if system_returns else 0

        results = {
            'תקופה': f"{months_back} חודשים",
            'תשואת Buy & Hold': f"{buy_and_hold_return:.2f}%",
            'תשואת האלגוריתם': f"{total_system_return:.2f}%",
            'מספר עסקאות': len(system_returns),
            'תשואה ממוצעת לעסקה': f"{(total_system_return / len(system_returns)):.2f}%" if system_returns else "אין עסקאות",
            'עסקאות מפורטות': trades
        }

        # הדפסת סיכום מפורט
        print("\nסיכום עסקאות:")
        for trade in trades:
            if trade['action'] == 'ENTER':
                print(f"\nכניסה בתאריך {trade['date']}")
                print(f"מחיר: {trade['price']:.2f}")
                print(f"המלצה: {trade['recommendation']}")
                print(f"ציון: {trade['score']:.2f}")
            else:
                print(f"\nיציאה בתאריך {trade['date']}")
                print(f"מחיר: {trade['price']:.2f}")
                print(f"תשואה: {trade['returns']:.2f}%")
                print(f"סיבה: {trade.get('reason', 'לא צוין')}")

        return results

    except Exception as e:
        print(f"שגיאה בבדיקת הביצועים: {str(e)}")
        return None

symbol = "TEVA.TA"

print(backtest_with_our_algorithm(symbol=symbol))