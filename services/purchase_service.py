from database.db import execute_query, fetch_query, fetch_one
from datetime import datetime
import uuid

class PurchaseService:
    @staticmethod
    def create_purchase_bill(supplier_id, employee_id, items, discount=0, notes=""):
        bill_number = f"PB-{datetime.now().strftime('%Y%m%d')}-{uuid.uuid4().hex[:6].upper()}"
        total_amount = sum(item['quantity'] * item['unit_price'] for item in items)
        total_weight = sum(item.get('weight', 0) for item in items)
        
        bill_id = execute_query("""
            INSERT INTO bills (bill_number, bill_type, supplier_id, employee_id, bill_date, total_amount, total_weight, discount_amount, status, date_created, date_modified)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            bill_number, 'Purchase', supplier_id, employee_id, datetime.now().date(),
            total_amount - discount, total_weight, discount, 'Completed',
            datetime.now(), datetime.now()
        ))
        
        for item in items:
            execute_query("""
                INSERT INTO bill_items (bill_id, item_id, quantity, unit_price, line_total, weight_in_gm)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                bill_id, item['item_id'], item['quantity'], item['unit_price'],
                item['quantity'] * item['unit_price'], item.get('weight', 0)
            ))
        
        return bill_id, bill_number
    
    @staticmethod
    def get_purchase_report(start_date=None, end_date=None):
        query = """
            SELECT b.bill_number, s.name, b.bill_date, b.total_amount, b.status
            FROM bills b
            JOIN suppliers s ON b.supplier_id = s.id
            WHERE b.bill_type = 'Purchase'
        """
        
        if start_date and end_date:
            query += f" AND b.bill_date BETWEEN '{start_date}' AND '{end_date}'"
        
        query += " ORDER BY b.bill_date DESC"
        return fetch_query(query)