import tkinter as tk
from tkinter import messagebox, ttk
from database.db import execute_query, fetch_query
from datetime import datetime

def create_transaction(transaction_type, account_head, debit=0, credit=0, description=""):
    execute_query("""
        INSERT INTO transactions (transaction_type, description, account_head, debit_amount, credit_amount, date_created)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (transaction_type, description, account_head, debit, credit, datetime.now()))

def get_customer_transactions(customer_id):
    return fetch_query("""
        SELECT b.bill_number, b.bill_type, b.bill_date, b.total_amount, b.outstanding_amount
        FROM bills b
        WHERE b.customer_id = ?
        ORDER BY b.bill_date DESC
    """, (customer_id,))

def get_supplier_transactions(supplier_id):
    return fetch_query("""
        SELECT b.bill_number, b.bill_type, b.bill_date, b.total_amount, b.outstanding_amount
        FROM bills b
        WHERE b.supplier_id = ?
        ORDER BY b.bill_date DESC
    """, (supplier_id,))

def create_sales_transaction(customer_id, amount, description):
    create_transaction('SALES', 'Sales', credit=amount, description=description)

def create_purchase_transaction(supplier_id, amount, description):
    create_transaction('PURCHASE', 'Purchase', debit=amount, description=description)