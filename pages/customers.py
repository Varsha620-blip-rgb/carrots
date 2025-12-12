import tkinter as tk
from tkinter import messagebox, ttk
from database.db import execute_query, fetch_query, fetch_one
from datetime import datetime

customers_tree = None

def customers_page(parent):
    global customers_tree
    
    for widget in parent.winfo_children():
        widget.destroy()
    
    frame = ttk.Frame(parent)
    frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    
    title_frame = ttk.Frame(frame)
    title_frame.pack(fill=tk.X, pady=10)
    
    title_label = ttk.Label(title_frame, text="Customer Management", font=("Segoe UI", 16, "bold"))
    title_label.pack(side=tk.LEFT)
    
    search_frame = ttk.Frame(frame)
    search_frame.pack(fill=tk.X, pady=5)
    
    ttk.Label(search_frame, text="Search:").pack(side=tk.LEFT, padx=5)
    search_var = tk.StringVar()
    search_entry = ttk.Entry(search_frame, textvariable=search_var, width=30)
    search_entry.pack(side=tk.LEFT, padx=5)
    
    def search_customers():
        refresh_customers_list(customers_tree, search_var.get())
    
    ttk.Button(search_frame, text="Search", command=search_customers).pack(side=tk.LEFT, padx=5)
    ttk.Button(search_frame, text="Clear", command=lambda: [search_var.set(""), refresh_customers_list(customers_tree)]).pack(side=tk.LEFT, padx=5)
    
    button_frame = ttk.Frame(frame)
    button_frame.pack(fill=tk.X, pady=10)
    
    ttk.Button(button_frame, text="Add Customer", command=lambda: show_add_customer_dialog(parent)).pack(side=tk.LEFT, padx=5)
    ttk.Button(button_frame, text="Edit Customer", command=lambda: show_edit_customer_dialog(parent, customers_tree)).pack(side=tk.LEFT, padx=5)
    ttk.Button(button_frame, text="Delete Customer", command=lambda: delete_customer(customers_tree)).pack(side=tk.LEFT, padx=5)
    ttk.Button(button_frame, text="View Details", command=lambda: view_customer_details(customers_tree)).pack(side=tk.LEFT, padx=5)
    ttk.Button(button_frame, text="View Transactions", command=lambda: view_customer_transactions(customers_tree)).pack(side=tk.LEFT, padx=5)
    ttk.Button(button_frame, text="Refresh", command=lambda: refresh_customers_list(customers_tree)).pack(side=tk.LEFT, padx=5)
    
    tree_frame = ttk.Frame(frame)
    tree_frame.pack(fill=tk.BOTH, expand=True)
    
    columns = ('ID', 'Name', 'Phone', 'Email', 'City', 'GST', 'Credit Limit', 'Outstanding')
    customers_tree = ttk.Treeview(tree_frame, columns=columns, height=15, show='headings')
    
    col_widths = {'ID': 50, 'Name': 150, 'Phone': 100, 'Email': 150, 'City': 100, 
                  'GST': 120, 'Credit Limit': 100, 'Outstanding': 100}
    
    for col in columns:
        customers_tree.column(col, width=col_widths.get(col, 100), anchor='center')
        customers_tree.heading(col, text=col, command=lambda c=col: sort_column(customers_tree, c, False))
    
    scrollbar_y = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=customers_tree.yview)
    customers_tree.configure(yscroll=scrollbar_y.set)
    
    customers_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y)
    
    customers_tree.bind('<Double-1>', lambda e: view_customer_details(customers_tree))
    
    refresh_customers_list(customers_tree)
    
    status_frame = ttk.Frame(frame)
    status_frame.pack(fill=tk.X, pady=5)
    
    customer_count = fetch_query("SELECT COUNT(*) FROM customers")[0][0]
    total_outstanding = fetch_query("SELECT COALESCE(SUM(outstanding_balance), 0) FROM customers")[0][0]
    ttk.Label(status_frame, text=f"Total Customers: {customer_count} | Total Outstanding: ₹{total_outstanding:,.2f}").pack(side=tk.LEFT)

def sort_column(tree, col, reverse):
    items = [(tree.set(k, col), k) for k in tree.get_children('')]
    try:
        items.sort(key=lambda t: float(t[0].replace('₹','').replace(',','')) if '₹' in t[0] else (float(t[0]) if t[0].replace('.','',1).isdigit() else t[0]), reverse=reverse)
    except:
        items.sort(reverse=reverse)
    
    for index, (val, k) in enumerate(items):
        tree.move(k, '', index)
    
    tree.heading(col, command=lambda: sort_column(tree, col, not reverse))

def refresh_customers_list(tree, search_term=""):
    if tree is None:
        return
        
    for item in tree.get_children():
        tree.delete(item)
    
    if search_term:
        query = """
            SELECT id, name, phone, email, city, gst_number, credit_limit, outstanding_balance
            FROM customers
            WHERE name LIKE ? OR phone LIKE ? OR email LIKE ? OR city LIKE ?
            ORDER BY name
        """
        search_pattern = f"%{search_term}%"
        customers = fetch_query(query, (search_pattern, search_pattern, search_pattern, search_pattern))
    else:
        customers = fetch_query("""
            SELECT id, name, phone, email, city, gst_number, credit_limit, outstanding_balance
            FROM customers
            ORDER BY name
        """)
    
    for customer in customers:
        formatted = (
            customer[0], customer[1], customer[2] or "N/A", customer[3] or "N/A",
            customer[4] or "N/A", customer[5] or "N/A",
            f"₹{customer[6]:,.2f}" if customer[6] else "₹0.00",
            f"₹{customer[7]:,.2f}" if customer[7] else "₹0.00"
        )
        tree.insert('', 'end', values=formatted)

def show_add_customer_dialog(parent):
    dialog = tk.Toplevel(parent)
    dialog.title("Add New Customer")
    dialog.geometry("450x650")
    dialog.transient(parent)
    dialog.grab_set()
    
    main_frame = ttk.Frame(dialog, padding=20)
    main_frame.pack(fill=tk.BOTH, expand=True)
    
    ttk.Label(main_frame, text="Add New Customer", font=("Segoe UI", 14, "bold")).pack(pady=10)
    
    form_frame = ttk.Frame(main_frame)
    form_frame.pack(fill=tk.X)
    
    fields = {}
    field_info = [
        ('Name *', 'name'),
        ('Phone', 'phone'),
        ('Email', 'email'),
        ('Address', 'address'),
        ('City', 'city'),
        ('State', 'state'),
        ('Pincode', 'pincode'),
        ('GST Number', 'gst_number'),
        ('Credit Limit (₹)', 'credit_limit'),
    ]
    
    for row, (label, key) in enumerate(field_info):
        ttk.Label(form_frame, text=f"{label}:").grid(row=row, column=0, sticky='w', pady=5)
        fields[key] = ttk.Entry(form_frame, width=35)
        fields[key].grid(row=row, column=1, pady=5, padx=5)
    
    def save_customer():
        name = fields['name'].get().strip()
        
        if not name:
            messagebox.showwarning("Validation", "Customer name is required!")
            return
        
        try:
            credit_limit = float(fields['credit_limit'].get() or 0)
        except ValueError:
            messagebox.showerror("Error", "Invalid credit limit!")
            return
        
        try:
            execute_query("""
                INSERT INTO customers (name, phone, email, address, city, state, pincode, 
                                       gst_number, credit_limit, date_created, date_modified)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                name, fields['phone'].get() or None, fields['email'].get() or None,
                fields['address'].get() or None, fields['city'].get() or None,
                fields['state'].get() or None, fields['pincode'].get() or None,
                fields['gst_number'].get() or None, credit_limit,
                datetime.now(), datetime.now()
            ))
            messagebox.showinfo("Success", "Customer added successfully!")
            dialog.destroy()
            if customers_tree:
                refresh_customers_list(customers_tree)
        except Exception as e:
            if "UNIQUE constraint failed" in str(e):
                messagebox.showerror("Error", "A customer with this name already exists!")
            else:
                messagebox.showerror("Error", f"Error adding customer: {str(e)}")
    
    btn_frame = ttk.Frame(main_frame)
    btn_frame.pack(pady=20)
    
    ttk.Button(btn_frame, text="Save", command=save_customer, width=15).pack(side=tk.LEFT, padx=10)
    ttk.Button(btn_frame, text="Cancel", command=dialog.destroy, width=15).pack(side=tk.LEFT, padx=10)

def show_edit_customer_dialog(parent, tree):
    selected = tree.selection()
    if not selected:
        messagebox.showwarning("Warning", "Please select a customer to edit!")
        return
    
    customer_id = tree.item(selected[0])['values'][0]
    
    customer = fetch_one("""
        SELECT id, name, phone, email, address, city, state, pincode, 
               gst_number, credit_limit, outstanding_balance
        FROM customers WHERE id = ?
    """, (customer_id,))
    
    if not customer:
        messagebox.showerror("Error", "Customer not found!")
        return
    
    dialog = tk.Toplevel(parent)
    dialog.title("Edit Customer")
    dialog.geometry("450x650")
    dialog.transient(parent)
    dialog.grab_set()
    
    main_frame = ttk.Frame(dialog, padding=20)
    main_frame.pack(fill=tk.BOTH, expand=True)
    
    ttk.Label(main_frame, text="Edit Customer", font=("Segoe UI", 14, "bold")).pack(pady=10)
    
    form_frame = ttk.Frame(main_frame)
    form_frame.pack(fill=tk.X)
    
    fields = {}
    field_info = [
        ('Name *', 'name', customer[1]),
        ('Phone', 'phone', customer[2]),
        ('Email', 'email', customer[3]),
        ('Address', 'address', customer[4]),
        ('City', 'city', customer[5]),
        ('State', 'state', customer[6]),
        ('Pincode', 'pincode', customer[7]),
        ('GST Number', 'gst_number', customer[8]),
        ('Credit Limit (₹)', 'credit_limit', customer[9]),
    ]
    
    for row, (label, key, value) in enumerate(field_info):
        ttk.Label(form_frame, text=f"{label}:").grid(row=row, column=0, sticky='w', pady=5)
        fields[key] = ttk.Entry(form_frame, width=35)
        if value:
            fields[key].insert(0, str(value))
        fields[key].grid(row=row, column=1, pady=5, padx=5)
    
    row += 1
    ttk.Label(form_frame, text="Outstanding Balance:").grid(row=row, column=0, sticky='w', pady=5)
    outstanding_label = ttk.Label(form_frame, text=f"₹{customer[10]:,.2f}" if customer[10] else "₹0.00")
    outstanding_label.grid(row=row, column=1, sticky='w', pady=5, padx=5)
    
    def update_customer():
        name = fields['name'].get().strip()
        
        if not name:
            messagebox.showwarning("Validation", "Customer name is required!")
            return
        
        try:
            credit_limit = float(fields['credit_limit'].get() or 0)
        except ValueError:
            messagebox.showerror("Error", "Invalid credit limit!")
            return
        
        try:
            execute_query("""
                UPDATE customers 
                SET name = ?, phone = ?, email = ?, address = ?, city = ?, 
                    state = ?, pincode = ?, gst_number = ?, credit_limit = ?, date_modified = ?
                WHERE id = ?
            """, (
                name, fields['phone'].get() or None, fields['email'].get() or None,
                fields['address'].get() or None, fields['city'].get() or None,
                fields['state'].get() or None, fields['pincode'].get() or None,
                fields['gst_number'].get() or None, credit_limit,
                datetime.now(), customer_id
            ))
            messagebox.showinfo("Success", "Customer updated successfully!")
            dialog.destroy()
            refresh_customers_list(tree)
        except Exception as e:
            messagebox.showerror("Error", f"Error updating customer: {str(e)}")
    
    btn_frame = ttk.Frame(main_frame)
    btn_frame.pack(pady=20)
    
    ttk.Button(btn_frame, text="Update", command=update_customer, width=15).pack(side=tk.LEFT, padx=10)
    ttk.Button(btn_frame, text="Cancel", command=dialog.destroy, width=15).pack(side=tk.LEFT, padx=10)

def delete_customer(tree):
    selected = tree.selection()
    if not selected:
        messagebox.showwarning("Warning", "Please select a customer to delete!")
        return
    
    customer_id = tree.item(selected[0])['values'][0]
    customer_name = tree.item(selected[0])['values'][1]
    
    bills = fetch_query("SELECT COUNT(*) FROM bills WHERE customer_id = ?", (customer_id,))[0][0]
    if bills > 0:
        messagebox.showwarning("Warning", f"Cannot delete customer '{customer_name}' because they have {bills} associated bills.\n\nPlease delete the bills first or keep the customer record.")
        return
    
    if messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete customer '{customer_name}'?\n\nThis action cannot be undone."):
        try:
            execute_query("DELETE FROM customers WHERE id = ?", (customer_id,))
            messagebox.showinfo("Success", "Customer deleted successfully!")
            refresh_customers_list(tree)
        except Exception as e:
            messagebox.showerror("Error", f"Error deleting customer: {str(e)}")

def view_customer_details(tree):
    selected = tree.selection()
    if not selected:
        messagebox.showwarning("Warning", "Please select a customer to view!")
        return
    
    customer_id = tree.item(selected[0])['values'][0]
    
    customer = fetch_one("""
        SELECT * FROM customers WHERE id = ?
    """, (customer_id,))
    
    if not customer:
        messagebox.showerror("Error", "Customer not found!")
        return
    
    total_bills = fetch_query("SELECT COUNT(*), COALESCE(SUM(total_amount), 0) FROM bills WHERE customer_id = ?", (customer_id,))[0]
    
    details = f"""
CUSTOMER DETAILS
{'='*40}

Name: {customer[1]}
Phone: {customer[2] or 'N/A'}
Email: {customer[3] or 'N/A'}
Address: {customer[4] or 'N/A'}
City: {customer[5] or 'N/A'}
State: {customer[6] or 'N/A'}
Pincode: {customer[7] or 'N/A'}
GST Number: {customer[8] or 'N/A'}

FINANCIAL
Credit Limit: ₹{customer[9]:,.2f}
Outstanding Balance: ₹{customer[10]:,.2f}

STATISTICS
Total Bills: {total_bills[0]}
Total Business: ₹{total_bills[1]:,.2f}

Created: {customer[11]}
Modified: {customer[12]}
    """
    
    messagebox.showinfo("Customer Details", details)

def view_customer_transactions(tree):
    selected = tree.selection()
    if not selected:
        messagebox.showwarning("Warning", "Please select a customer!")
        return
    
    customer_id = tree.item(selected[0])['values'][0]
    customer_name = tree.item(selected[0])['values'][1]
    
    bills = fetch_query("""
        SELECT bill_number, bill_type, bill_date, total_amount, paid_amount, status
        FROM bills
        WHERE customer_id = ?
        ORDER BY bill_date DESC
        LIMIT 50
    """, (customer_id,))
    
    if not bills:
        messagebox.showinfo("Transactions", f"No transactions found for {customer_name}")
        return
    
    dialog = tk.Toplevel()
    dialog.title(f"Transactions - {customer_name}")
    dialog.geometry("700x400")
    
    columns = ('Bill #', 'Type', 'Date', 'Amount', 'Paid', 'Status')
    trans_tree = ttk.Treeview(dialog, columns=columns, height=15, show='headings')
    
    for col in columns:
        trans_tree.heading(col, text=col)
        trans_tree.column(col, width=100)
    
    for bill in bills:
        trans_tree.insert('', 'end', values=(
            bill[0], bill[1], bill[2], 
            f"₹{bill[3]:,.2f}", f"₹{bill[4]:,.2f}", bill[5]
        ))
    
    trans_tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    
    ttk.Button(dialog, text="Close", command=dialog.destroy).pack(pady=10)
