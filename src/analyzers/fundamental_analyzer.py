import numpy as np
import pandas as pd
from typing import Dict, Optional


class FundamentalIndicators:
    @staticmethod
    def calculate_pe_ratio(price: float, eps: float) -> float:
        """חישוב מכפיל רווח"""
        return price / eps if eps != 0 else np.inf

    @staticmethod
    def calculate_pb_ratio(price: float, book_value: float) -> float:
        """חישוב מכפיל הון"""
        return price / book_value if book_value != 0 else np.inf

    @staticmethod
    def calculate_ps_ratio(price: float, sales_per_share: float) -> float:
        """חישוב מכפיל מכירות"""
        return price / sales_per_share if sales_per_share != 0 else np.inf

    @staticmethod
    def calculate_peg_ratio(pe_ratio: float, growth_rate: float) -> float:
        """חישוב מכפיל PEG"""
        return pe_ratio / growth_rate if growth_rate != 0 else np.inf

    @staticmethod
    def calculate_dividend_yield(dividend_per_share: float, price: float) -> float:
        """חישוב תשואת דיבידנד"""
        return (dividend_per_share / price) * 100 if price != 0 else 0

    @staticmethod
    def calculate_return_on_equity(net_income: float, shareholder_equity: float) -> float:
        """חישוב תשואה על ההון"""
        return (net_income / shareholder_equity) * 100 if shareholder_equity != 0 else 0

    @staticmethod
    def calculate_debt_to_equity(total_debt: float, shareholder_equity: float) -> float:
        """חישוב יחס חוב להון"""
        return total_debt / shareholder_equity if shareholder_equity != 0 else np.inf

    @staticmethod
    def calculate_current_ratio(current_assets: float, current_liabilities: float) -> float:
        """חישוב יחס שוטף"""
        return current_assets / current_liabilities if current_liabilities != 0 else np.inf

    @staticmethod
    def calculate_quick_ratio(current_assets: float, inventory: float, current_liabilities: float) -> float:
        """חישוב יחס מהיר"""
        return (current_assets - inventory) / current_liabilities if current_liabilities != 0 else np.inf

    @staticmethod
    def calculate_profit_margin(net_income: float, revenue: float) -> float:
        """חישוב שולי רווח נקי"""
        return (net_income / revenue) * 100 if revenue != 0 else 0

    @staticmethod
    def calculate_growth_rate(current_value: float, previous_value: float) -> float:
        """חישוב שיעור צמיחה"""
        return ((current_value / previous_value) - 1) * 100 if previous_value != 0 else np.inf

    @staticmethod
    def analyze_fundamentals(financial_data: Dict) -> Dict:
        """ניתוח פונדמנטלי מקיף"""
        results = {}

        try:
            # חישוב מכפילים
            if all(key in financial_data for key in ['price', 'eps']):
                results['pe_ratio'] = FundamentalIndicators.calculate_pe_ratio(
                    financial_data['price'], financial_data['eps']
                )

            if all(key in financial_data for key in ['price', 'book_value']):
                results['pb_ratio'] = FundamentalIndicators.calculate_pb_ratio(
                    financial_data['price'], financial_data['book_value']
                )

            # חישוב צמיחה
            if all(key in financial_data for key in ['current_revenue', 'previous_revenue']):
                results['revenue_growth'] = FundamentalIndicators.calculate_growth_rate(
                    financial_data['current_revenue'], financial_data['previous_revenue']
                )

            # חישוב רווחיות
            if all(key in financial_data for key in ['net_income', 'revenue']):
                results['profit_margin'] = FundamentalIndicators.calculate_profit_margin(
                    financial_data['net_income'], financial_data['revenue']
                )

            # חישוב יחסי נזילות
            if all(key in financial_data for key in ['current_assets', 'current_liabilities']):
                results['current_ratio'] = FundamentalIndicators.calculate_current_ratio(
                    financial_data['current_assets'], financial_data['current_liabilities']
                )

            # דירוג כולל
            results['overall_score'] = FundamentalIndicators.calculate_overall_score(results)

        except Exception as e:
            print(f"Error in fundamental analysis: {str(e)}")
            results['error'] = str(e)

        return results

    @staticmethod
    def calculate_overall_score(metrics: Dict) -> float:
        """חישוב ציון כולל למניה"""
        scores = []
        weights = {
            'pe_ratio': 0.2,
            'pb_ratio': 0.15,
            'profit_margin': 0.2,
            'current_ratio': 0.15,
            'revenue_growth': 0.3
        }

        for metric, weight in weights.items():
            if metric not in metrics:
                continue

            value = metrics[metric]

            # חישוב ציון לכל מדד
            if metric == 'pe_ratio':
                score = 1.0 if 0 < value < 15 else 0.5 if 15 <= value < 25 else 0.0
            elif metric == 'pb_ratio':
                score = 1.0 if 0 < value < 3 else 0.5 if 3 <= value < 5 else 0.0
            elif metric == 'profit_margin':
                score = 1.0 if value > 20 else 0.5 if 10 <= value <= 20 else 0.0
            elif metric == 'current_ratio':
                score = 1.0 if value > 2 else 0.5 if 1 <= value <= 2 else 0.0
            elif metric == 'revenue_growth':
                score = 1.0 if value > 20 else 0.5 if 5 <= value <= 20 else 0.0

            scores.append(score * weight)

        return sum(scores) / sum(weights[m] for m in metrics.keys() if m in weights)