from database.db import execute_query, fetch_query, fetch_one
from datetime import datetime

class StockService:
    @staticmethod
    def get_item_stock(item_id):
        result = fetch_one("""
            SELECT quantity, weight_in_gm FROM items WHERE id = ?
        """, (item_id,))
        return {'quantity': result[0] if result else 0, 'weight': result[1] if result else 0}
    
    @staticmethod
    def add_stock(item_id, quantity, weight_in_gm=0, reference="", reason="", adjusted_by="System"):
        current = StockService.get_item_stock(item_id)
        new_qty = current['quantity'] + quantity
        new_weight = current['weight'] + weight_in_gm
        
        execute_query("""
            INSERT INTO stock_movements (item_id, transaction_type, quantity_change, weight_change,
                                         previous_quantity, new_quantity, previous_weight, new_weight,
                                         reference, reason, adjusted_by, date_created)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (item_id, 'IN', quantity, weight_in_gm, current['quantity'], new_qty, 
              current['weight'], new_weight, reference, reason, adjusted_by, datetime.now()))
        
        execute_query("""
            UPDATE items SET quantity = ?, weight_in_gm = ?, date_modified = ? WHERE id = ?
        """, (new_qty, new_weight, datetime.now(), item_id))
        
        StockService.sync_inventory(item_id)
        return new_qty
    
    @staticmethod
    def remove_stock(item_id, quantity, weight_in_gm=0, reference="", reason="", adjusted_by="System"):
        current = StockService.get_item_stock(item_id)
        new_qty = max(0, current['quantity'] - quantity)
        new_weight = max(0, current['weight'] - weight_in_gm)
        
        execute_query("""
            INSERT INTO stock_movements (item_id, transaction_type, quantity_change, weight_change,
                                         previous_quantity, new_quantity, previous_weight, new_weight,
                                         reference, reason, adjusted_by, date_created)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (item_id, 'OUT', -quantity, -weight_in_gm, current['quantity'], new_qty, 
              current['weight'], new_weight, reference, reason, adjusted_by, datetime.now()))
        
        execute_query("""
            UPDATE items SET quantity = ?, weight_in_gm = ?, date_modified = ? WHERE id = ?
        """, (new_qty, new_weight, datetime.now(), item_id))
        
        StockService.sync_inventory(item_id)
        return new_qty
    
    @staticmethod
    def adjust_stock(item_id, new_quantity, new_weight=None, reason="Manual Adjustment", adjusted_by="Admin"):
        current = StockService.get_item_stock(item_id)
        qty_change = new_quantity - current['quantity']
        
        if new_weight is None:
            new_weight = current['weight']
        weight_change = new_weight - current['weight']
        
        transaction_type = 'ADJUSTMENT'
        if qty_change > 0:
            transaction_type = 'ADJUSTMENT_IN'
        elif qty_change < 0:
            transaction_type = 'ADJUSTMENT_OUT'
        
        execute_query("""
            INSERT INTO stock_movements (item_id, transaction_type, quantity_change, weight_change,
                                         previous_quantity, new_quantity, previous_weight, new_weight,
                                         reference, reason, adjusted_by, date_created)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (item_id, transaction_type, qty_change, weight_change, current['quantity'], new_quantity, 
              current['weight'], new_weight, 'Manual Stock Adjustment', reason, adjusted_by, datetime.now()))
        
        execute_query("""
            UPDATE items SET quantity = ?, weight_in_gm = ?, date_modified = ? WHERE id = ?
        """, (new_quantity, new_weight, datetime.now(), item_id))
        
        StockService.sync_inventory(item_id)
        return new_quantity
    
    @staticmethod
    def sync_inventory(item_id):
        item = fetch_one("SELECT quantity, weight_in_gm FROM items WHERE id = ?", (item_id,))
        if not item:
            return
        
        existing = fetch_one("SELECT id FROM inventory WHERE item_id = ?", (item_id,))
        if existing:
            execute_query("""
                UPDATE inventory SET quantity = ?, weight_in_gm = ?, last_updated = ? WHERE item_id = ?
            """, (item[0], item[1], datetime.now(), item_id))
        else:
            execute_query("""
                INSERT INTO inventory (item_id, quantity, weight_in_gm, last_updated)
                VALUES (?, ?, ?, ?)
            """, (item_id, item[0], item[1], datetime.now()))
    
    @staticmethod
    def get_current_stock(item_id):
        result = fetch_one("""
            SELECT quantity, weight_in_gm FROM items WHERE id = ?
        """, (item_id,))
        return result if result else (0, 0)
    
    @staticmethod
    def get_stock_report():
        return fetch_query("""
            SELECT i.id, i.name, COALESCE(ic.name, 'Uncategorized'), i.quantity, 
                   i.weight_in_gm, i.price, (i.quantity * i.price) as total_value,
                   COALESCE(m.name, 'N/A') as material
            FROM items i
            LEFT JOIN item_categories ic ON i.category_id = ic.id
            LEFT JOIN materials m ON i.material_id = m.id
            WHERE i.is_active = 1
            ORDER BY i.name
        """)
    
    @staticmethod
    def get_stock_movements(item_id=None, limit=100):
        if item_id:
            return fetch_query("""
                SELECT sm.id, i.name, sm.transaction_type, sm.quantity_change, sm.weight_change,
                       sm.previous_quantity, sm.new_quantity, sm.reason, sm.adjusted_by, sm.date_created
                FROM stock_movements sm
                JOIN items i ON sm.item_id = i.id
                WHERE sm.item_id = ?
                ORDER BY sm.date_created DESC
                LIMIT ?
            """, (item_id, limit))
        else:
            return fetch_query("""
                SELECT sm.id, i.name, sm.transaction_type, sm.quantity_change, sm.weight_change,
                       sm.previous_quantity, sm.new_quantity, sm.reason, sm.adjusted_by, sm.date_created
                FROM stock_movements sm
                JOIN items i ON sm.item_id = i.id
                ORDER BY sm.date_created DESC
                LIMIT ?
            """, (limit,))
    
    @staticmethod
    def get_low_stock_items(threshold=5):
        return fetch_query("""
            SELECT i.id, i.name, i.quantity, i.weight_in_gm, COALESCE(ic.name, 'N/A') as category
            FROM items i
            LEFT JOIN item_categories ic ON i.category_id = ic.id
            WHERE i.is_active = 1 AND i.quantity <= ?
            ORDER BY i.quantity ASC
        """, (threshold,))
    
    @staticmethod
    def get_stock_valuation():
        gold_value = fetch_one("""
            SELECT COALESCE(SUM(quantity * price), 0), COALESCE(SUM(weight_in_gm), 0)
            FROM items i
            JOIN materials m ON i.material_id = m.id
            WHERE i.is_active = 1 AND m.name = 'Gold'
        """)
        
        diamond_value = fetch_one("""
            SELECT COALESCE(SUM(quantity * price), 0), COALESCE(SUM(diamond_carat), 0)
            FROM items i
            JOIN materials m ON i.material_id = m.id
            WHERE i.is_active = 1 AND m.name = 'Diamond'
        """)
        
        total_value = fetch_one("""
            SELECT COALESCE(SUM(quantity * price), 0) FROM items WHERE is_active = 1
        """)
        
        return {
            'gold_value': gold_value[0] if gold_value else 0,
            'gold_weight': gold_value[1] if gold_value else 0,
            'diamond_value': diamond_value[0] if diamond_value else 0,
            'diamond_carat': diamond_value[1] if diamond_value else 0,
            'total_value': total_value[0] if total_value else 0
        }
