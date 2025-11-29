import tkinter as tk
from tkinter import messagebox, ttk
from database.db import execute_query, fetch_query, fetch_one
from datetime import datetime

def customers_page(parent):
    for widget in parent.winfo_children():
        widget.destroy()
    
    frame = ttk.Frame(parent)
    frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    
    # Title
    title_label = ttk.Label(frame, text="Customer Management", font=("Segoe UI", 16, "bold"))
    title_label.pack(pady=10)
    
    # Button frame
    button_frame = ttk.Frame(frame)
    button_frame.pack(fill=tk.X, pady=10)
    
    ttk.Button(button_frame, text="Add Customer", command=lambda: show_add_customer_dialog(parent)).pack(side=tk.LEFT, padx=5)
    ttk.Button(button_frame, text="View Details", command=lambda: show_customer_details(parent)).pack(side=tk.LEFT, padx=5)
    ttk.Button(button_frame, text="Refresh", command=lambda: refresh_customers_list(tree)).pack(side=tk.LEFT, padx=5)
    
    # Treeview for customers
    columns = ('ID', 'Name', 'Phone', 'Email', 'City', 'Outstanding')
    tree = ttk.Treeview(frame, columns=columns, height=15)
    
    for col in columns:
        tree.column(col, width=150)
        tree.heading(col, text=col)
    
    tree.pack(fill=tk.BOTH, expand=True)
    
    refresh_customers_list(tree)

def refresh_customers_list(tree):
    for item in tree.get_children():
        tree.delete(item)
    
    customers = fetch_query("""
        SELECT id, name, phone, email, city, outstanding_balance
        FROM customers
        ORDER BY date_created DESC
    """)
    
    for customer in customers:
        tree.insert('', 'end', values=customer)

def show_add_customer_dialog(parent):
    dialog = tk.Toplevel(parent)
    dialog.title("Add New Customer")
    dialog.geometry("400x600")
    
    fields = {}
    
    labels = ['Name', 'Phone', 'Email', 'Address', 'City', 'State', 'Pincode', 'GST Number', 'Credit Limit']
    
    for label in labels:
        ttk.Label(dialog, text=f"{label}:").pack(pady=5)
        fields[label.lower()] = ttk.Entry(dialog, width=40)
        fields[label.lower()].pack(pady=5)
    
    def save_customer():
        try:
            execute_query("""
                INSERT INTO customers (name, phone, email, address, city, state, pincode, gst_number, credit_limit, date_created, date_modified)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                fields['name'].get(),
                fields['phone'].get(),
                fields['email'].get(),
                fields['address'].get(),
                fields['city'].get(),
                fields['state'].get(),
                fields['pincode'].get(),
                fields['gst number'].get(),
                float(fields['credit limit'].get() or 0),
                datetime.now(),
                datetime.now()
            ))
            messagebox.showinfo("Success", "Customer added successfully!")
            dialog.destroy()
        except Exception as e:
            messagebox.showerror("Error", f"Error adding customer: {str(e)}")
    
    ttk.Button(dialog, text="Save", command=save_customer).pack(pady=20)

def show_customer_details(parent):
    messagebox.showinfo("Customer Details", "Select customer from list to view details")