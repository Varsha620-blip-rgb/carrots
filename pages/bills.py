import tkinter as tk
from tkinter import messagebox, ttk
from database.db import execute_query, fetch_query, fetch_one
from datetime import datetime
import uuid

bills_tree = None

def bills_page(parent):
    global bills_tree
    
    for widget in parent.winfo_children():
        widget.destroy()
    
    frame = ttk.Frame(parent)
    frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    
    title_frame = ttk.Frame(frame)
    title_frame.pack(fill=tk.X, pady=10)
    
    title_label = ttk.Label(title_frame, text="Bill Management", font=("Segoe UI", 16, "bold"))
    title_label.pack(side=tk.LEFT)
    
    filter_frame = ttk.Frame(frame)
    filter_frame.pack(fill=tk.X, pady=5)
    
    ttk.Label(filter_frame, text="Type:").pack(side=tk.LEFT, padx=5)
    type_var = tk.StringVar(value="All")
    type_combo = ttk.Combobox(filter_frame, textvariable=type_var, values=['All', 'Sales', 'Purchase'], width=12)
    type_combo.pack(side=tk.LEFT, padx=5)
    
    ttk.Label(filter_frame, text="Status:").pack(side=tk.LEFT, padx=5)
    status_var = tk.StringVar(value="All")
    status_combo = ttk.Combobox(filter_frame, textvariable=status_var, values=['All', 'Completed', 'Pending', 'Cancelled'], width=12)
    status_combo.pack(side=tk.LEFT, padx=5)
    
    ttk.Label(filter_frame, text="Search:").pack(side=tk.LEFT, padx=5)
    search_var = tk.StringVar()
    search_entry = ttk.Entry(filter_frame, textvariable=search_var, width=20)
    search_entry.pack(side=tk.LEFT, padx=5)
    
    def apply_filter():
        refresh_bills_list(bills_tree, type_var.get(), status_var.get(), search_var.get())
    
    ttk.Button(filter_frame, text="Filter", command=apply_filter).pack(side=tk.LEFT, padx=5)
    ttk.Button(filter_frame, text="Clear", command=lambda: [type_var.set("All"), status_var.set("All"), search_var.set(""), refresh_bills_list(bills_tree)]).pack(side=tk.LEFT, padx=5)
    
    button_frame = ttk.Frame(frame)
    button_frame.pack(fill=tk.X, pady=10)
    
    ttk.Button(button_frame, text="New Sales Bill", command=lambda: show_new_bill_dialog(parent, 'Sales')).pack(side=tk.LEFT, padx=5)
    ttk.Button(button_frame, text="New Purchase Bill", command=lambda: show_new_bill_dialog(parent, 'Purchase')).pack(side=tk.LEFT, padx=5)
    ttk.Button(button_frame, text="View Bill", command=lambda: view_bill_details(bills_tree)).pack(side=tk.LEFT, padx=5)
    ttk.Button(button_frame, text="Add Payment", command=lambda: add_payment_dialog(bills_tree)).pack(side=tk.LEFT, padx=5)
    ttk.Button(button_frame, text="Cancel Bill", command=lambda: cancel_bill(bills_tree)).pack(side=tk.LEFT, padx=5)
    ttk.Button(button_frame, text="Refresh", command=lambda: refresh_bills_list(bills_tree)).pack(side=tk.LEFT, padx=5)
    
    tree_frame = ttk.Frame(frame)
    tree_frame.pack(fill=tk.BOTH, expand=True)
    
    columns = ('ID', 'Bill #', 'Type', 'Customer/Supplier', 'Employee', 'Date', 'Total', 'Paid', 'Outstanding', 'Status')
    bills_tree = ttk.Treeview(tree_frame, columns=columns, height=15, show='headings')
    
    col_widths = {'ID': 40, 'Bill #': 120, 'Type': 70, 'Customer/Supplier': 130, 'Employee': 90,
                  'Date': 90, 'Total': 90, 'Paid': 90, 'Outstanding': 90, 'Status': 80}
    
    for col in columns:
        bills_tree.column(col, width=col_widths.get(col, 100), anchor='center')
        bills_tree.heading(col, text=col)
    
    scrollbar_y = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=bills_tree.yview)
    bills_tree.configure(yscroll=scrollbar_y.set)
    
    bills_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y)
    
    bills_tree.bind('<Double-1>', lambda e: view_bill_details(bills_tree))
    
    refresh_bills_list(bills_tree)
    
    status_frame = ttk.Frame(frame)
    status_frame.pack(fill=tk.X, pady=5)
    
    today = datetime.now().date()
    today_sales = fetch_query("SELECT COALESCE(SUM(total_amount), 0) FROM bills WHERE bill_type='Sales' AND DATE(bill_date)=?", (today,))[0][0]
    today_purchases = fetch_query("SELECT COALESCE(SUM(total_amount), 0) FROM bills WHERE bill_type='Purchase' AND DATE(bill_date)=?", (today,))[0][0]
    ttk.Label(status_frame, text=f"Today's Sales: {today_sales:,.2f} | Today's Purchases: {today_purchases:,.2f}").pack(side=tk.LEFT)

def refresh_bills_list(tree, bill_type="All", status="All", search=""):
    if tree is None:
        return
        
    for item in tree.get_children():
        tree.delete(item)
    
    query = """
        SELECT b.id, b.bill_number, b.bill_type, 
               CASE WHEN b.bill_type = 'Sales' THEN COALESCE(c.name, 'Walk-in')
                    ELSE COALESCE(s.name, 'Unknown') END as party,
               COALESCE(e.name, 'N/A') as employee,
               b.bill_date, b.total_amount, b.paid_amount, b.outstanding_amount, b.status
        FROM bills b
        LEFT JOIN customers c ON b.customer_id = c.id
        LEFT JOIN suppliers s ON b.supplier_id = s.id
        LEFT JOIN employees e ON b.employee_id = e.id
        WHERE 1=1
    """
    params = []
    
    if bill_type and bill_type != "All":
        query += " AND b.bill_type = ?"
        params.append(bill_type)
    
    if status and status != "All":
        query += " AND b.status = ?"
        params.append(status)
    
    if search:
        query += " AND (b.bill_number LIKE ? OR c.name LIKE ? OR s.name LIKE ?)"
        search_pattern = f"%{search}%"
        params.extend([search_pattern, search_pattern, search_pattern])
    
    query += " ORDER BY b.bill_date DESC, b.id DESC LIMIT 200"
    
    bills = fetch_query(query, tuple(params)) if params else fetch_query(query)
    
    for bill in bills:
        formatted = (
            bill[0], bill[1], bill[2], bill[3], bill[4], bill[5],
            f"{bill[6]:,.2f}", f"{bill[7]:,.2f}", f"{bill[8]:,.2f}", bill[9]
        )
        tree.insert('', 'end', values=formatted)

def get_or_create_customer(name, phone=None, email=None):
    if not name or name.strip() == "":
        return None
    
    name = name.strip()
    
    existing = fetch_one("SELECT id FROM customers WHERE name = ? OR phone = ?", (name, phone if phone else ""))
    if existing:
        return existing[0]
    
    customer_id = execute_query("""
        INSERT INTO customers (name, phone, email, date_created, date_modified)
        VALUES (?, ?, ?, ?, ?)
    """, (name, phone, email, datetime.now(), datetime.now()))
    
    return customer_id

def show_new_bill_dialog(parent, bill_type):
    dialog = tk.Toplevel(parent)
    dialog.title(f"New {bill_type} Bill")
    dialog.geometry("950x750")
    dialog.transient(parent)
    dialog.grab_set()
    
    main_frame = ttk.Frame(dialog, padding=10)
    main_frame.pack(fill=tk.BOTH, expand=True)
    
    ttk.Label(main_frame, text=f"New {bill_type} Bill", font=("Segoe UI", 14, "bold")).pack(pady=5)
    
    header_frame = ttk.LabelFrame(main_frame, text="Bill Information", padding=10)
    header_frame.pack(fill=tk.X, pady=5)
    
    row1 = ttk.Frame(header_frame)
    row1.pack(fill=tk.X, pady=5)
    
    if bill_type == 'Sales':
        ttk.Label(row1, text="Customer:").pack(side=tk.LEFT, padx=5)
        customers = fetch_query("SELECT id, name, phone FROM customers ORDER BY name")
        customer_names = ['Walk-in Customer'] + [f"{c[1]} ({c[2] or 'No Phone'})" for c in customers]
        customer_var = ttk.Combobox(row1, values=customer_names, width=25)
        customer_var.set('Walk-in Customer')
        customer_var.pack(side=tk.LEFT, padx=5)
        party_combo = customer_var
        party_data = {f"{c[1]} ({c[2] or 'No Phone'})": c[0] for c in customers}
        
        ttk.Button(row1, text="+ New", command=lambda: show_quick_add_customer(customer_var, party_data)).pack(side=tk.LEFT, padx=2)
    else:
        ttk.Label(row1, text="Supplier:").pack(side=tk.LEFT, padx=5)
        suppliers = fetch_query("SELECT id, name FROM suppliers ORDER BY name")
        supplier_var = ttk.Combobox(row1, values=[f"{s[1]} (ID:{s[0]})" for s in suppliers], width=30)
        supplier_var.pack(side=tk.LEFT, padx=5)
        party_combo = supplier_var
        party_data = {f"{s[1]} (ID:{s[0]})": s[0] for s in suppliers}
    
    ttk.Label(row1, text="Employee *:").pack(side=tk.LEFT, padx=20)
    employees = fetch_query("SELECT id, name FROM employees WHERE status = 'Active' ORDER BY name")
    employee_var = ttk.Combobox(row1, values=[f"{e[1]}" for e in employees], width=20, state='readonly')
    employee_var.pack(side=tk.LEFT, padx=5)
    employee_data = {e[1]: e[0] for e in employees}
    
    row2 = ttk.Frame(header_frame)
    row2.pack(fill=tk.X, pady=5)
    
    ttk.Label(row2, text="Date:").pack(side=tk.LEFT, padx=5)
    date_entry = ttk.Entry(row2, width=12)
    date_entry.insert(0, datetime.now().strftime('%Y-%m-%d'))
    date_entry.pack(side=tk.LEFT, padx=5)
    
    ttk.Label(row2, text="Payment Mode:").pack(side=tk.LEFT, padx=20)
    payment_mode = ttk.Combobox(row2, values=['Cash', 'Card', 'UPI', 'Bank Transfer', 'Cheque', 'Credit'], width=12)
    payment_mode.set('Cash')
    payment_mode.pack(side=tk.LEFT, padx=5)
    
    gold_rate = fetch_query("SELECT rate_per_gram FROM gold_rates WHERE purity='22K' AND is_active=1 ORDER BY rate_date DESC LIMIT 1")
    current_rate = gold_rate[0][0] if gold_rate else 0
    ttk.Label(row2, text=f"Gold Rate (22K): {current_rate:,.2f}/gm", font=("Segoe UI", 9, "bold")).pack(side=tk.RIGHT, padx=10)
    
    items_frame = ttk.LabelFrame(main_frame, text="Items", padding=10)
    items_frame.pack(fill=tk.BOTH, expand=True, pady=5)
    
    add_item_frame = ttk.Frame(items_frame)
    add_item_frame.pack(fill=tk.X, pady=5)
    
    ttk.Label(add_item_frame, text="Item:").pack(side=tk.LEFT, padx=5)
    items_list = fetch_query("""
        SELECT i.id, i.name, i.price, i.quantity, COALESCE(m.name, 'N/A') as material, i.weight_in_gm
        FROM items i
        LEFT JOIN materials m ON i.material_id = m.id
        WHERE i.is_active=1 ORDER BY i.name
    """)
    item_combo = ttk.Combobox(add_item_frame, values=[f"{i[1]} [{i[4]}] ({i[2]:,.0f})" for i in items_list], width=35)
    item_combo.pack(side=tk.LEFT, padx=5)
    item_data = {f"{i[1]} [{i[4]}] ({i[2]:,.0f})": {'id': i[0], 'name': i[1], 'price': i[2], 'stock': i[3], 'material': i[4], 'weight': i[5]} for i in items_list}
    
    ttk.Label(add_item_frame, text="Qty:").pack(side=tk.LEFT, padx=5)
    qty_entry = ttk.Entry(add_item_frame, width=6)
    qty_entry.insert(0, "1")
    qty_entry.pack(side=tk.LEFT, padx=5)
    
    ttk.Label(add_item_frame, text="Price:").pack(side=tk.LEFT, padx=5)
    price_entry = ttk.Entry(add_item_frame, width=10)
    price_entry.pack(side=tk.LEFT, padx=5)
    
    ttk.Label(add_item_frame, text="Weight:").pack(side=tk.LEFT, padx=5)
    weight_entry = ttk.Entry(add_item_frame, width=8)
    weight_entry.insert(0, "0")
    weight_entry.pack(side=tk.LEFT, padx=5)
    
    def on_item_select(event):
        selected = item_combo.get()
        if selected in item_data:
            price_entry.delete(0, tk.END)
            price_entry.insert(0, str(item_data[selected]['price']))
            weight_entry.delete(0, tk.END)
            weight_entry.insert(0, str(item_data[selected]['weight'] or 0))
    
    item_combo.bind('<<ComboboxSelected>>', on_item_select)
    
    columns = ('Item', 'Material', 'Qty', 'Price', 'Weight', 'Total')
    items_tree = ttk.Treeview(items_frame, columns=columns, height=8, show='headings')
    
    for col in columns:
        items_tree.heading(col, text=col)
        items_tree.column(col, width=100 if col != 'Item' else 180)
    
    items_tree.pack(fill=tk.BOTH, expand=True, pady=5)
    
    bill_items = []
    
    def add_item():
        selected = item_combo.get()
        if not selected or selected not in item_data:
            messagebox.showwarning("Warning", "Please select an item!")
            return
        
        try:
            qty = float(qty_entry.get())
            price = float(price_entry.get())
            weight = float(weight_entry.get() or 0)
        except ValueError:
            messagebox.showerror("Error", "Invalid quantity or price!")
            return
        
        if qty <= 0 or price <= 0:
            messagebox.showwarning("Warning", "Quantity and price must be positive!")
            return
        
        item_info = item_data[selected]
        
        if bill_type == 'Sales' and qty > item_info['stock']:
            if not messagebox.askyesno("Stock Warning", f"Available stock: {item_info['stock']}\nYou're adding: {qty}\n\nProceed anyway?"):
                return
        
        total = qty * price
        
        bill_items.append({
            'item_id': item_info['id'],
            'name': item_info['name'],
            'material': item_info['material'],
            'quantity': qty,
            'unit_price': price,
            'weight': weight,
            'line_total': total
        })
        
        items_tree.insert('', 'end', values=(item_info['name'], item_info['material'], qty, f"{price:,.2f}", f"{weight:.3f}", f"{total:,.2f}"))
        update_totals()
        
        item_combo.set("")
        qty_entry.delete(0, tk.END)
        qty_entry.insert(0, "1")
        price_entry.delete(0, tk.END)
        weight_entry.delete(0, tk.END)
        weight_entry.insert(0, "0")
    
    def remove_item():
        selected = items_tree.selection()
        if not selected:
            return
        idx = items_tree.index(selected[0])
        items_tree.delete(selected[0])
        del bill_items[idx]
        update_totals()
    
    btn_frame = ttk.Frame(items_frame)
    btn_frame.pack(fill=tk.X)
    ttk.Button(btn_frame, text="Add Item", command=add_item).pack(side=tk.LEFT, padx=5)
    ttk.Button(btn_frame, text="Remove Selected", command=remove_item).pack(side=tk.LEFT, padx=5)
    
    totals_frame = ttk.LabelFrame(main_frame, text="Totals & Payment", padding=10)
    totals_frame.pack(fill=tk.X, pady=5)
    
    totals_row = ttk.Frame(totals_frame)
    totals_row.pack(fill=tk.X)
    
    subtotal_var = tk.StringVar(value="0.00")
    discount_var = tk.StringVar(value="0")
    tax_var = tk.StringVar(value="3")
    making_var = tk.StringVar(value="0")
    total_var = tk.StringVar(value="0.00")
    paid_var = tk.StringVar(value="0")
    
    ttk.Label(totals_row, text="Subtotal:").pack(side=tk.LEFT, padx=5)
    ttk.Label(totals_row, textvariable=subtotal_var, font=("Segoe UI", 10, "bold"), width=12).pack(side=tk.LEFT, padx=5)
    
    ttk.Label(totals_row, text="Discount:").pack(side=tk.LEFT, padx=10)
    discount_entry = ttk.Entry(totals_row, textvariable=discount_var, width=8)
    discount_entry.pack(side=tk.LEFT, padx=5)
    
    ttk.Label(totals_row, text="Tax %:").pack(side=tk.LEFT, padx=10)
    tax_entry = ttk.Entry(totals_row, textvariable=tax_var, width=6)
    tax_entry.pack(side=tk.LEFT, padx=5)
    
    ttk.Label(totals_row, text="Making:").pack(side=tk.LEFT, padx=10)
    making_entry = ttk.Entry(totals_row, textvariable=making_var, width=8)
    making_entry.pack(side=tk.LEFT, padx=5)
    
    ttk.Label(totals_row, text="TOTAL:").pack(side=tk.LEFT, padx=15)
    ttk.Label(totals_row, textvariable=total_var, font=("Segoe UI", 12, "bold")).pack(side=tk.LEFT, padx=5)
    
    pay_row = ttk.Frame(totals_frame)
    pay_row.pack(fill=tk.X, pady=10)
    
    ttk.Label(pay_row, text="Amount Paid:").pack(side=tk.LEFT, padx=5)
    paid_entry = ttk.Entry(pay_row, textvariable=paid_var, width=12)
    paid_entry.pack(side=tk.LEFT, padx=5)
    
    ttk.Label(pay_row, text="Remarks:").pack(side=tk.LEFT, padx=20)
    remarks_entry = ttk.Entry(pay_row, width=40)
    remarks_entry.pack(side=tk.LEFT, padx=5)
    
    def update_totals(*args):
        subtotal = sum(item['line_total'] for item in bill_items)
        subtotal_var.set(f"{subtotal:,.2f}")
        
        try:
            discount = float(discount_var.get() or 0)
            tax_percent = float(tax_var.get() or 0)
            making = float(making_var.get() or 0)
        except:
            discount = 0
            tax_percent = 0
            making = 0
        
        after_discount = subtotal - discount + making
        tax_amount = after_discount * (tax_percent / 100)
        total = after_discount + tax_amount
        total_var.set(f"{total:,.2f}")
    
    discount_var.trace('w', update_totals)
    tax_var.trace('w', update_totals)
    making_var.trace('w', update_totals)
    
    def save_bill():
        if not bill_items:
            messagebox.showwarning("Warning", "Please add at least one item!")
            return
        
        employee_name = employee_var.get()
        if not employee_name:
            messagebox.showwarning("Warning", "Please select an employee who handled this transaction!")
            return
        
        employee_id = employee_data.get(employee_name)
        
        party_selected = party_combo.get()
        party_id = None
        
        if bill_type == 'Sales':
            if party_selected and party_selected != 'Walk-in Customer':
                party_id = party_data.get(party_selected)
                if not party_id:
                    customer_name = party_selected.split(' (')[0] if ' (' in party_selected else party_selected
                    party_id = get_or_create_customer(customer_name)
        else:
            party_id = party_data.get(party_selected) if party_selected else None
        
        try:
            discount = float(discount_var.get() or 0)
            tax_percent = float(tax_var.get() or 0)
            making = float(making_var.get() or 0)
            paid = float(paid_var.get() or 0)
        except ValueError:
            messagebox.showerror("Error", "Invalid amount values!")
            return
        
        subtotal = sum(item['line_total'] for item in bill_items)
        total_weight = sum(item['weight'] for item in bill_items)
        after_discount = subtotal - discount + making
        tax_amount = after_discount * (tax_percent / 100)
        total = after_discount + tax_amount
        outstanding = total - paid
        
        bill_number = f"{'SB' if bill_type == 'Sales' else 'PB'}-{datetime.now().strftime('%Y%m%d')}-{uuid.uuid4().hex[:6].upper()}"
        
        status = 'Completed' if outstanding <= 0 else 'Pending'
        
        try:
            if bill_type == 'Sales':
                bill_id = execute_query("""
                    INSERT INTO bills (bill_number, bill_type, customer_id, employee_id, bill_date, 
                                      total_amount, total_weight, discount_amount, tax_amount, 
                                      making_charges, paid_amount, outstanding_amount, payment_mode,
                                      status, remarks, date_created, date_modified)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    bill_number, bill_type, party_id, employee_id, date_entry.get(), total,
                    total_weight, discount, tax_amount, making, paid, outstanding, 
                    payment_mode.get(), status, remarks_entry.get() or None, 
                    datetime.now(), datetime.now()
                ))
            else:
                bill_id = execute_query("""
                    INSERT INTO bills (bill_number, bill_type, supplier_id, employee_id, bill_date, 
                                      total_amount, total_weight, discount_amount, tax_amount, 
                                      making_charges, paid_amount, outstanding_amount, payment_mode,
                                      status, remarks, date_created, date_modified)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    bill_number, bill_type, party_id, employee_id, date_entry.get(), total,
                    total_weight, discount, tax_amount, making, paid, outstanding, 
                    payment_mode.get(), status, remarks_entry.get() or None, 
                    datetime.now(), datetime.now()
                ))
            
            for item in bill_items:
                execute_query("""
                    INSERT INTO bill_items (bill_id, item_id, quantity, unit_price, line_total, weight_in_gm)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (bill_id, item['item_id'], item['quantity'], item['unit_price'], item['line_total'], item['weight']))
                
                if bill_type == 'Sales':
                    execute_query("UPDATE items SET quantity = quantity - ? WHERE id = ?", (item['quantity'], item['item_id']))
                else:
                    execute_query("UPDATE items SET quantity = quantity + ? WHERE id = ?", (item['quantity'], item['item_id']))
            
            if party_id and bill_type == 'Sales' and outstanding > 0:
                execute_query("""
                    UPDATE customers SET outstanding_balance = outstanding_balance + ?, date_modified = ?
                    WHERE id = ?
                """, (outstanding, datetime.now(), party_id))
            
            messagebox.showinfo("Success", f"Bill {bill_number} created successfully!\n\nTotal: {total:,.2f}\nPaid: {paid:,.2f}\nOutstanding: {outstanding:,.2f}")
            dialog.destroy()
            if bills_tree:
                refresh_bills_list(bills_tree)
        except Exception as e:
            messagebox.showerror("Error", f"Error creating bill: {str(e)}")
    
    action_frame = ttk.Frame(main_frame)
    action_frame.pack(pady=10)
    
    ttk.Button(action_frame, text="Save Bill", command=save_bill, width=15).pack(side=tk.LEFT, padx=10)
    ttk.Button(action_frame, text="Cancel", command=dialog.destroy, width=15).pack(side=tk.LEFT, padx=10)

def show_quick_add_customer(customer_combo, party_data):
    dialog = tk.Toplevel()
    dialog.title("Quick Add Customer")
    dialog.geometry("350x250")
    dialog.transient(customer_combo.winfo_toplevel())
    dialog.grab_set()
    
    main_frame = ttk.Frame(dialog, padding=20)
    main_frame.pack(fill=tk.BOTH, expand=True)
    
    ttk.Label(main_frame, text="Add New Customer", font=("Segoe UI", 12, "bold")).pack(pady=10)
    
    form_frame = ttk.Frame(main_frame)
    form_frame.pack(fill=tk.X)
    
    ttk.Label(form_frame, text="Name *:").grid(row=0, column=0, sticky='w', pady=5)
    name_entry = ttk.Entry(form_frame, width=30)
    name_entry.grid(row=0, column=1, pady=5, padx=5)
    
    ttk.Label(form_frame, text="Phone:").grid(row=1, column=0, sticky='w', pady=5)
    phone_entry = ttk.Entry(form_frame, width=30)
    phone_entry.grid(row=1, column=1, pady=5, padx=5)
    
    ttk.Label(form_frame, text="Email:").grid(row=2, column=0, sticky='w', pady=5)
    email_entry = ttk.Entry(form_frame, width=30)
    email_entry.grid(row=2, column=1, pady=5, padx=5)
    
    def save_customer():
        name = name_entry.get().strip()
        if not name:
            messagebox.showwarning("Validation", "Customer name is required!")
            return
        
        phone = phone_entry.get().strip() or None
        email = email_entry.get().strip() or None
        
        try:
            customer_id = execute_query("""
                INSERT INTO customers (name, phone, email, date_created, date_modified)
                VALUES (?, ?, ?, ?, ?)
            """, (name, phone, email, datetime.now(), datetime.now()))
            
            new_value = f"{name} ({phone or 'No Phone'})"
            current_values = list(customer_combo['values'])
            current_values.append(new_value)
            customer_combo['values'] = current_values
            customer_combo.set(new_value)
            party_data[new_value] = customer_id
            
            messagebox.showinfo("Success", "Customer added successfully!")
            dialog.destroy()
        except Exception as e:
            messagebox.showerror("Error", f"Error adding customer: {str(e)}")
    
    btn_frame = ttk.Frame(main_frame)
    btn_frame.pack(pady=15)
    
    ttk.Button(btn_frame, text="Save", command=save_customer, width=12).pack(side=tk.LEFT, padx=5)
    ttk.Button(btn_frame, text="Cancel", command=dialog.destroy, width=12).pack(side=tk.LEFT, padx=5)

def add_payment_dialog(tree):
    selected = tree.selection()
    if not selected:
        messagebox.showwarning("Warning", "Please select a bill to add payment!")
        return
    
    bill_id = tree.item(selected[0])['values'][0]
    bill_num = tree.item(selected[0])['values'][1]
    outstanding = float(tree.item(selected[0])['values'][8].replace(',', ''))
    
    if outstanding <= 0:
        messagebox.showinfo("Info", "This bill is fully paid!")
        return
    
    dialog = tk.Toplevel()
    dialog.title(f"Add Payment - {bill_num}")
    dialog.geometry("350x250")
    dialog.grab_set()
    
    main_frame = ttk.Frame(dialog, padding=20)
    main_frame.pack(fill=tk.BOTH, expand=True)
    
    ttk.Label(main_frame, text=f"Outstanding: {outstanding:,.2f}", font=("Segoe UI", 12, "bold")).pack(pady=10)
    
    ttk.Label(main_frame, text="Payment Amount:").pack(pady=5)
    amount_entry = ttk.Entry(main_frame, width=20)
    amount_entry.insert(0, str(outstanding))
    amount_entry.pack(pady=5)
    
    ttk.Label(main_frame, text="Payment Mode:").pack(pady=5)
    mode_combo = ttk.Combobox(main_frame, values=['Cash', 'Card', 'UPI', 'Bank Transfer', 'Cheque'], width=18)
    mode_combo.set('Cash')
    mode_combo.pack(pady=5)
    
    def save_payment():
        try:
            amount = float(amount_entry.get())
        except:
            messagebox.showerror("Error", "Invalid amount!")
            return
        
        if amount <= 0:
            messagebox.showerror("Error", "Amount must be positive!")
            return
        
        new_outstanding = outstanding - amount
        new_status = 'Completed' if new_outstanding <= 0 else 'Pending'
        
        try:
            execute_query("""
                UPDATE bills SET paid_amount = paid_amount + ?, outstanding_amount = ?,
                                 status = ?, date_modified = ? WHERE id = ?
            """, (amount, max(0, new_outstanding), new_status, datetime.now(), bill_id))
            
            execute_query("""
                INSERT INTO payments (payment_type, payment_date, amount, payment_mode, 
                                     reference_type, reference_id, description, date_created)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, ('Receipt', datetime.now().date(), amount, mode_combo.get(), 
                  'Bill', bill_id, f"Payment for {bill_num}", datetime.now()))
            
            messagebox.showinfo("Success", f"Payment of {amount:,.2f} recorded!")
            dialog.destroy()
            refresh_bills_list(tree)
        except Exception as e:
            messagebox.showerror("Error", f"Error: {str(e)}")
    
    ttk.Button(main_frame, text="Save Payment", command=save_payment).pack(pady=15)

def view_bill_details(tree):
    selected = tree.selection()
    if not selected:
        messagebox.showwarning("Warning", "Please select a bill to view!")
        return
    
    bill_id = tree.item(selected[0])['values'][0]
    
    bill = fetch_one("""
        SELECT b.*, c.name as customer_name, s.name as supplier_name, e.name as employee_name
        FROM bills b
        LEFT JOIN customers c ON b.customer_id = c.id
        LEFT JOIN suppliers s ON b.supplier_id = s.id
        LEFT JOIN employees e ON b.employee_id = e.id
        WHERE b.id = ?
    """, (bill_id,))
    
    if not bill:
        messagebox.showerror("Error", "Bill not found!")
        return
    
    items = fetch_query("""
        SELECT i.name, bi.quantity, bi.unit_price, bi.line_total, bi.weight_in_gm
        FROM bill_items bi
        JOIN items i ON bi.item_id = i.id
        WHERE bi.bill_id = ?
    """, (bill_id,))
    
    items_str = "\n".join([f"  - {i[0]}: {i[1]} x {i[2]:,.2f} = {i[3]:,.2f}" for i in items])
    party = bill['customer_name'] if bill['bill_type'] == 'Sales' else bill['supplier_name']
    
    details = f"""
BILL DETAILS
{'='*50}

Bill Number: {bill['bill_number']}
Type: {bill['bill_type']}
{'Customer' if bill['bill_type'] == 'Sales' else 'Supplier'}: {party or 'Walk-in/Unknown'}
Employee: {bill['employee_name'] or 'N/A'}
Date: {bill['bill_date']}
Status: {bill['status']}
Payment Mode: {bill['payment_mode'] or 'N/A'}

ITEMS:
{items_str}

AMOUNTS:
Subtotal: {bill['total_amount']:,.2f}
Discount: {bill['discount_amount']:,.2f}
Tax: {bill['tax_amount']:,.2f}
Making Charges: {bill['making_charges'] or 0:,.2f}
Total: {bill['total_amount']:,.2f}
Paid: {bill['paid_amount']:,.2f}
Outstanding: {bill['outstanding_amount']:,.2f}

Total Weight: {bill['total_weight']:.3f} gm
Remarks: {bill['remarks'] or 'N/A'}
    """
    
    messagebox.showinfo("Bill Details", details)

def cancel_bill(tree):
    selected = tree.selection()
    if not selected:
        messagebox.showwarning("Warning", "Please select a bill to cancel!")
        return
    
    bill_id = tree.item(selected[0])['values'][0]
    bill_num = tree.item(selected[0])['values'][1]
    bill_status = tree.item(selected[0])['values'][9]
    
    if bill_status == 'Cancelled':
        messagebox.showinfo("Info", "This bill is already cancelled!")
        return
    
    if messagebox.askyesno("Confirm Cancel", f"Are you sure you want to cancel bill {bill_num}?\n\nThis will restore the stock quantities."):
        try:
            bill = fetch_one("SELECT bill_type, customer_id, outstanding_amount FROM bills WHERE id = ?", (bill_id,))
            items = fetch_query("SELECT item_id, quantity FROM bill_items WHERE bill_id = ?", (bill_id,))
            
            for item in items:
                if bill['bill_type'] == 'Sales':
                    execute_query("UPDATE items SET quantity = quantity + ? WHERE id = ?", (item[1], item[0]))
                else:
                    execute_query("UPDATE items SET quantity = quantity - ? WHERE id = ?", (item[1], item[0]))
            
            if bill['customer_id'] and bill['bill_type'] == 'Sales':
                execute_query("""
                    UPDATE customers SET outstanding_balance = outstanding_balance - ?, date_modified = ?
                    WHERE id = ?
                """, (bill['outstanding_amount'] or 0, datetime.now(), bill['customer_id']))
            
            execute_query("UPDATE bills SET status = 'Cancelled', date_modified = ? WHERE id = ?", (datetime.now(), bill_id))
            
            messagebox.showinfo("Success", f"Bill {bill_num} has been cancelled!")
            refresh_bills_list(tree)
        except Exception as e:
            messagebox.showerror("Error", f"Error cancelling bill: {str(e)}")
