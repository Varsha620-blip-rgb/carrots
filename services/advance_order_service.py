from database.db import execute_query, fetch_query, fetch_one
from datetime import datetime, date
import uuid

class AdvanceOrderService:
    STATUSES = ['Pending', 'In Progress', 'Ready', 'Delivered', 'Cancelled']
    PRIORITIES = ['Low', 'Normal', 'High', 'Urgent']
    ORDER_TYPES = ['Custom', 'Repair', 'Modification', 'Special Order', 'Bulk Order']
    
    @staticmethod
    def create_order(customer_id, employee_id, order_type, material_type, 
                    estimated_weight, estimated_amount, advance_amount,
                    expected_delivery_date, specifications, design_notes="",
                    gold_rate_locked=0, diamond_rate_locked=0, priority='Normal',
                    assigned_artisan=None, remarks=""):
        
        order_number = f"AO-{datetime.now().strftime('%Y%m%d')}-{uuid.uuid4().hex[:6].upper()}"
        balance_amount = estimated_amount - advance_amount
        
        order_id = execute_query("""
            INSERT INTO advance_orders (order_number, customer_id, employee_id, order_date,
                                       expected_delivery_date, order_type, material_type,
                                       estimated_weight, estimated_amount, advance_amount,
                                       balance_amount, gold_rate_locked, diamond_rate_locked,
                                       specifications, design_notes, status, priority,
                                       assigned_artisan, remarks, date_created, date_modified)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (order_number, customer_id, employee_id, date.today(),
              expected_delivery_date, order_type, material_type,
              estimated_weight, estimated_amount, advance_amount,
              balance_amount, gold_rate_locked, diamond_rate_locked,
              specifications, design_notes, 'Pending', priority,
              assigned_artisan, remarks, datetime.now(), datetime.now()))
        
        return order_id, order_number
    
    @staticmethod
    def add_order_item(order_id, item_type, description, material_type,
                      estimated_weight=0, estimated_diamond_carat=0, purity=None,
                      estimated_price=0, design_reference=None, remarks=""):
        
        return execute_query("""
            INSERT INTO advance_order_items (order_id, item_type, description, material_type,
                                            estimated_weight, estimated_diamond_carat, purity,
                                            estimated_price, design_reference, remarks)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (order_id, item_type, description, material_type,
              estimated_weight, estimated_diamond_carat, purity,
              estimated_price, design_reference, remarks))
    
    @staticmethod
    def update_order_status(order_id, new_status, remarks=None):
        execute_query("""
            UPDATE advance_orders 
            SET status = ?, remarks = COALESCE(?, remarks), date_modified = ?
            WHERE id = ?
        """, (new_status, remarks, datetime.now(), order_id))
    
    @staticmethod
    def update_order(order_id, **kwargs):
        allowed_fields = ['expected_delivery_date', 'estimated_amount', 'advance_amount',
                         'final_amount', 'balance_amount', 'specifications', 'design_notes',
                         'priority', 'assigned_artisan', 'remarks', 'status']
        
        updates = []
        values = []
        for field, value in kwargs.items():
            if field in allowed_fields:
                updates.append(f"{field} = ?")
                values.append(value)
        
        if updates:
            values.append(datetime.now())
            values.append(order_id)
            execute_query(f"""
                UPDATE advance_orders 
                SET {', '.join(updates)}, date_modified = ?
                WHERE id = ?
            """, tuple(values))
    
    @staticmethod
    def mark_delivered(order_id, final_amount, bill_id=None):
        balance = final_amount - (fetch_one("SELECT advance_amount FROM advance_orders WHERE id = ?", (order_id,))[0] or 0)
        execute_query("""
            UPDATE advance_orders 
            SET status = 'Delivered', actual_delivery_date = ?, final_amount = ?, 
                balance_amount = ?, bill_id = ?, date_modified = ?
            WHERE id = ?
        """, (date.today(), final_amount, balance, bill_id, datetime.now(), order_id))
    
    @staticmethod
    def get_order(order_id):
        return fetch_one("""
            SELECT ao.*, c.name as customer_name, c.phone as customer_phone,
                   e.name as employee_name
            FROM advance_orders ao
            JOIN customers c ON ao.customer_id = c.id
            LEFT JOIN employees e ON ao.employee_id = e.id
            WHERE ao.id = ?
        """, (order_id,))
    
    @staticmethod
    def get_order_items(order_id):
        return fetch_query("""
            SELECT * FROM advance_order_items WHERE order_id = ?
        """, (order_id,))
    
    @staticmethod
    def get_all_orders(status=None, limit=100):
        if status and status != 'All':
            return fetch_query("""
                SELECT ao.id, ao.order_number, c.name as customer_name, ao.order_date,
                       ao.expected_delivery_date, ao.material_type, ao.estimated_amount,
                       ao.advance_amount, ao.status, ao.priority
                FROM advance_orders ao
                JOIN customers c ON ao.customer_id = c.id
                WHERE ao.status = ?
                ORDER BY ao.order_date DESC
                LIMIT ?
            """, (status, limit))
        else:
            return fetch_query("""
                SELECT ao.id, ao.order_number, c.name as customer_name, ao.order_date,
                       ao.expected_delivery_date, ao.material_type, ao.estimated_amount,
                       ao.advance_amount, ao.status, ao.priority
                FROM advance_orders ao
                JOIN customers c ON ao.customer_id = c.id
                ORDER BY ao.order_date DESC
                LIMIT ?
            """, (limit,))
    
    @staticmethod
    def get_pending_orders():
        return fetch_query("""
            SELECT ao.id, ao.order_number, c.name as customer_name, ao.expected_delivery_date,
                   ao.material_type, ao.estimated_amount, ao.priority
            FROM advance_orders ao
            JOIN customers c ON ao.customer_id = c.id
            WHERE ao.status IN ('Pending', 'In Progress')
            ORDER BY ao.expected_delivery_date ASC
        """)
    
    @staticmethod
    def get_overdue_orders():
        return fetch_query("""
            SELECT ao.id, ao.order_number, c.name as customer_name, c.phone,
                   ao.expected_delivery_date, ao.material_type, ao.estimated_amount, ao.status
            FROM advance_orders ao
            JOIN customers c ON ao.customer_id = c.id
            WHERE ao.status IN ('Pending', 'In Progress') 
                  AND ao.expected_delivery_date < ?
            ORDER BY ao.expected_delivery_date ASC
        """, (date.today(),))
    
    @staticmethod
    def get_customer_orders(customer_id, include_completed=False):
        if include_completed:
            return fetch_query("""
                SELECT ao.id, ao.order_number, ao.order_date, ao.expected_delivery_date,
                       ao.material_type, ao.estimated_amount, ao.advance_amount, ao.status
                FROM advance_orders ao
                WHERE ao.customer_id = ?
                ORDER BY ao.order_date DESC
            """, (customer_id,))
        else:
            return fetch_query("""
                SELECT ao.id, ao.order_number, ao.order_date, ao.expected_delivery_date,
                       ao.material_type, ao.estimated_amount, ao.advance_amount, ao.status
                FROM advance_orders ao
                WHERE ao.customer_id = ? AND ao.status NOT IN ('Delivered', 'Cancelled')
                ORDER BY ao.order_date DESC
            """, (customer_id,))
    
    @staticmethod
    def cancel_order(order_id, reason=""):
        execute_query("""
            UPDATE advance_orders 
            SET status = 'Cancelled', remarks = ?, date_modified = ?
            WHERE id = ?
        """, (reason, datetime.now(), order_id))
    
    @staticmethod
    def delete_order(order_id):
        execute_query("DELETE FROM advance_order_items WHERE order_id = ?", (order_id,))
        execute_query("DELETE FROM advance_orders WHERE id = ?", (order_id,))
    
    @staticmethod
    def get_orders_summary():
        pending = fetch_one("SELECT COUNT(*) FROM advance_orders WHERE status = 'Pending'")[0]
        in_progress = fetch_one("SELECT COUNT(*) FROM advance_orders WHERE status = 'In Progress'")[0]
        ready = fetch_one("SELECT COUNT(*) FROM advance_orders WHERE status = 'Ready'")[0]
        overdue = fetch_one("""
            SELECT COUNT(*) FROM advance_orders 
            WHERE status IN ('Pending', 'In Progress') AND expected_delivery_date < ?
        """, (date.today(),))[0]
        
        total_advance = fetch_one("""
            SELECT COALESCE(SUM(advance_amount), 0) FROM advance_orders 
            WHERE status NOT IN ('Delivered', 'Cancelled')
        """)[0]
        
        return {
            'pending': pending,
            'in_progress': in_progress,
            'ready': ready,
            'overdue': overdue,
            'total_advance_collected': total_advance
        }
