import tkinter as tk
from tkinter import messagebox, ttk
from database.db import execute_query, fetch_query, fetch_one
from datetime import datetime

def bills_page(parent):
    for widget in parent.winfo_children():
        widget.destroy()
    
    frame = ttk.Frame(parent)
    frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    
    # Title
    title_label = ttk.Label(frame, text="Bill Management", font=("Segoe UI", 16, "bold"))
    title_label.pack(pady=10)
    
    # Button frame
    button_frame = ttk.Frame(frame)
    button_frame.pack(fill=tk.X, pady=10)
    
    ttk.Button(button_frame, text="New Sales Bill", command=lambda: show_new_bill_dialog(parent, 'Sales')).pack(side=tk.LEFT, padx=5)
    ttk.Button(button_frame, text="New Purchase Bill", command=lambda: show_new_bill_dialog(parent, 'Purchase')).pack(side=tk.LEFT, padx=5)
    ttk.Button(button_frame, text="View Bills", command=lambda: refresh_bills_list(tree)).pack(side=tk.LEFT, padx=5)
    
    # Treeview for bills
    columns = ('ID', 'Bill #', 'Type', 'Date', 'Total', 'Status')
    tree = ttk.Treeview(frame, columns=columns, height=15)
    
    for col in columns:
        tree.column(col, width=150)
        tree.heading(col, text=col)
    
    tree.pack(fill=tk.BOTH, expand=True)
    
    refresh_bills_list(tree)

def refresh_bills_list(tree):
    for item in tree.get_children():
        tree.delete(item)
    
    bills = fetch_query("""
        SELECT id, bill_number, bill_type, bill_date, total_amount, status
        FROM bills
        ORDER BY bill_date DESC
        LIMIT 100
    """)
    
    for bill in bills:
        tree.insert('', 'end', values=bill)

def show_new_bill_dialog(parent, bill_type):
    messagebox.showinfo("New Bill", f"Creating new {bill_type} Bill - Coming soon!")