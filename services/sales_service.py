from database.db import execute_query, fetch_query, fetch_one
from datetime import datetime
import uuid

class SalesService:
    @staticmethod
    def create_sales_bill(customer_id, employee_id, items, discount=0, notes=""):
        bill_number = f"SB-{datetime.now().strftime('%Y%m%d')}-{uuid.uuid4().hex[:6].upper()}"
        total_amount = sum(item['quantity'] * item['unit_price'] for item in items)
        total_weight = sum(item.get('weight', 0) for item in items)
        
        bill_id = execute_query("""
            INSERT INTO bills (bill_number, bill_type, customer_id, employee_id, bill_date, total_amount, total_weight, discount_amount, status, date_created, date_modified)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            bill_number, 'Sales', customer_id, employee_id, datetime.now().date(),
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
    def get_sales_report(start_date=None, end_date=None):
        query = """
            SELECT b.bill_number, c.name, b.bill_date, b.total_amount, b.status
            FROM bills b
            JOIN customers c ON b.customer_id = c.id
            WHERE b.bill_type = 'Sales'
        """
        
        if start_date and end_date:
            query += f" AND b.bill_date BETWEEN '{start_date}' AND '{end_date}'"
        
        query += " ORDER BY b.bill_date DESC"
        return fetch_query(query)