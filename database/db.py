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
    
    # Customers table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS customers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL UNIQUE,
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
        name TEXT NOT NULL UNIQUE,
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
        name TEXT NOT NULL UNIQUE,
        phone TEXT,
        email TEXT,
        address TEXT,
        city TEXT,
        state TEXT,
        pincode TEXT,
        gst_number TEXT,
        date_created TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        date_modified TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    # Item Categories
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS item_categories (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL UNIQUE,
        description TEXT,
        date_created TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    # Items table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        category_id INTEGER,
        barcode TEXT UNIQUE,
        price REAL NOT NULL,
        cost_price REAL,
        quantity INTEGER DEFAULT 0,
        weight_in_gm REAL DEFAULT 0,
        purity TEXT,
        description TEXT,
        is_active INTEGER DEFAULT 1,
        date_created TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        date_modified TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (category_id) REFERENCES item_categories(id)
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
        discount_amount REAL DEFAULT 0,
        tax_amount REAL DEFAULT 0,
        paid_amount REAL DEFAULT 0,
        outstanding_amount REAL DEFAULT 0,
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
        last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (item_id) REFERENCES items(id)
    )
    ''')
    
    # Stock Movements
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS stock_movements (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        item_id INTEGER NOT NULL,
        transaction_type TEXT NOT NULL,
        quantity_change REAL NOT NULL,
        weight_change REAL DEFAULT 0,
        bill_id INTEGER,
        reference TEXT,
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
        description TEXT,
        account_head TEXT,
        debit_amount REAL DEFAULT 0,
        credit_amount REAL DEFAULT 0,
        reference_id INTEGER,
        reference_type TEXT,
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
        item_id INTEGER,
        weight_sent REAL NOT NULL,
        date_sent DATE,
        status TEXT DEFAULT 'Pending',
        weight_received REAL DEFAULT 0,
        date_received DATE,
        loss_gain REAL DEFAULT 0,
        bill_id INTEGER,
        date_created TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (item_id) REFERENCES items(id),
        FOREIGN KEY (bill_id) REFERENCES bills(id)
    )
    ''')
    
    conn.commit()
    conn.close()

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