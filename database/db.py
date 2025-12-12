import sqlite3
from datetime import datetime
from pathlib import Path
from config import DATABASE_PATH

def get_connection():
    conn = sqlite3.connect(str(DATABASE_PATH))
    conn.row_factory = sqlite3.Row
    return conn

def create_tables():
    conn = get_connection()
    cursor = conn.cursor()
    
    # Materials table (Gold, Diamond, Silver, Platinum, etc.)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS materials (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL UNIQUE,
        material_type TEXT NOT NULL,
        description TEXT,
        is_active INTEGER DEFAULT 1,
        date_created TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    # Insert default materials if not exist
    cursor.execute("INSERT OR IGNORE INTO materials (name, material_type, description) VALUES ('Gold', 'metal', 'Precious metal - Gold')")
    cursor.execute("INSERT OR IGNORE INTO materials (name, material_type, description) VALUES ('Diamond', 'gemstone', 'Precious gemstone - Diamond')")
    cursor.execute("INSERT OR IGNORE INTO materials (name, material_type, description) VALUES ('Silver', 'metal', 'Precious metal - Silver')")
    cursor.execute("INSERT OR IGNORE INTO materials (name, material_type, description) VALUES ('Platinum', 'metal', 'Precious metal - Platinum')")
    
    # Customers table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS customers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        phone TEXT,
        email TEXT,
        address TEXT,
        city TEXT,
        state TEXT,
        pincode TEXT,
        gst_number TEXT,
        credit_limit REAL DEFAULT 0,
        outstanding_balance REAL DEFAULT 0,
        date_created TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        date_modified TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    # Employees table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS employees (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        phone TEXT,
        email TEXT,
        address TEXT,
        position TEXT,
        salary REAL,
        date_joined DATE,
        status TEXT DEFAULT 'Active',
        date_created TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        date_modified TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    # Suppliers table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS suppliers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        phone TEXT,
        email TEXT,
        address TEXT,
        city TEXT,
        state TEXT,
        pincode TEXT,
        gst_number TEXT,
        supplier_type TEXT DEFAULT 'General',
        date_created TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        date_modified TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    # Item Categories
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS item_categories (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL UNIQUE,
        material_id INTEGER,
        description TEXT,
        date_created TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (material_id) REFERENCES materials(id)
    )
    ''')
    
    # Insert default categories if not exist
    cursor.execute("INSERT OR IGNORE INTO item_categories (name, description) VALUES ('Gold Jewelry', 'Gold jewelry items')")
    cursor.execute("INSERT OR IGNORE INTO item_categories (name, description) VALUES ('Diamond Jewelry', 'Diamond jewelry items')")
    cursor.execute("INSERT OR IGNORE INTO item_categories (name, description) VALUES ('Gold Coins', 'Gold coins and bars')")
    cursor.execute("INSERT OR IGNORE INTO item_categories (name, description) VALUES ('Loose Diamonds', 'Loose diamond stones')")
    cursor.execute("INSERT OR IGNORE INTO item_categories (name, description) VALUES ('Silver Items', 'Silver jewelry and articles')")
    
    # Items table - Enhanced for gold and diamond
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        category_id INTEGER,
        material_id INTEGER,
        item_type TEXT DEFAULT 'finished',
        barcode TEXT UNIQUE,
        price REAL NOT NULL,
        cost_price REAL,
        quantity INTEGER DEFAULT 0,
        weight_in_gm REAL DEFAULT 0,
        purity TEXT,
        making_charges REAL DEFAULT 0,
        making_charges_type TEXT DEFAULT 'per_gram',
        gold_weight REAL DEFAULT 0,
        diamond_weight REAL DEFAULT 0,
        diamond_count INTEGER DEFAULT 0,
        diamond_clarity TEXT,
        diamond_color TEXT,
        diamond_cut TEXT,
        diamond_carat REAL DEFAULT 0,
        diamond_certification TEXT,
        stone_weight REAL DEFAULT 0,
        stone_type TEXT,
        hallmark TEXT,
        hsn_code TEXT,
        description TEXT,
        is_active INTEGER DEFAULT 1,
        date_created TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        date_modified TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (category_id) REFERENCES item_categories(id),
        FOREIGN KEY (material_id) REFERENCES materials(id)
    )
    ''')
    
    # Bills (Invoices) table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS bills (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        bill_number TEXT UNIQUE NOT NULL,
        bill_type TEXT NOT NULL,
        customer_id INTEGER,
        supplier_id INTEGER,
        employee_id INTEGER,
        bill_date DATE NOT NULL,
        total_amount REAL NOT NULL,
        total_weight REAL DEFAULT 0,
        total_gold_weight REAL DEFAULT 0,
        total_diamond_weight REAL DEFAULT 0,
        discount_amount REAL DEFAULT 0,
        tax_amount REAL DEFAULT 0,
        making_charges REAL DEFAULT 0,
        paid_amount REAL DEFAULT 0,
        outstanding_amount REAL DEFAULT 0,
        payment_mode TEXT DEFAULT 'Cash',
        status TEXT DEFAULT 'Pending',
        remarks TEXT,
        date_created TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        date_modified TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (customer_id) REFERENCES customers(id),
        FOREIGN KEY (supplier_id) REFERENCES suppliers(id),
        FOREIGN KEY (employee_id) REFERENCES employees(id)
    )
    ''')
    
    # Bill Items table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS bill_items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        bill_id INTEGER NOT NULL,
        item_id INTEGER NOT NULL,
        quantity REAL NOT NULL,
        unit_price REAL NOT NULL,
        line_total REAL NOT NULL,
        weight_in_gm REAL DEFAULT 0,
        gold_weight REAL DEFAULT 0,
        diamond_weight REAL DEFAULT 0,
        making_charges REAL DEFAULT 0,
        discount REAL DEFAULT 0,
        remarks TEXT,
        FOREIGN KEY (bill_id) REFERENCES bills(id),
        FOREIGN KEY (item_id) REFERENCES items(id)
    )
    ''')
    
    # Inventory/Stock table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS inventory (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        item_id INTEGER NOT NULL UNIQUE,
        quantity INTEGER DEFAULT 0,
        weight_in_gm REAL DEFAULT 0,
        reserved_quantity INTEGER DEFAULT 0,
        min_stock_level INTEGER DEFAULT 0,
        last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (item_id) REFERENCES items(id)
    )
    ''')
    
    # Stock Movements - Enhanced for audit
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS stock_movements (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        item_id INTEGER NOT NULL,
        transaction_type TEXT NOT NULL,
        quantity_change REAL NOT NULL,
        weight_change REAL DEFAULT 0,
        previous_quantity REAL DEFAULT 0,
        new_quantity REAL DEFAULT 0,
        previous_weight REAL DEFAULT 0,
        new_weight REAL DEFAULT 0,
        bill_id INTEGER,
        reference TEXT,
        reason TEXT,
        adjusted_by TEXT,
        date_created TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (item_id) REFERENCES items(id),
        FOREIGN KEY (bill_id) REFERENCES bills(id)
    )
    ''')
    
    # Transactions (General ledger)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS transactions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        transaction_type TEXT NOT NULL,
        transaction_date DATE,
        description TEXT,
        account_head TEXT,
        debit_amount REAL DEFAULT 0,
        credit_amount REAL DEFAULT 0,
        reference_id INTEGER,
        reference_type TEXT,
        payment_mode TEXT,
        date_created TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        notes TEXT
    )
    ''')
    
    # Smith/Jeweller Transfers
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS artisan_transfers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        artisan_name TEXT NOT NULL,
        artisan_type TEXT NOT NULL,
        artisan_phone TEXT,
        item_id INTEGER,
        material_type TEXT,
        weight_sent REAL NOT NULL,
        date_sent DATE,
        expected_return_date DATE,
        status TEXT DEFAULT 'Pending',
        weight_received REAL DEFAULT 0,
        date_received DATE,
        loss_gain REAL DEFAULT 0,
        labour_charges REAL DEFAULT 0,
        bill_id INTEGER,
        remarks TEXT,
        date_created TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (item_id) REFERENCES items(id),
        FOREIGN KEY (bill_id) REFERENCES bills(id)
    )
    ''')
    
    # Metal Rates table (Gold, Silver, Platinum)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS metal_rates (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        material_id INTEGER,
        rate_date DATE NOT NULL,
        purity TEXT NOT NULL,
        rate_per_gram REAL NOT NULL,
        making_charges REAL DEFAULT 0,
        is_active INTEGER DEFAULT 1,
        notes TEXT,
        date_created TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        date_modified TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (material_id) REFERENCES materials(id),
        UNIQUE(material_id, rate_date, purity)
    )
    ''')
    
    # Legacy gold_rates table for compatibility
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS gold_rates (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        rate_date DATE NOT NULL,
        purity TEXT NOT NULL,
        rate_per_gram REAL NOT NULL,
        making_charges REAL DEFAULT 0,
        is_active INTEGER DEFAULT 1,
        notes TEXT,
        date_created TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        date_modified TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        UNIQUE(rate_date, purity)
    )
    ''')
    
    # Diamond Rates table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS diamond_rates (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        rate_date DATE NOT NULL,
        shape TEXT DEFAULT 'Round',
        clarity TEXT NOT NULL,
        color TEXT NOT NULL,
        carat_from REAL DEFAULT 0,
        carat_to REAL DEFAULT 10,
        rate_per_carat REAL NOT NULL,
        certification TEXT,
        is_active INTEGER DEFAULT 1,
        notes TEXT,
        date_created TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        date_modified TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    # Advance Orders table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS advance_orders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        order_number TEXT UNIQUE NOT NULL,
        customer_id INTEGER NOT NULL,
        employee_id INTEGER,
        order_date DATE NOT NULL,
        expected_delivery_date DATE,
        actual_delivery_date DATE,
        order_type TEXT DEFAULT 'Custom',
        material_type TEXT DEFAULT 'Gold',
        estimated_weight REAL DEFAULT 0,
        estimated_amount REAL DEFAULT 0,
        advance_amount REAL DEFAULT 0,
        final_amount REAL DEFAULT 0,
        balance_amount REAL DEFAULT 0,
        gold_rate_locked REAL DEFAULT 0,
        diamond_rate_locked REAL DEFAULT 0,
        specifications TEXT,
        design_notes TEXT,
        status TEXT DEFAULT 'Pending',
        priority TEXT DEFAULT 'Normal',
        assigned_artisan TEXT,
        bill_id INTEGER,
        remarks TEXT,
        date_created TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        date_modified TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (customer_id) REFERENCES customers(id),
        FOREIGN KEY (employee_id) REFERENCES employees(id),
        FOREIGN KEY (bill_id) REFERENCES bills(id)
    )
    ''')
    
    # Advance Order Items
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS advance_order_items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        order_id INTEGER NOT NULL,
        item_type TEXT,
        description TEXT,
        material_type TEXT,
        estimated_weight REAL DEFAULT 0,
        estimated_diamond_carat REAL DEFAULT 0,
        purity TEXT,
        estimated_price REAL DEFAULT 0,
        design_reference TEXT,
        remarks TEXT,
        FOREIGN KEY (order_id) REFERENCES advance_orders(id)
    )
    ''')
    
    # Payment Records
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS payments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        payment_type TEXT NOT NULL,
        payment_date DATE NOT NULL,
        amount REAL NOT NULL,
        payment_mode TEXT DEFAULT 'Cash',
        reference_type TEXT,
        reference_id INTEGER,
        customer_id INTEGER,
        supplier_id INTEGER,
        description TEXT,
        receipt_number TEXT,
        bank_name TEXT,
        cheque_number TEXT,
        transaction_id TEXT,
        status TEXT DEFAULT 'Completed',
        date_created TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (customer_id) REFERENCES customers(id),
        FOREIGN KEY (supplier_id) REFERENCES suppliers(id)
    )
    ''')
    
    # Old Gold/Exchange table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS old_gold_exchange (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        bill_id INTEGER,
        customer_id INTEGER,
        exchange_date DATE NOT NULL,
        item_description TEXT,
        gross_weight REAL NOT NULL,
        purity TEXT,
        net_weight REAL DEFAULT 0,
        rate_per_gram REAL NOT NULL,
        deduction_percent REAL DEFAULT 0,
        total_value REAL NOT NULL,
        remarks TEXT,
        date_created TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (bill_id) REFERENCES bills(id),
        FOREIGN KEY (customer_id) REFERENCES customers(id)
    )
    ''')
    
    # Scheme/Savings Plans
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS savings_schemes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        scheme_name TEXT NOT NULL,
        scheme_type TEXT DEFAULT 'Monthly',
        monthly_amount REAL,
        duration_months INTEGER,
        bonus_percent REAL DEFAULT 0,
        bonus_month INTEGER,
        is_active INTEGER DEFAULT 1,
        description TEXT,
        date_created TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    # Customer Scheme Enrollments
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS scheme_enrollments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        scheme_id INTEGER NOT NULL,
        customer_id INTEGER NOT NULL,
        enrollment_date DATE NOT NULL,
        monthly_amount REAL NOT NULL,
        total_paid REAL DEFAULT 0,
        total_months_paid INTEGER DEFAULT 0,
        maturity_date DATE,
        status TEXT DEFAULT 'Active',
        remarks TEXT,
        date_created TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (scheme_id) REFERENCES savings_schemes(id),
        FOREIGN KEY (customer_id) REFERENCES customers(id)
    )
    ''')
    
    # Scheme Payments
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS scheme_payments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        enrollment_id INTEGER NOT NULL,
        payment_date DATE NOT NULL,
        amount REAL NOT NULL,
        payment_mode TEXT DEFAULT 'Cash',
        receipt_number TEXT,
        month_number INTEGER,
        remarks TEXT,
        date_created TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (enrollment_id) REFERENCES scheme_enrollments(id)
    )
    ''')
    
    conn.commit()
    
    # Run migrations to add missing columns to existing tables
    run_migrations(cursor)
    
    conn.commit()
    conn.close()


def run_migrations(cursor):
    """Add missing columns to existing tables for backwards compatibility"""
    
    def add_column_if_not_exists(table, column, definition):
        try:
            cursor.execute(f"SELECT {column} FROM {table} LIMIT 1")
        except:
            try:
                cursor.execute(f"ALTER TABLE {table} ADD COLUMN {column} {definition}")
            except:
                pass
    
    # Items table migrations
    add_column_if_not_exists('items', 'material_id', 'INTEGER')
    add_column_if_not_exists('items', 'item_type', "TEXT DEFAULT 'finished'")
    add_column_if_not_exists('items', 'gold_weight', 'REAL DEFAULT 0')
    add_column_if_not_exists('items', 'diamond_weight', 'REAL DEFAULT 0')
    add_column_if_not_exists('items', 'diamond_count', 'INTEGER DEFAULT 0')
    add_column_if_not_exists('items', 'diamond_clarity', 'TEXT')
    add_column_if_not_exists('items', 'diamond_color', 'TEXT')
    add_column_if_not_exists('items', 'diamond_cut', 'TEXT')
    add_column_if_not_exists('items', 'diamond_carat', 'REAL DEFAULT 0')
    add_column_if_not_exists('items', 'diamond_certification', 'TEXT')
    add_column_if_not_exists('items', 'stone_weight', 'REAL DEFAULT 0')
    add_column_if_not_exists('items', 'stone_type', 'TEXT')
    add_column_if_not_exists('items', 'hallmark', 'TEXT')
    add_column_if_not_exists('items', 'hsn_code', 'TEXT')
    add_column_if_not_exists('items', 'cost_price', 'REAL')
    add_column_if_not_exists('items', 'making_charges', 'REAL DEFAULT 0')
    add_column_if_not_exists('items', 'making_charges_type', "TEXT DEFAULT 'per_gram'")
    
    # Bills table migrations
    add_column_if_not_exists('bills', 'employee_id', 'INTEGER')
    add_column_if_not_exists('bills', 'total_gold_weight', 'REAL DEFAULT 0')
    add_column_if_not_exists('bills', 'total_diamond_weight', 'REAL DEFAULT 0')
    add_column_if_not_exists('bills', 'making_charges', 'REAL DEFAULT 0')
    add_column_if_not_exists('bills', 'paid_amount', 'REAL DEFAULT 0')
    add_column_if_not_exists('bills', 'outstanding_amount', 'REAL DEFAULT 0')
    add_column_if_not_exists('bills', 'payment_mode', "TEXT DEFAULT 'Cash'")
    add_column_if_not_exists('bills', 'remarks', 'TEXT')
    
    # Item categories migrations
    add_column_if_not_exists('item_categories', 'material_id', 'INTEGER')
    
    # Stock movements migrations
    add_column_if_not_exists('stock_movements', 'weight_change', 'REAL DEFAULT 0')
    add_column_if_not_exists('stock_movements', 'previous_weight', 'REAL DEFAULT 0')
    add_column_if_not_exists('stock_movements', 'new_weight', 'REAL DEFAULT 0')
    add_column_if_not_exists('stock_movements', 'adjusted_by', 'TEXT')


def execute_query(query, params=None):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        conn.commit()
        return cursor.lastrowid
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()

def fetch_query(query, params=None):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        return cursor.fetchall()
    finally:
        conn.close()

def fetch_one(query, params=None):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        return cursor.fetchone()
    finally:
        conn.close()

def execute_many(query, params_list):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.executemany(query, params_list)
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()
