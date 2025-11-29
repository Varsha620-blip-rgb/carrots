import csv
from datetime import datetime
from pathlib import Path
from config import EXPORT_PATH

class ExportService:
    @staticmethod
    def export_to_csv(data, filename, headers):
        filepath = EXPORT_PATH / f"{filename}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        
        with open(filepath, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(headers)
            writer.writerows(data)
        
        return filepath
    
    @staticmethod
    def export_stock_report(items):
        headers = ['Item ID', 'Item Name', 'Category', 'Quantity', 'Weight(gm)', 'Price', 'Total Value']
        return ExportService.export_to_csv(items, 'stock_report', headers)
    
    @staticmethod
    def export_sales_report(sales):
        headers = ['Bill Number', 'Customer', 'Date', 'Amount', 'Status']
        return ExportService.export_to_csv(sales, 'sales_report', headers)
    
    @staticmethod
    def export_purchase_report(purchases):
        headers = ['Bill Number', 'Supplier', 'Date', 'Amount', 'Status']
        return ExportService.export_to_csv(purchases, 'purchase_report', headers)