import tkinter as tk
from tkinter import messagebox, ttk
from database.db import execute_query, fetch_query, fetch_one
from datetime import datetime, date, timedelta
from services.advance_order_service import AdvanceOrderService

orders_tree = None

def advance_orders_page(parent):
    global orders_tree
    
    for widget in parent.winfo_children():
        widget.destroy()
    
    frame = ttk.Frame(parent)
    frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    
    title_frame = ttk.Frame(frame)
    title_frame.pack(fill=tk.X, pady=10)
    
    title_label = ttk.Label(title_frame, text="Advance Orders / Custom Bookings", font=("Segoe UI", 16, "bold"))
    title_label.pack(side=tk.LEFT)
    
    summary = AdvanceOrderService.get_orders_summary()
    summary_text = f"Pending: {summary['pending']} | In Progress: {summary['in_progress']} | Ready: {summary['ready']} | Overdue: {summary['overdue']}"
    ttk.Label(title_frame, text=summary_text, font=("Segoe UI", 9)).pack(side=tk.RIGHT)
    
    filter_frame = ttk.Frame(frame)
    filter_frame.pack(fill=tk.X, pady=5)
    
    ttk.Label(filter_frame, text="Status:").pack(side=tk.LEFT, padx=5)
    status_var = tk.StringVar(value="All")
    status_combo = ttk.Combobox(filter_frame, textvariable=status_var, 
                                values=['All'] + AdvanceOrderService.STATUSES, width=12)
    status_combo.pack(side=tk.LEFT, padx=5)
    
    ttk.Label(filter_frame, text="Search:").pack(side=tk.LEFT, padx=10)
    search_var = tk.StringVar()
    search_entry = ttk.Entry(filter_frame, textvariable=search_var, width=20)
    search_entry.pack(side=tk.LEFT, padx=5)
    
    def apply_filter():
        refresh_orders_list(orders_tree, status_var.get())
    
    ttk.Button(filter_frame, text="Filter", command=apply_filter).pack(side=tk.LEFT, padx=5)
    ttk.Button(filter_frame, text="Clear", command=lambda: [status_var.set("All"), refresh_orders_list(orders_tree)]).pack(side=tk.LEFT, padx=5)
    
    button_frame = ttk.Frame(frame)
    button_frame.pack(fill=tk.X, pady=10)
    
    ttk.Button(button_frame, text="New Order", command=lambda: show_new_order_dialog(parent)).pack(side=tk.LEFT, padx=5)
    ttk.Button(button_frame, text="View Order", command=lambda: view_order_details(orders_tree)).pack(side=tk.LEFT, padx=5)
    ttk.Button(button_frame, text="Update Status", command=lambda: update_order_status_dialog(orders_tree)).pack(side=tk.LEFT, padx=5)
    ttk.Button(button_frame, text="Add Payment", command=lambda: add_advance_payment(orders_tree)).pack(side=tk.LEFT, padx=5)
    ttk.Button(button_frame, text="Convert to Bill", command=lambda: convert_to_bill(parent, orders_tree)).pack(side=tk.LEFT, padx=5)
    ttk.Button(button_frame, text="Cancel Order", command=lambda: cancel_order(orders_tree)).pack(side=tk.LEFT, padx=5)
    ttk.Button(button_frame, text="Refresh", command=lambda: refresh_orders_list(orders_tree)).pack(side=tk.LEFT, padx=5)
    
    tree_frame = ttk.Frame(frame)
    tree_frame.pack(fill=tk.BOTH, expand=True)
    
    columns = ('ID', 'Order #', 'Customer', 'Order Date', 'Delivery Date', 'Material', 'Estimated', 'Advance', 'Status', 'Priority')
    orders_tree = ttk.Treeview(tree_frame, columns=columns, height=15, show='headings')
    
    col_widths = {'ID': 40, 'Order #': 130, 'Customer': 130, 'Order Date': 90, 'Delivery Date': 90,
                  'Material': 70, 'Estimated': 90, 'Advance': 80, 'Status': 80, 'Priority': 70}
    
    for col in columns:
        orders_tree.column(col, width=col_widths.get(col, 100), anchor='center')
        orders_tree.heading(col, text=col)
    
    scrollbar_y = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=orders_tree.yview)
    orders_tree.configure(yscroll=scrollbar_y.set)
    
    orders_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y)
    
    orders_tree.bind('<Double-1>', lambda e: view_order_details(orders_tree))
    
    refresh_orders_list(orders_tree)
    
    status_frame = ttk.Frame(frame)
    status_frame.pack(fill=tk.X, pady=5)
    
    total_advance = fetch_query("""
        SELECT COALESCE(SUM(advance_amount), 0) FROM advance_orders 
        WHERE status NOT IN ('Delivered', 'Cancelled')
    """)[0][0]
    ttk.Label(status_frame, text=f"Total Advance Collected (Pending Orders): {total_advance:,.2f}").pack(side=tk.LEFT)

def refresh_orders_list(tree, status="All"):
    if tree is None:
        return
    
    for item in tree.get_children():
        tree.delete(item)
    
    orders = AdvanceOrderService.get_all_orders(status)
    
    for order in orders:
        is_overdue = order[4] and str(order[4]) < str(date.today()) and order[8] not in ('Delivered', 'Cancelled')
        formatted = (
            order[0], order[1], order[2], order[3], order[4] or 'N/A',
            order[5], f"{order[6]:,.2f}" if order[6] else "0.00",
            f"{order[7]:,.2f}" if order[7] else "0.00",
            order[8] + (' (!)' if is_overdue else ''), order[9]
        )
        tree.insert('', 'end', values=formatted)

def show_new_order_dialog(parent):
    dialog = tk.Toplevel(parent)
    dialog.title("New Advance Order")
    dialog.geometry("600x650")
    dialog.transient(parent)
    dialog.grab_set()
    
    main_frame = ttk.Frame(dialog, padding=15)
    main_frame.pack(fill=tk.BOTH, expand=True)
    
    ttk.Label(main_frame, text="New Advance Order / Custom Booking", font=("Segoe UI", 14, "bold")).pack(pady=10)
    
    form_frame = ttk.Frame(main_frame)
    form_frame.pack(fill=tk.X)
    
    customers = fetch_query("SELECT id, name, phone FROM customers ORDER BY name")
    employees = fetch_query("SELECT id, name FROM employees WHERE status = 'Active' ORDER BY name")
    
    row = 0
    ttk.Label(form_frame, text="Customer *:").grid(row=row, column=0, sticky='w', pady=5)
    customer_combo = ttk.Combobox(form_frame, values=[f"{c[1]} ({c[2] or 'No Phone'})" for c in customers], width=35)
    customer_combo.grid(row=row, column=1, pady=5, padx=5)
    customer_data = {f"{c[1]} ({c[2] or 'No Phone'})": c[0] for c in customers}
    
    row += 1
    ttk.Label(form_frame, text="Employee:").grid(row=row, column=0, sticky='w', pady=5)
    employee_combo = ttk.Combobox(form_frame, values=[e[1] for e in employees], width=35)
    employee_combo.grid(row=row, column=1, pady=5, padx=5)
    employee_data = {e[1]: e[0] for e in employees}
    
    row += 1
    ttk.Label(form_frame, text="Order Type:").grid(row=row, column=0, sticky='w', pady=5)
    order_type_combo = ttk.Combobox(form_frame, values=AdvanceOrderService.ORDER_TYPES, width=35)
    order_type_combo.set('Custom')
    order_type_combo.grid(row=row, column=1, pady=5, padx=5)
    
    row += 1
    ttk.Label(form_frame, text="Material Type:").grid(row=row, column=0, sticky='w', pady=5)
    material_combo = ttk.Combobox(form_frame, values=['Gold', 'Diamond', 'Gold with Diamond', 'Silver', 'Platinum'], width=35)
    material_combo.set('Gold')
    material_combo.grid(row=row, column=1, pady=5, padx=5)
    
    row += 1
    ttk.Label(form_frame, text="Priority:").grid(row=row, column=0, sticky='w', pady=5)
    priority_combo = ttk.Combobox(form_frame, values=AdvanceOrderService.PRIORITIES, width=35)
    priority_combo.set('Normal')
    priority_combo.grid(row=row, column=1, pady=5, padx=5)
    
    row += 1
    ttk.Label(form_frame, text="Expected Delivery:").grid(row=row, column=0, sticky='w', pady=5)
    delivery_entry = ttk.Entry(form_frame, width=38)
    delivery_entry.insert(0, (date.today() + timedelta(days=15)).strftime('%Y-%m-%d'))
    delivery_entry.grid(row=row, column=1, pady=5, padx=5)
    
    row += 1
    ttk.Label(form_frame, text="Estimated Weight (gm):").grid(row=row, column=0, sticky='w', pady=5)
    weight_entry = ttk.Entry(form_frame, width=38)
    weight_entry.insert(0, "0")
    weight_entry.grid(row=row, column=1, pady=5, padx=5)
    
    row += 1
    ttk.Label(form_frame, text="Estimated Amount:").grid(row=row, column=0, sticky='w', pady=5)
    amount_entry = ttk.Entry(form_frame, width=38)
    amount_entry.insert(0, "0")
    amount_entry.grid(row=row, column=1, pady=5, padx=5)
    
    row += 1
    ttk.Label(form_frame, text="Advance Amount:").grid(row=row, column=0, sticky='w', pady=5)
    advance_entry = ttk.Entry(form_frame, width=38)
    advance_entry.insert(0, "0")
    advance_entry.grid(row=row, column=1, pady=5, padx=5)
    
    row += 1
    ttk.Label(form_frame, text="Assigned Artisan:").grid(row=row, column=0, sticky='w', pady=5)
    artisan_entry = ttk.Entry(form_frame, width=38)
    artisan_entry.grid(row=row, column=1, pady=5, padx=5)
    
    row += 1
    ttk.Label(form_frame, text="Specifications:").grid(row=row, column=0, sticky='nw', pady=5)
    spec_text = tk.Text(form_frame, width=29, height=4)
    spec_text.grid(row=row, column=1, pady=5, padx=5)
    
    row += 1
    ttk.Label(form_frame, text="Design Notes:").grid(row=row, column=0, sticky='nw', pady=5)
    design_text = tk.Text(form_frame, width=29, height=3)
    design_text.grid(row=row, column=1, pady=5, padx=5)
    
    row += 1
    ttk.Label(form_frame, text="Remarks:").grid(row=row, column=0, sticky='w', pady=5)
    remarks_entry = ttk.Entry(form_frame, width=38)
    remarks_entry.grid(row=row, column=1, pady=5, padx=5)
    
    def save_order():
        customer_selected = customer_combo.get()
        if not customer_selected or customer_selected not in customer_data:
            messagebox.showwarning("Validation", "Please select a customer!")
            return
        
        customer_id = customer_data[customer_selected]
        employee_id = employee_data.get(employee_combo.get())
        
        try:
            estimated_weight = float(weight_entry.get() or 0)
            estimated_amount = float(amount_entry.get() or 0)
            advance_amount = float(advance_entry.get() or 0)
        except ValueError:
            messagebox.showerror("Error", "Invalid number format!")
            return
        
        specifications = spec_text.get("1.0", tk.END).strip()
        if not specifications:
            messagebox.showwarning("Validation", "Please provide order specifications!")
            return
        
        try:
            order_id, order_number = AdvanceOrderService.create_order(
                customer_id=customer_id,
                employee_id=employee_id,
                order_type=order_type_combo.get(),
                material_type=material_combo.get(),
                estimated_weight=estimated_weight,
                estimated_amount=estimated_amount,
                advance_amount=advance_amount,
                expected_delivery_date=delivery_entry.get(),
                specifications=specifications,
                design_notes=design_text.get("1.0", tk.END).strip(),
                priority=priority_combo.get(),
                assigned_artisan=artisan_entry.get() or None,
                remarks=remarks_entry.get() or None
            )
            
            if advance_amount > 0:
                execute_query("""
                    INSERT INTO payments (payment_type, payment_date, amount, payment_mode,
                                         reference_type, reference_id, customer_id, description, date_created)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, ('Advance', date.today(), advance_amount, 'Cash', 'Advance Order', order_id,
                      customer_id, f"Advance for order {order_number}", datetime.now()))
            
            messagebox.showinfo("Success", f"Order {order_number} created successfully!\n\nAdvance Received: {advance_amount:,.2f}")
            dialog.destroy()
            if orders_tree:
                refresh_orders_list(orders_tree)
        except Exception as e:
            messagebox.showerror("Error", f"Error creating order: {str(e)}")
    
    btn_frame = ttk.Frame(main_frame)
    btn_frame.pack(pady=15)
    
    ttk.Button(btn_frame, text="Save Order", command=save_order, width=15).pack(side=tk.LEFT, padx=10)
    ttk.Button(btn_frame, text="Cancel", command=dialog.destroy, width=15).pack(side=tk.LEFT, padx=10)

def view_order_details(tree):
    selected = tree.selection()
    if not selected:
        messagebox.showwarning("Warning", "Please select an order to view!")
        return
    
    order_id = tree.item(selected[0])['values'][0]
    order = AdvanceOrderService.get_order(order_id)
    
    if not order:
        messagebox.showerror("Error", "Order not found!")
        return
    
    balance = (order['estimated_amount'] or 0) - (order['advance_amount'] or 0)
    
    details = f"""
ADVANCE ORDER DETAILS
{'='*50}

Order Number: {order['order_number']}
Order Type: {order['order_type']}
Status: {order['status']}
Priority: {order['priority']}

CUSTOMER
Name: {order['customer_name']}
Phone: {order['customer_phone'] or 'N/A'}

DATES
Order Date: {order['order_date']}
Expected Delivery: {order['expected_delivery_date'] or 'N/A'}
Actual Delivery: {order['actual_delivery_date'] or 'Not yet'}

MATERIAL
Type: {order['material_type']}
Estimated Weight: {order['estimated_weight']:.3f} gm

AMOUNTS
Estimated Amount: {order['estimated_amount']:,.2f}
Advance Paid: {order['advance_amount']:,.2f}
Balance Due: {balance:,.2f}

DETAILS
Specifications: {order['specifications'] or 'N/A'}
Design Notes: {order['design_notes'] or 'N/A'}
Assigned Artisan: {order['assigned_artisan'] or 'N/A'}
Remarks: {order['remarks'] or 'N/A'}

Employee: {order['employee_name'] or 'N/A'}
    """
    
    messagebox.showinfo("Order Details", details)

def update_order_status_dialog(tree):
    selected = tree.selection()
    if not selected:
        messagebox.showwarning("Warning", "Please select an order!")
        return
    
    order_id = tree.item(selected[0])['values'][0]
    order_num = tree.item(selected[0])['values'][1]
    current_status = tree.item(selected[0])['values'][8].replace(' (!)', '')
    
    if current_status in ('Delivered', 'Cancelled'):
        messagebox.showinfo("Info", "This order is already completed/cancelled!")
        return
    
    dialog = tk.Toplevel()
    dialog.title(f"Update Status - {order_num}")
    dialog.geometry("300x200")
    dialog.grab_set()
    
    main_frame = ttk.Frame(dialog, padding=20)
    main_frame.pack(fill=tk.BOTH, expand=True)
    
    ttk.Label(main_frame, text=f"Current Status: {current_status}", font=("Segoe UI", 11)).pack(pady=10)
    
    ttk.Label(main_frame, text="New Status:").pack(pady=5)
    status_combo = ttk.Combobox(main_frame, values=AdvanceOrderService.STATUSES, width=20)
    status_combo.pack(pady=5)
    
    ttk.Label(main_frame, text="Remarks:").pack(pady=5)
    remarks_entry = ttk.Entry(main_frame, width=30)
    remarks_entry.pack(pady=5)
    
    def update_status():
        new_status = status_combo.get()
        if not new_status:
            messagebox.showwarning("Validation", "Please select a status!")
            return
        
        try:
            AdvanceOrderService.update_order_status(order_id, new_status, remarks_entry.get() or None)
            messagebox.showinfo("Success", f"Status updated to {new_status}!")
            dialog.destroy()
            refresh_orders_list(tree)
        except Exception as e:
            messagebox.showerror("Error", f"Error: {str(e)}")
    
    ttk.Button(main_frame, text="Update", command=update_status).pack(pady=15)

def add_advance_payment(tree):
    selected = tree.selection()
    if not selected:
        messagebox.showwarning("Warning", "Please select an order!")
        return
    
    order_id = tree.item(selected[0])['values'][0]
    order_num = tree.item(selected[0])['values'][1]
    
    order = AdvanceOrderService.get_order(order_id)
    if not order:
        messagebox.showerror("Error", "Order not found!")
        return
    
    if order['status'] in ('Delivered', 'Cancelled'):
        messagebox.showinfo("Info", "Cannot add payment to completed/cancelled order!")
        return
    
    dialog = tk.Toplevel()
    dialog.title(f"Add Advance Payment - {order_num}")
    dialog.geometry("300x200")
    dialog.grab_set()
    
    main_frame = ttk.Frame(dialog, padding=20)
    main_frame.pack(fill=tk.BOTH, expand=True)
    
    current_advance = order['advance_amount'] or 0
    balance = (order['estimated_amount'] or 0) - current_advance
    
    ttk.Label(main_frame, text=f"Current Advance: {current_advance:,.2f}").pack(pady=5)
    ttk.Label(main_frame, text=f"Balance Due: {balance:,.2f}").pack(pady=5)
    
    ttk.Label(main_frame, text="Additional Amount:").pack(pady=10)
    amount_entry = ttk.Entry(main_frame, width=20)
    amount_entry.pack(pady=5)
    
    def add_payment():
        try:
            amount = float(amount_entry.get())
        except:
            messagebox.showerror("Error", "Invalid amount!")
            return
        
        if amount <= 0:
            messagebox.showerror("Error", "Amount must be positive!")
            return
        
        new_advance = current_advance + amount
        
        try:
            execute_query("""
                UPDATE advance_orders SET advance_amount = ?, date_modified = ? WHERE id = ?
            """, (new_advance, datetime.now(), order_id))
            
            execute_query("""
                INSERT INTO payments (payment_type, payment_date, amount, payment_mode,
                                     reference_type, reference_id, customer_id, description, date_created)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, ('Advance', date.today(), amount, 'Cash', 'Advance Order', order_id,
                  order['customer_id'], f"Additional advance for {order_num}", datetime.now()))
            
            messagebox.showinfo("Success", f"Payment of {amount:,.2f} added!\nTotal Advance: {new_advance:,.2f}")
            dialog.destroy()
            refresh_orders_list(tree)
        except Exception as e:
            messagebox.showerror("Error", f"Error: {str(e)}")
    
    ttk.Button(main_frame, text="Add Payment", command=add_payment).pack(pady=15)

def convert_to_bill(parent, tree):
    selected = tree.selection()
    if not selected:
        messagebox.showwarning("Warning", "Please select an order to convert!")
        return
    
    order_id = tree.item(selected[0])['values'][0]
    order_num = tree.item(selected[0])['values'][1]
    status = tree.item(selected[0])['values'][8].replace(' (!)', '')
    
    if status not in ('Ready', 'In Progress'):
        messagebox.showwarning("Warning", "Only 'Ready' or 'In Progress' orders can be converted to bills!")
        return
    
    order = AdvanceOrderService.get_order(order_id)
    
    if messagebox.askyesno("Confirm", f"Convert order {order_num} to a sales bill?\n\nThis will mark the order as Delivered."):
        from pages.bills import show_new_bill_dialog
        
        AdvanceOrderService.update_order_status(order_id, 'Delivered')
        messagebox.showinfo("Info", f"Order marked as Delivered.\n\nPlease create a new sales bill for the final transaction.")
        refresh_orders_list(tree)

def cancel_order(tree):
    selected = tree.selection()
    if not selected:
        messagebox.showwarning("Warning", "Please select an order to cancel!")
        return
    
    order_id = tree.item(selected[0])['values'][0]
    order_num = tree.item(selected[0])['values'][1]
    status = tree.item(selected[0])['values'][8].replace(' (!)', '')
    
    if status in ('Delivered', 'Cancelled'):
        messagebox.showinfo("Info", "This order is already completed/cancelled!")
        return
    
    advance = tree.item(selected[0])['values'][7]
    
    if messagebox.askyesno("Confirm Cancel", f"Cancel order {order_num}?\n\nAdvance collected: {advance}\nNote: Advance refund needs to be handled separately."):
        try:
            AdvanceOrderService.cancel_order(order_id, "Cancelled by user")
            messagebox.showinfo("Success", f"Order {order_num} has been cancelled!")
            refresh_orders_list(tree)
        except Exception as e:
            messagebox.showerror("Error", f"Error: {str(e)}")
