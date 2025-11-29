import tkinter as tk
from tkinter import ttk
from database.db import fetch_query
from datetime import datetime, timedelta

def dashboard_page(parent):
    for widget in parent.winfo_children():
        widget.destroy()
    
    frame = ttk.Frame(parent)
    frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    
    # Title
    title_label = ttk.Label(frame, text="Dashboard", font=("Segoe UI", 16, "bold"))
    title_label.pack(pady=10)
    
    # Stats frame
    stats_frame = ttk.Frame(frame)
    stats_frame.pack(fill=tk.X, pady=20)
    
    # Get statistics
    total_customers = fetch_query("SELECT COUNT(*) as count FROM customers")[0][0]
    total_items = fetch_query("SELECT COUNT(*) as count FROM items WHERE is_active = 1")[0][0]
    total_employees = fetch_query("SELECT COUNT(*) as count FROM employees WHERE status = 'Active'")[0][0]
    
    # Today's sales
    today = datetime.now().date()
    today_sales = fetch_query("""
        SELECT COALESCE(SUM(total_amount), 0) as total
        FROM bills
        WHERE bill_type = 'Sales' AND DATE(bill_date) = ?
    """, (today,))[0][0]
    
    # Create stat cards
    create_stat_card(stats_frame, "Total Customers", total_customers, 0)
    create_stat_card(stats_frame, "Total Items", total_items, 1)
    create_stat_card(stats_frame, "Active Employees", total_employees, 2)
    create_stat_card(stats_frame, "Today's Sales", f"₹ {today_sales}", 3)

def create_stat_card(parent, title, value, column):
    card = ttk.LabelFrame(parent, text=title, padding=20)
    card.grid(row=0, column=column, padx=20, pady=10, sticky='nsew')
    
    value_label = ttk.Label(card, text=str(value), font=("Segoe UI", 24, "bold"))
    value_label.pack()