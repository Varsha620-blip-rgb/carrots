from database.db import execute_query, fetch_query, fetch_one
from datetime import datetime

class StockService:
    @staticmethod
    def add_stock(item_id, quantity, weight_in_gm=0, reference=""):
        execute_query("""
            INSERT INTO stock_movements (item_id, transaction_type, quantity_change, weight_change, reference, date_created)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (item_id, 'IN', quantity, weight_in_gm, reference, datetime.now()))
        
        execute_query("""
            UPDATE inventory
            SET quantity = quantity + ?, weight_in_gm = weight_in_gm + ?, last_updated = ?
            WHERE item_id = ?
        """, (quantity, weight_in_gm, datetime.now(), item_id))
    
    @staticmethod
    def remove_stock(item_id, quantity, weight_in_gm=0, reference=""):
        execute_query("""
            INSERT INTO stock_movements (item_id, transaction_type, quantity_change, weight_change, reference, date_created)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (item_id, 'OUT', -quantity, -weight_in_gm, reference, datetime.now()))
        
        execute_query("""
            UPDATE inventory
            SET quantity = quantity - ?, weight_in_gm = weight_in_gm - ?, last_updated = ?
            WHERE item_id = ?
        """, (quantity, weight_in_gm, datetime.now(), item_id))
    
    @staticmethod
    def get_current_stock(item_id):
        result = fetch_one("""
            SELECT quantity, weight_in_gm
            FROM inventory
            WHERE item_id = ?
        """, (item_id,))
        return result if result else (0, 0)
    
    @staticmethod
    def get_stock_report():
        return fetch_query("""
            SELECT i.id, i.name, ic.name, inv.quantity, inv.weight_in_gm, i.price, (inv.quantity * i.price) as total_value
            FROM items i
            LEFT JOIN item_categories ic ON i.category_id = ic.id
            LEFT JOIN inventory inv ON i.id = inv.item_id
            WHERE i.is_active = 1
            ORDER BY i.name
        """)