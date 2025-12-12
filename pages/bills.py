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
    ttk.Button(button_frame, text="Edit Bill", command=lambda: edit_bill(bills_tree)).pack(side=tk.LEFT, padx=5)
    ttk.Button(button_frame, text="Cancel Bill", command=lambda: cancel_bill(bills_tree)).pack(side=tk.LEFT, padx=5)
    ttk.Button(button_frame, text="Refresh", command=lambda: refresh_bills_list(bills_tree)).pack(side=tk.LEFT, padx=5)
    
    tree_frame = ttk.Frame(frame)
    tree_frame.pack(fill=tk.BOTH, expand=True)
    
    columns = ('ID', 'Bill #', 'Type', 'Customer/Supplier', 'Date', 'Total', 'Paid', 'Outstanding', 'Status')
    bills_tree = ttk.Treeview(tree_frame, columns=columns, height=15, show='headings')
    
    col_widths = {'ID': 40, 'Bill #': 120, 'Type': 70, 'Customer/Supplier': 150, 
                  'Date': 90, 'Total': 100, 'Paid': 100, 'Outstanding': 100, 'Status': 80}
    
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
    ttk.Label(status_frame, text=f"Today's Sales: ₹{today_sales:,.2f} | Today's Purchases: ₹{today_purchases:,.2f}").pack(side=tk.LEFT)

def refresh_bills_list(tree, bill_type="All", status="All", search=""):
    if tree is None:
        return
        
    for item in tree.get_children():
        tree.delete(item)
    
    query = """
        SELECT b.id, b.bill_number, b.bill_type, 
               CASE WHEN b.bill_type = 'Sales' THEN COALESCE(c.name, 'Walk-in')
                    ELSE COALESCE(s.name, 'Unknown') END as party,
               b.bill_date, b.total_amount, b.paid_amount, b.outstanding_amount, b.status
        FROM bills b
        LEFT JOIN customers c ON b.customer_id = c.id
        LEFT JOIN suppliers s ON b.supplier_id = s.id
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
            bill[0], bill[1], bill[2], bill[3], bill[4],
            f"₹{bill[5]:,.2f}", f"₹{bill[6]:,.2f}", f"₹{bill[7]:,.2f}", bill[8]
        )
        tree.insert('', 'end', values=formatted)

def show_new_bill_dialog(parent, bill_type):
    dialog = tk.Toplevel(parent)
    dialog.title(f"New {bill_type} Bill")
    dialog.geometry("900x700")
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
        customers = fetch_query("SELECT id, name FROM customers ORDER BY name")
        customer_var = ttk.Combobox(row1, values=[f"{c[1]} (ID:{c[0]})" for c in customers], width=30)
        customer_var.pack(side=tk.LEFT, padx=5)
        party_combo = customer_var
        party_data = {f"{c[1]} (ID:{c[0]})": c[0] for c in customers}
    else:
        ttk.Label(row1, text="Supplier:").pack(side=tk.LEFT, padx=5)
        suppliers = fetch_query("SELECT id, name FROM suppliers ORDER BY name")
        supplier_var = ttk.Combobox(row1, values=[f"{s[1]} (ID:{s[0]})" for s in suppliers], width=30)
        supplier_var.pack(side=tk.LEFT, padx=5)
        party_combo = supplier_var
        party_data = {f"{s[1]} (ID:{s[0]})": s[0] for s in suppliers}
    
    ttk.Label(row1, text="Date:").pack(side=tk.LEFT, padx=20)
    date_entry = ttk.Entry(row1, width=15)
    date_entry.insert(0, datetime.now().strftime('%Y-%m-%d'))
    date_entry.pack(side=tk.LEFT, padx=5)
    
    gold_rate = fetch_query("SELECT rate_per_gram FROM gold_rates WHERE purity='22K' AND is_active=1 ORDER BY rate_date DESC LIMIT 1")
    current_rate = gold_rate[0][0] if gold_rate else 0
    ttk.Label(row1, text=f"Gold Rate (22K): ₹{current_rate:,.2f}/gm").pack(side=tk.RIGHT, padx=10)
    
    items_frame = ttk.LabelFrame(main_frame, text="Items", padding=10)
    items_frame.pack(fill=tk.BOTH, expand=True, pady=5)
    
    add_item_frame = ttk.Frame(items_frame)
    add_item_frame.pack(fill=tk.X, pady=5)
    
    ttk.Label(add_item_frame, text="Item:").pack(side=tk.LEFT, padx=5)
    items_list = fetch_query("SELECT id, name, price, quantity FROM items WHERE is_active=1 ORDER BY name")
    item_combo = ttk.Combobox(add_item_frame, values=[f"{i[1]} (₹{i[2]:,.2f})" for i in items_list], width=30)
    item_combo.pack(side=tk.LEFT, padx=5)
    item_data = {f"{i[1]} (₹{i[2]:,.2f})": {'id': i[0], 'name': i[1], 'price': i[2], 'stock': i[3]} for i in items_list}
    
    ttk.Label(add_item_frame, text="Qty:").pack(side=tk.LEFT, padx=5)
    qty_entry = ttk.Entry(add_item_frame, width=8)
    qty_entry.insert(0, "1")
    qty_entry.pack(side=tk.LEFT, padx=5)
    
    ttk.Label(add_item_frame, text="Price:").pack(side=tk.LEFT, padx=5)
    price_entry = ttk.Entry(add_item_frame, width=12)
    price_entry.pack(side=tk.LEFT, padx=5)
    
    ttk.Label(add_item_frame, text="Weight(gm):").pack(side=tk.LEFT, padx=5)
    weight_entry = ttk.Entry(add_item_frame, width=10)
    weight_entry.insert(0, "0")
    weight_entry.pack(side=tk.LEFT, padx=5)
    
    def on_item_select(event):
        selected = item_combo.get()
        if selected in item_data:
            price_entry.delete(0, tk.END)
            price_entry.insert(0, str(item_data[selected]['price']))
    
    item_combo.bind('<<ComboboxSelected>>', on_item_select)
    
    columns = ('Item', 'Qty', 'Price', 'Weight', 'Total')
    items_tree = ttk.Treeview(items_frame, columns=columns, height=8, show='headings')
    
    for col in columns:
        items_tree.heading(col, text=col)
        items_tree.column(col, width=120)
    
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
        total = qty * price
        
        bill_items.append({
            'item_id': item_info['id'],
            'name': item_info['name'],
            'quantity': qty,
            'unit_price': price,
            'weight': weight,
            'line_total': total
        })
        
        items_tree.insert('', 'end', values=(item_info['name'], qty, f"₹{price:,.2f}", f"{weight} gm", f"₹{total:,.2f}"))
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
    
    totals_frame = ttk.LabelFrame(main_frame, text="Totals", padding=10)
    totals_frame.pack(fill=tk.X, pady=5)
    
    totals_row = ttk.Frame(totals_frame)
    totals_row.pack(fill=tk.X)
    
    subtotal_var = tk.StringVar(value="₹0.00")
    discount_var = tk.StringVar(value="0")
    tax_var = tk.StringVar(value="0")
    total_var = tk.StringVar(value="₹0.00")
    paid_var = tk.StringVar(value="0")
    
    ttk.Label(totals_row, text="Subtotal:").pack(side=tk.LEFT, padx=5)
    ttk.Label(totals_row, textvariable=subtotal_var, font=("Segoe UI", 10, "bold")).pack(side=tk.LEFT, padx=5)
    
    ttk.Label(totals_row, text="Discount:").pack(side=tk.LEFT, padx=20)
    discount_entry = ttk.Entry(totals_row, textvariable=discount_var, width=10)
    discount_entry.pack(side=tk.LEFT, padx=5)
    
    ttk.Label(totals_row, text="Tax %:").pack(side=tk.LEFT, padx=10)
    tax_entry = ttk.Entry(totals_row, textvariable=tax_var, width=8)
    tax_entry.pack(side=tk.LEFT, padx=5)
    
    ttk.Label(totals_row, text="Total:").pack(side=tk.LEFT, padx=20)
    ttk.Label(totals_row, textvariable=total_var, font=("Segoe UI", 12, "bold")).pack(side=tk.LEFT, padx=5)
    
    pay_row = ttk.Frame(totals_frame)
    pay_row.pack(fill=tk.X, pady=10)
    
    ttk.Label(pay_row, text="Amount Paid:").pack(side=tk.LEFT, padx=5)
    paid_entry = ttk.Entry(pay_row, textvariable=paid_var, width=15)
    paid_entry.pack(side=tk.LEFT, padx=5)
    
    ttk.Label(pay_row, text="Remarks:").pack(side=tk.LEFT, padx=20)
    remarks_entry = ttk.Entry(pay_row, width=40)
    remarks_entry.pack(side=tk.LEFT, padx=5)
    
    def update_totals(*args):
        subtotal = sum(item['line_total'] for item in bill_items)
        subtotal_var.set(f"₹{subtotal:,.2f}")
        
        try:
            discount = float(discount_var.get() or 0)
            tax_percent = float(tax_var.get() or 0)
        except:
            discount = 0
            tax_percent = 0
        
        tax_amount = (subtotal - discount) * (tax_percent / 100)
        total = subtotal - discount + tax_amount
        total_var.set(f"₹{total:,.2f}")
    
    discount_var.trace('w', update_totals)
    tax_var.trace('w', update_totals)
    
    def save_bill():
        if not bill_items:
            messagebox.showwarning("Warning", "Please add at least one item!")
            return
        
        party_selected = party_combo.get()
        party_id = party_data.get(party_selected) if party_selected else None
        
        try:
            discount = float(discount_var.get() or 0)
            tax_percent = float(tax_var.get() or 0)
            paid = float(paid_var.get() or 0)
        except ValueError:
            messagebox.showerror("Error", "Invalid amount values!")
            return
        
        subtotal = sum(item['line_total'] for item in bill_items)
        total_weight = sum(item['weight'] for item in bill_items)
        tax_amount = (subtotal - discount) * (tax_percent / 100)
        total = subtotal - discount + tax_amount
        outstanding = total - paid
        
        bill_number = f"{'SB' if bill_type == 'Sales' else 'PB'}-{datetime.now().strftime('%Y%m%d')}-{uuid.uuid4().hex[:6].upper()}"
        
        status = 'Completed' if outstanding <= 0 else 'Pending'
        
        try:
            if bill_type == 'Sales':
                bill_id = execute_query("""
                    INSERT INTO bills (bill_number, bill_type, customer_id, bill_date, total_amount, 
                                      total_weight, discount_amount, tax_amount, paid_amount, 
                                      outstanding_amount, status, remarks, date_created, date_modified)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    bill_number, bill_type, party_id, date_entry.get(), total,
                    total_weight, discount, tax_amount, paid, outstanding, status,
                    remarks_entry.get() or None, datetime.now(), datetime.now()
                ))
            else:
                bill_id = execute_query("""
                    INSERT INTO bills (bill_number, bill_type, supplier_id, bill_date, total_amount, 
                                      total_weight, discount_amount, tax_amount, paid_amount, 
                                      outstanding_amount, status, remarks, date_created, date_modified)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    bill_number, bill_type, party_id, date_entry.get(), total,
                    total_weight, discount, tax_amount, paid, outstanding, status,
                    remarks_entry.get() or None, datetime.now(), datetime.now()
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
            
            messagebox.showinfo("Success", f"Bill {bill_number} created successfully!\n\nTotal: ₹{total:,.2f}\nPaid: ₹{paid:,.2f}\nOutstanding: ₹{outstanding:,.2f}")
            dialog.destroy()
            if bills_tree:
                refresh_bills_list(bills_tree)
        except Exception as e:
            messagebox.showerror("Error", f"Error creating bill: {str(e)}")
    
    action_frame = ttk.Frame(main_frame)
    action_frame.pack(pady=10)
    
    ttk.Button(action_frame, text="Save Bill", command=save_bill, width=15).pack(side=tk.LEFT, padx=10)
    ttk.Button(action_frame, text="Cancel", command=dialog.destroy, width=15).pack(side=tk.LEFT, padx=10)

def view_bill_details(tree):
    selected = tree.selection()
    if not selected:
        messagebox.showwarning("Warning", "Please select a bill to view!")
        return
    
    bill_id = tree.item(selected[0])['values'][0]
    
    bill = fetch_one("""
        SELECT b.*, c.name as customer_name, s.name as supplier_name
        FROM bills b
        LEFT JOIN customers c ON b.customer_id = c.id
        LEFT JOIN suppliers s ON b.supplier_id = s.id
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
    
    items_str = "\n".join([f"  - {i[0]}: {i[1]} x ₹{i[2]:,.2f} = ₹{i[3]:,.2f}" for i in items])
    party = bill['customer_name'] if bill[3] == 'Sales' else bill['supplier_name']
    
    details = f"""
BILL DETAILS
{'='*50}

Bill Number: {bill[1]}
Type: {bill[2]}
{'Customer' if bill[2] == 'Sales' else 'Supplier'}: {party or 'Walk-in/Unknown'}
Date: {bill[6]}
Status: {bill[13]}

ITEMS:
{items_str}

AMOUNTS:
Subtotal: ₹{bill[7]:,.2f}
Discount: ₹{bill[9]:,.2f}
Tax: ₹{bill[10]:,.2f}
Total: ₹{bill[7]:,.2f}
Paid: ₹{bill[11]:,.2f}
Outstanding: ₹{bill[12]:,.2f}

Total Weight: {bill[8]} gm
Remarks: {bill[14] or 'N/A'}
    """
    
    messagebox.showinfo("Bill Details", details)

def edit_bill(tree):
    selected = tree.selection()
    if not selected:
        messagebox.showwarning("Warning", "Please select a bill to edit!")
        return
    
    bill_status = tree.item(selected[0])['values'][8]
    if bill_status == 'Cancelled':
        messagebox.showwarning("Warning", "Cannot edit a cancelled bill!")
        return
    
    messagebox.showinfo("Edit Bill", "Bill editing feature - Use payment update for now")

def cancel_bill(tree):
    selected = tree.selection()
    if not selected:
        messagebox.showwarning("Warning", "Please select a bill to cancel!")
        return
    
    bill_id = tree.item(selected[0])['values'][0]
    bill_num = tree.item(selected[0])['values'][1]
    bill_status = tree.item(selected[0])['values'][8]
    
    if bill_status == 'Cancelled':
        messagebox.showinfo("Info", "This bill is already cancelled!")
        return
    
    if messagebox.askyesno("Confirm Cancel", f"Are you sure you want to cancel bill {bill_num}?\n\nThis will restore the stock quantities."):
        try:
            bill = fetch_one("SELECT bill_type FROM bills WHERE id = ?", (bill_id,))
            items = fetch_query("SELECT item_id, quantity FROM bill_items WHERE bill_id = ?", (bill_id,))
            
            for item in items:
                if bill[0] == 'Sales':
                    execute_query("UPDATE items SET quantity = quantity + ? WHERE id = ?", (item[1], item[0]))
                else:
                    execute_query("UPDATE items SET quantity = quantity - ? WHERE id = ?", (item[1], item[0]))
            
            execute_query("UPDATE bills SET status = 'Cancelled', date_modified = ? WHERE id = ?", (datetime.now(), bill_id))
            
            messagebox.showinfo("Success", f"Bill {bill_num} has been cancelled!")
            refresh_bills_list(tree)
        except Exception as e:
            messagebox.showerror("Error", f"Error cancelling bill: {str(e)}")
