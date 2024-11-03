import pandas as pd
from pathlib import Path
import json
from datetime import datetime
import logging
from ..config.settings import EXPORT_DIR


class ExportManager:
    def __init__(self):
        self.export_dir = EXPORT_DIR
        self.export_dir.mkdir(parents=True, exist_ok=True)
        self.logger = logging.getLogger(__name__)

    def export_to_excel(self, data: dict, filename: str):
        """ייצוא נתונים לאקסל"""
        try:
            filepath = self.export_dir / filename
            with pd.ExcelWriter(filepath) as writer:
                for sheet_name, sheet_data in data.items():
                    if isinstance(sheet_data, pd.DataFrame):
                        sheet_data.to_excel(writer, sheet_name=sheet_name)
                    else:
                        pd.DataFrame(sheet_data).to_excel(writer, sheet_name=sheet_name)

            self.logger.info(f"Successfully exported data to {filepath}")
            return filepath

        except Exception as e:
            self.logger.error(f"Error exporting to Excel: {str(e)}")
            raise

    def export_to_json(self, data: dict, filename: str):
        """ייצוא נתונים ל-JSON"""
        try:
            filepath = self.export_dir / filename
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=4)

            self.logger.info(f"Successfully exported data to {filepath}")
            return filepath

        except Exception as e:
            self.logger.error(f"Error exporting to JSON: {str(e)}")
            raise

    def export_to_csv(self, data: pd.DataFrame, filename: str):
        """ייצוא נתונים ל-CSV"""
        try:
            filepath = self.export_dir / filename
            data.to_csv(filepath, index=True, encoding='utf-8-sig')

            self.logger.info(f"Successfully exported data to {filepath}")
            return filepath

        except Exception as e:
            self.logger.error(f"Error exporting to CSV: {str(e)}")
            raise

    def create_analysis_report(self, analysis_data: dict, include_charts: bool = True):
        """יצירת דוח ניתוח מפורט"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # ייצוא לאקסל
        excel_data = {
            'Summary': pd.DataFrame([analysis_data['summary']]),
            'Technical': pd.DataFrame(analysis_data.get('technical_data', {})),
            'Fundamental': pd.DataFrame(analysis_data.get('fundamental_data', {})),
            'Risk': pd.DataFrame(analysis_data.get('risk_metrics', {}))
        }

        excel_path = self.export_to_excel(
            excel_data,
            f"analysis_report_{timestamp}.xlsx"
        )

        # ייצוא ל-JSON
        json_path = self.export_to_json(
            analysis_data,
            f"analysis_report_{timestamp}.json"
        )

        return {
            'excel_report': excel_path,
            'json_report': json_path
        }

    def cleanup_old_exports(self, days: int = 30):
        """ניקוי קבצי ייצוא ישנים"""
        try:
            current_time = datetime.now()
            for filepath in self.export_dir.glob('*'):
                file_age = datetime.fromtimestamp(filepath.stat().st_mtime)
                if (current_time - file_age).days > days:
                    filepath.unlink()
                    self.logger.info(f"Deleted old export file: {filepath}")

        except Exception as e:
            self.logger.error(f"Error cleaning up exports: {str(e)}")