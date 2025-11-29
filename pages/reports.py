import tkinter as tk
from tkinter import messagebox, ttk
from database.db import fetch_query
from datetime import datetime

def reports_page(parent):
    for widget in parent.winfo_children():
        widget.destroy()
    
    frame = ttk.Frame(parent)
    frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    
    # Title
    title_label = ttk.Label(frame, text="Reports", font=("Segoe UI", 16, "bold"))
    title_label.pack(pady=10)
    
    # Button frame
    button_frame = ttk.Frame(frame)
    button_frame.pack(fill=tk.X, pady=10)
    
    ttk.Button(button_frame, text="Stock Report", command=lambda: show_stock_report(parent)).pack(side=tk.LEFT, padx=5)
    ttk.Button(button_frame, text="Sales Report", command=lambda: show_sales_report(parent)).pack(side=tk.LEFT, padx=5)
    ttk.Button(button_frame, text="Purchase Report", command=lambda: show_purchase_report(parent)).pack(side=tk.LEFT, padx=5)
    ttk.Button(button_frame, text="Customer Report", command=lambda: show_customer_report(parent)).pack(side=tk.LEFT, padx=5)
    
    # Report output area
    output_frame = ttk.Frame(frame)
    output_frame.pack(fill=tk.BOTH, expand=True, pady=20)
    
    output_text = tk.Text(output_frame, height=20, width=80)
    output_text.pack(fill=tk.BOTH, expand=True)
    
    scrollbar = ttk.Scrollbar(output_text)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    output_text.config(yscrollcommand=scrollbar.set)

def show_stock_report(parent):
    messagebox.showinfo("Stock Report", "Stock Report - Coming soon!")

def show_sales_report(parent):
    messagebox.showinfo("Sales Report", "Sales Report - Coming soon!")

def show_purchase_report(parent):
    messagebox.showinfo("Purchase Report", "Purchase Report - Coming soon!")

def show_customer_report(parent):
    messagebox.showinfo("Customer Report", "Customer Report - Coming soon!")