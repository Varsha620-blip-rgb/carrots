import tkinter as tk
from tkinter import Menu, messagebox, ttk
from datetime import datetime
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from database.db import create_tables, get_connection, fetch_query, execute_query
from pages.items import items_page, refresh_items_list
from pages.customers import customers_page, refresh_customers_list
from pages.employees import employees_page, refresh_employees_list
from pages.bills import bills_page, refresh_bills_list
from pages.dashboard import dashboard_page
from pages.reports import reports_page
from pages.gold_rates import gold_rates_page
from pages.data_import import data_import_page
from pages.transactions import create_transaction
from pages.advance_orders import advance_orders_page
from services.stock_service import StockService
from services.sales_service import SalesService
from services.purchase_service import PurchaseService
from services.gold_rate_service import GoldRateService, DiamondRateService
from services.advance_order_service import AdvanceOrderService
from utils.validators import Validators
from utils.helpers import Helpers
from utils.export import ExportService

create_tables()

APP_TITLE = "MT GOLD LAND - Jewelry Management System (Gold & Diamond)"
APP_VERSION = "2.0.0"
WINDOW_WIDTH = 1400
WINDOW_HEIGHT = 800

PRIMARY_COLOR = "#1e2d3d"
SECONDARY_COLOR = "#3a5068"
SUCCESS_COLOR = "#28a745"
ERROR_COLOR = "#dc3545"
WARNING_COLOR = "#ffc107"

def clear_frame(frame):
    for widget in frame.winfo_children():
        widget.destroy()

def make_nav_button(parent, text, command):
    btn = tk.Button(
        parent, text=text, font=("Segoe UI", 11), fg="white", bg=PRIMARY_COLOR,
        activebackground=SECONDARY_COLOR, activeforeground="white", bd=0, relief=tk.FLAT,
        anchor="w", padx=20, pady=12, command=command, wraplength=180
    )
    btn.pack(fill=tk.X)
    return btn

def show_dashboard():
    dashboard_page(content_frame)

def show_new_bill():
    bills_page(content_frame)

def show_manage_items():
    items_page(content_frame)

def show_manage_customers():
    customers_page(content_frame)

def show_manage_employees():
    employees_page(content_frame)

def show_reports():
    reports_page(content_frame)

def show_gold_rates():
    gold_rates_page(content_frame)

def show_data_import():
    data_import_page(content_frame)

def show_advance_orders():
    advance_orders_page(content_frame)

def show_stock_management():
    items_page(content_frame)

def add_item_category():
    dialog = tk.Toplevel(root)
    dialog.title("Add Item Category")
    dialog.geometry("400x250")
    dialog.transient(root)
    dialog.grab_set()
    
    main_frame = ttk.Frame(dialog, padding=20)
    main_frame.pack(fill=tk.BOTH, expand=True)
    
    ttk.Label(main_frame, text="Add New Category", font=("Segoe UI", 12, "bold")).pack(pady=10)
    
    form_frame = ttk.Frame(main_frame)
    form_frame.pack(fill=tk.X, pady=10)
    
    ttk.Label(form_frame, text="Category Name:").grid(row=0, column=0, sticky='w', pady=5)
    name_entry = ttk.Entry(form_frame, width=30)
    name_entry.grid(row=0, column=1, pady=5, padx=5)
    
    ttk.Label(form_frame, text="Material Type:").grid(row=1, column=0, sticky='w', pady=5)
    material_combo = ttk.Combobox(form_frame, values=['Gold', 'Diamond', 'Silver', 'Platinum', 'General'], width=27)
    material_combo.set('Gold')
    material_combo.grid(row=1, column=1, pady=5, padx=5)
    
    ttk.Label(form_frame, text="Description:").grid(row=2, column=0, sticky='w', pady=5)
    desc_entry = ttk.Entry(form_frame, width=30)
    desc_entry.grid(row=2, column=1, pady=5, padx=5)
    
    def save():
        name = name_entry.get().strip()
        if not name:
            messagebox.showwarning("Validation", "Category name is required!")
            return
        try:
            material_id = fetch_query("SELECT id FROM materials WHERE name = ?", (material_combo.get(),))
            mat_id = material_id[0][0] if material_id else None
            execute_query(
                "INSERT INTO item_categories (name, material_id, description, date_created) VALUES (?, ?, ?, ?)",
                (name, mat_id, desc_entry.get() or None, datetime.now())
            )
            messagebox.showinfo("Success", "Category added successfully!")
            dialog.destroy()
        except Exception as e:
            if "UNIQUE constraint" in str(e):
                messagebox.showerror("Error", "Category already exists!")
            else:
                messagebox.showerror("Error", f"Error: {str(e)}")
    
    ttk.Button(main_frame, text="Save", command=save, width=15).pack(pady=15)

def manage_categories():
    dialog = tk.Toplevel(root)
    dialog.title("Manage Categories")
    dialog.geometry("500x400")
    dialog.transient(root)
    
    categories = fetch_query("""
        SELECT ic.id, ic.name, COALESCE(m.name, 'General'), ic.description
        FROM item_categories ic
        LEFT JOIN materials m ON ic.material_id = m.id
        ORDER BY ic.name
    """)
    
    columns = ('ID', 'Name', 'Material', 'Description')
    tree = ttk.Treeview(dialog, columns=columns, height=15, show='headings')
    
    for col in columns:
        tree.heading(col, text=col)
        tree.column(col, width=100 if col != 'Description' else 150)
    
    for cat in categories:
        tree.insert('', 'end', values=cat)
    
    tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    
    def delete_category():
        selected = tree.selection()
        if not selected:
            return
        cat_id = tree.item(selected[0])['values'][0]
        if messagebox.askyesno("Confirm", "Delete this category?"):
            execute_query("DELETE FROM item_categories WHERE id = ?", (cat_id,))
            tree.delete(selected[0])
    
    ttk.Button(dialog, text="Delete Selected", command=delete_category).pack(pady=10)

def add_supplier():
    dialog = tk.Toplevel(root)
    dialog.title("Add Supplier")
    dialog.geometry("450x550")
    dialog.transient(root)
    dialog.grab_set()
    
    main_frame = ttk.Frame(dialog, padding=20)
    main_frame.pack(fill=tk.BOTH, expand=True)
    
    ttk.Label(main_frame, text="Add New Supplier", font=("Segoe UI", 12, "bold")).pack(pady=10)
    
    form_frame = ttk.Frame(main_frame)
    form_frame.pack(fill=tk.X)
    
    fields = {}
    labels = [('Name *', 'name'), ('Phone', 'phone'), ('Email', 'email'), ('Address', 'address'), 
              ('City', 'city'), ('State', 'state'), ('Pincode', 'pincode'), ('GST Number', 'gst_number'),
              ('Supplier Type', 'supplier_type')]
    
    for row, (label, key) in enumerate(labels):
        ttk.Label(form_frame, text=f"{label}:").grid(row=row, column=0, sticky='w', pady=5)
        if key == 'supplier_type':
            fields[key] = ttk.Combobox(form_frame, values=['Gold', 'Diamond', 'Silver', 'General', 'Artisan'], width=37)
            fields[key].set('General')
        else:
            fields[key] = ttk.Entry(form_frame, width=40)
        fields[key].grid(row=row, column=1, pady=5, padx=5)
    
    def save():
        name = fields['name'].get().strip()
        if not name:
            messagebox.showwarning("Validation", "Supplier name is required!")
            return
        try:
            execute_query(
                """INSERT INTO suppliers (name, phone, email, address, city, state, pincode, 
                   gst_number, supplier_type, date_created, date_modified)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (name, fields['phone'].get() or None, fields['email'].get() or None, 
                 fields['address'].get() or None, fields['city'].get() or None, fields['state'].get() or None,
                 fields['pincode'].get() or None, fields['gst_number'].get() or None,
                 fields['supplier_type'].get(), datetime.now(), datetime.now())
            )
            messagebox.showinfo("Success", "Supplier added successfully!")
            dialog.destroy()
        except Exception as e:
            messagebox.showerror("Error", f"Error: {str(e)}")
    
    ttk.Button(main_frame, text="Save", command=save, width=15).pack(pady=15)

def manage_suppliers():
    dialog = tk.Toplevel(root)
    dialog.title("Manage Suppliers")
    dialog.geometry("800x500")
    dialog.transient(root)
    
    suppliers = fetch_query("SELECT id, name, phone, email, city, supplier_type, gst_number FROM suppliers ORDER BY name")
    
    columns = ('ID', 'Name', 'Phone', 'Email', 'City', 'Type', 'GST')
    tree = ttk.Treeview(dialog, columns=columns, height=18, show='headings')
    
    for col in columns:
        tree.heading(col, text=col)
        tree.column(col, width=100)
    
    for sup in suppliers:
        tree.insert('', 'end', values=sup)
    
    tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    
    btn_frame = ttk.Frame(dialog)
    btn_frame.pack(pady=10)
    
    def delete_supplier():
        selected = tree.selection()
        if not selected:
            return
        sup_id = tree.item(selected[0])['values'][0]
        bills = fetch_query("SELECT COUNT(*) FROM bills WHERE supplier_id = ?", (sup_id,))[0][0]
        if bills > 0:
            messagebox.showwarning("Warning", f"Cannot delete. Supplier has {bills} bills.")
            return
        if messagebox.askyesno("Confirm", "Delete this supplier?"):
            execute_query("DELETE FROM suppliers WHERE id = ?", (sup_id,))
            tree.delete(selected[0])
    
    ttk.Button(btn_frame, text="Add Supplier", command=lambda: [dialog.destroy(), add_supplier()]).pack(side=tk.LEFT, padx=5)
    ttk.Button(btn_frame, text="Delete Selected", command=delete_supplier).pack(side=tk.LEFT, padx=5)

def quick_sales_entry():
    from pages.bills import show_new_bill_dialog
    show_new_bill_dialog(content_frame, 'Sales')

def quick_purchase_entry():
    from pages.bills import show_new_bill_dialog
    show_new_bill_dialog(content_frame, 'Purchase')

def cash_collection():
    dialog = tk.Toplevel(root)
    dialog.title("Cash Collection / Receipt")
    dialog.geometry("400x350")
    dialog.transient(root)
    dialog.grab_set()
    
    main_frame = ttk.Frame(dialog, padding=20)
    main_frame.pack(fill=tk.BOTH, expand=True)
    
    ttk.Label(main_frame, text="Record Cash Collection", font=("Segoe UI", 12, "bold")).pack(pady=10)
    
    customers = fetch_query("SELECT id, name FROM customers WHERE outstanding_balance > 0 ORDER BY name")
    
    form_frame = ttk.Frame(main_frame)
    form_frame.pack(fill=tk.X, pady=10)
    
    ttk.Label(form_frame, text="Customer:").grid(row=0, column=0, sticky='w', pady=5)
    customer_combo = ttk.Combobox(form_frame, values=[f"{c[1]} (ID:{c[0]})" for c in customers], width=30)
    customer_combo.grid(row=0, column=1, pady=5, padx=5)
    customer_data = {f"{c[1]} (ID:{c[0]})": c[0] for c in customers}
    
    ttk.Label(form_frame, text="Amount:").grid(row=1, column=0, sticky='w', pady=5)
    amount_entry = ttk.Entry(form_frame, width=33)
    amount_entry.grid(row=1, column=1, pady=5, padx=5)
    
    ttk.Label(form_frame, text="Payment Mode:").grid(row=2, column=0, sticky='w', pady=5)
    mode_combo = ttk.Combobox(form_frame, values=['Cash', 'Card', 'UPI', 'Bank Transfer', 'Cheque'], width=30)
    mode_combo.set('Cash')
    mode_combo.grid(row=2, column=1, pady=5, padx=5)
    
    ttk.Label(form_frame, text="Description:").grid(row=3, column=0, sticky='w', pady=5)
    desc_entry = ttk.Entry(form_frame, width=33)
    desc_entry.grid(row=3, column=1, pady=5, padx=5)
    
    def save():
        customer_id = customer_data.get(customer_combo.get())
        try:
            amount = float(amount_entry.get())
        except:
            messagebox.showerror("Error", "Invalid amount!")
            return
        
        if amount <= 0:
            messagebox.showerror("Error", "Amount must be positive!")
            return
        
        try:
            execute_query("""
                INSERT INTO payments (payment_type, payment_date, amount, payment_mode,
                                     customer_id, description, date_created)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, ('Receipt', datetime.now().date(), amount, mode_combo.get(),
                  customer_id, desc_entry.get() or "Cash collection", datetime.now()))
            
            if customer_id:
                execute_query("""
                    UPDATE customers SET outstanding_balance = outstanding_balance - ?, date_modified = ?
                    WHERE id = ?
                """, (amount, datetime.now(), customer_id))
            
            execute_query("""
                INSERT INTO transactions (transaction_type, transaction_date, description,
                                         account_head, debit_amount, payment_mode, date_created)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, ('Receipt', datetime.now().date(), desc_entry.get() or "Cash collection",
                  'Cash', amount, mode_combo.get(), datetime.now()))
            
            messagebox.showinfo("Success", f"Collection of {amount:,.2f} recorded!")
            dialog.destroy()
        except Exception as e:
            messagebox.showerror("Error", f"Error: {str(e)}")
    
    ttk.Button(main_frame, text="Save Collection", command=save, width=15).pack(pady=15)

def cash_payment():
    dialog = tk.Toplevel(root)
    dialog.title("Cash Payment")
    dialog.geometry("400x350")
    dialog.transient(root)
    dialog.grab_set()
    
    main_frame = ttk.Frame(dialog, padding=20)
    main_frame.pack(fill=tk.BOTH, expand=True)
    
    ttk.Label(main_frame, text="Record Cash Payment", font=("Segoe UI", 12, "bold")).pack(pady=10)
    
    suppliers = fetch_query("SELECT id, name FROM suppliers ORDER BY name")
    
    form_frame = ttk.Frame(main_frame)
    form_frame.pack(fill=tk.X, pady=10)
    
    ttk.Label(form_frame, text="Pay To:").grid(row=0, column=0, sticky='w', pady=5)
    supplier_combo = ttk.Combobox(form_frame, values=['General Expense'] + [f"{s[1]} (ID:{s[0]})" for s in suppliers], width=30)
    supplier_combo.grid(row=0, column=1, pady=5, padx=5)
    supplier_data = {f"{s[1]} (ID:{s[0]})": s[0] for s in suppliers}
    
    ttk.Label(form_frame, text="Amount:").grid(row=1, column=0, sticky='w', pady=5)
    amount_entry = ttk.Entry(form_frame, width=33)
    amount_entry.grid(row=1, column=1, pady=5, padx=5)
    
    ttk.Label(form_frame, text="Payment Mode:").grid(row=2, column=0, sticky='w', pady=5)
    mode_combo = ttk.Combobox(form_frame, values=['Cash', 'Card', 'UPI', 'Bank Transfer', 'Cheque'], width=30)
    mode_combo.set('Cash')
    mode_combo.grid(row=2, column=1, pady=5, padx=5)
    
    ttk.Label(form_frame, text="Description:").grid(row=3, column=0, sticky='w', pady=5)
    desc_entry = ttk.Entry(form_frame, width=33)
    desc_entry.grid(row=3, column=1, pady=5, padx=5)
    
    def save():
        supplier_id = supplier_data.get(supplier_combo.get())
        try:
            amount = float(amount_entry.get())
        except:
            messagebox.showerror("Error", "Invalid amount!")
            return
        
        if amount <= 0:
            messagebox.showerror("Error", "Amount must be positive!")
            return
        
        try:
            execute_query("""
                INSERT INTO payments (payment_type, payment_date, amount, payment_mode,
                                     supplier_id, description, date_created)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, ('Payment', datetime.now().date(), amount, mode_combo.get(),
                  supplier_id, desc_entry.get() or "Cash payment", datetime.now()))
            
            execute_query("""
                INSERT INTO transactions (transaction_type, transaction_date, description,
                                         account_head, credit_amount, payment_mode, date_created)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, ('Payment', datetime.now().date(), desc_entry.get() or "Cash payment",
                  'Cash', amount, mode_combo.get(), datetime.now()))
            
            messagebox.showinfo("Success", f"Payment of {amount:,.2f} recorded!")
            dialog.destroy()
        except Exception as e:
            messagebox.showerror("Error", f"Error: {str(e)}")
    
    ttk.Button(main_frame, text="Save Payment", command=save, width=15).pack(pady=15)

def stock_report():
    stock_data = StockService.get_stock_report()
    
    if not stock_data:
        messagebox.showinfo("Stock Report", "No stock data available")
        return
    
    dialog = tk.Toplevel(root)
    dialog.title("Stock Report")
    dialog.geometry("1000x600")
    
    columns = ('ID', 'Item', 'Category', 'Qty', 'Weight(gm)', 'Price', 'Total Value', 'Material')
    tree = ttk.Treeview(dialog, columns=columns, height=25)
    
    for col in columns:
        tree.column(col, width=120)
        tree.heading(col, text=col)
    
    total_value = 0
    for item in stock_data:
        value = item[6] if item[6] else 0
        total_value += value
        tree.insert('', 'end', values=(
            item[0], item[1], item[2] or 'N/A', item[3], 
            f"{item[4]:.3f}" if item[4] else '0.000',
            f"{item[5]:,.2f}" if item[5] else '0.00',
            f"{value:,.2f}",
            item[7] if len(item) > 7 else 'N/A'
        ))
    
    tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    
    ttk.Label(dialog, text=f"Total Stock Value: {total_value:,.2f}", font=("Segoe UI", 12, "bold")).pack(pady=5)
    ttk.Button(dialog, text="Close", command=dialog.destroy).pack(pady=10)

def sales_report():
    sales_data = SalesService.get_sales_report()
    
    dialog = tk.Toplevel(root)
    dialog.title("Sales Report")
    dialog.geometry("800x600")
    
    columns = ('Bill Number', 'Customer', 'Date', 'Amount', 'Status')
    tree = ttk.Treeview(dialog, columns=columns, height=25)
    
    for col in columns:
        tree.column(col, width=150)
        tree.heading(col, text=col)
    
    for item in sales_data:
        tree.insert('', 'end', values=(item[0], item[1], item[2], f"{item[3]:,.2f}", item[4]))
    
    tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    ttk.Button(dialog, text="Close", command=dialog.destroy).pack(pady=10)

def purchase_report():
    purchase_data = PurchaseService.get_purchase_report()
    
    dialog = tk.Toplevel(root)
    dialog.title("Purchase Report")
    dialog.geometry("800x600")
    
    columns = ('Bill Number', 'Supplier', 'Date', 'Amount', 'Status')
    tree = ttk.Treeview(dialog, columns=columns, height=25)
    
    for col in columns:
        tree.column(col, width=150)
        tree.heading(col, text=col)
    
    for item in purchase_data:
        tree.insert('', 'end', values=(item[0], item[1], item[2], f"{item[3]:,.2f}", item[4]))
    
    tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    ttk.Button(dialog, text="Close", command=dialog.destroy).pack(pady=10)

def today_summary():
    today = datetime.now().date()
    
    sales_total = fetch_query(
        "SELECT COALESCE(SUM(total_amount), 0) FROM bills WHERE bill_type = 'Sales' AND DATE(bill_date) = ?",
        (today,)
    )[0][0]
    
    purchase_total = fetch_query(
        "SELECT COALESCE(SUM(total_amount), 0) FROM bills WHERE bill_type = 'Purchase' AND DATE(bill_date) = ?",
        (today,)
    )[0][0]
    
    sales_count = fetch_query(
        "SELECT COUNT(*) FROM bills WHERE bill_type = 'Sales' AND DATE(bill_date) = ?",
        (today,)
    )[0][0]
    
    purchase_count = fetch_query(
        "SELECT COUNT(*) FROM bills WHERE bill_type = 'Purchase' AND DATE(bill_date) = ?",
        (today,)
    )[0][0]
    
    collections = fetch_query(
        "SELECT COALESCE(SUM(amount), 0) FROM payments WHERE payment_type = 'Receipt' AND payment_date = ?",
        (today,)
    )[0][0]
    
    payments = fetch_query(
        "SELECT COALESCE(SUM(amount), 0) FROM payments WHERE payment_type = 'Payment' AND payment_date = ?",
        (today,)
    )[0][0]
    
    summary = f"""
TODAY'S SUMMARY - {datetime.now().strftime('%d-%m-%Y')}
{'='*50}

SALES:
  Total Amount: {sales_total:,.2f}
  Number of Bills: {sales_count}

PURCHASES:
  Total Amount: {purchase_total:,.2f}
  Number of Bills: {purchase_count}

COLLECTIONS:
  Cash Received: {collections:,.2f}

PAYMENTS:
  Cash Paid: {payments:,.2f}

NET PROFIT (Sales - Purchases): {sales_total - purchase_total:,.2f}
NET CASH FLOW: {collections - payments:,.2f}
    """
    
    messagebox.showinfo("Today's Summary", summary)

def show_artisan_management():
    dialog = tk.Toplevel(root)
    dialog.title("Artisan/Smith Management")
    dialog.geometry("900x500")
    dialog.transient(root)
    
    notebook = ttk.Notebook(dialog)
    notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    
    transfers_frame = ttk.Frame(notebook)
    notebook.add(transfers_frame, text="Metal Transfers")
    
    transfers = fetch_query("""
        SELECT id, artisan_name, artisan_type, weight_sent, date_sent, status, 
               weight_received, loss_gain FROM artisan_transfers ORDER BY date_sent DESC
    """)
    
    columns = ('ID', 'Artisan', 'Type', 'Sent (gm)', 'Date Sent', 'Status', 'Received (gm)', 'Loss/Gain')
    tree = ttk.Treeview(transfers_frame, columns=columns, height=15, show='headings')
    
    for col in columns:
        tree.heading(col, text=col)
        tree.column(col, width=100)
    
    for t in transfers:
        tree.insert('', 'end', values=t)
    
    tree.pack(fill=tk.BOTH, expand=True, pady=10)
    
    def add_transfer():
        add_dialog = tk.Toplevel(dialog)
        add_dialog.title("New Transfer")
        add_dialog.geometry("400x350")
        add_dialog.grab_set()
        
        frame = ttk.Frame(add_dialog, padding=20)
        frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(frame, text="Artisan Name:").grid(row=0, column=0, sticky='w', pady=5)
        artisan_entry = ttk.Entry(frame, width=30)
        artisan_entry.grid(row=0, column=1, pady=5)
        
        ttk.Label(frame, text="Type:").grid(row=1, column=0, sticky='w', pady=5)
        type_combo = ttk.Combobox(frame, values=['Smith', 'Jeweller', 'Refiner', 'Polisher'], width=27)
        type_combo.set('Smith')
        type_combo.grid(row=1, column=1, pady=5)
        
        ttk.Label(frame, text="Material:").grid(row=2, column=0, sticky='w', pady=5)
        material_combo = ttk.Combobox(frame, values=['Gold', 'Silver', 'Platinum'], width=27)
        material_combo.set('Gold')
        material_combo.grid(row=2, column=1, pady=5)
        
        ttk.Label(frame, text="Weight (gm):").grid(row=3, column=0, sticky='w', pady=5)
        weight_entry = ttk.Entry(frame, width=30)
        weight_entry.grid(row=3, column=1, pady=5)
        
        ttk.Label(frame, text="Expected Return:").grid(row=4, column=0, sticky='w', pady=5)
        return_entry = ttk.Entry(frame, width=30)
        return_entry.insert(0, datetime.now().strftime('%Y-%m-%d'))
        return_entry.grid(row=4, column=1, pady=5)
        
        def save_transfer():
            try:
                weight = float(weight_entry.get())
                execute_query("""
                    INSERT INTO artisan_transfers (artisan_name, artisan_type, material_type, 
                                                  weight_sent, date_sent, expected_return_date, status, date_created)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (artisan_entry.get(), type_combo.get(), material_combo.get(),
                      weight, datetime.now().date(), return_entry.get(), 'Pending', datetime.now()))
                messagebox.showinfo("Success", "Transfer recorded!")
                add_dialog.destroy()
            except Exception as e:
                messagebox.showerror("Error", f"Error: {str(e)}")
        
        ttk.Button(frame, text="Save", command=save_transfer).grid(row=5, column=0, columnspan=2, pady=20)
    
    ttk.Button(transfers_frame, text="New Transfer", command=add_transfer).pack(pady=5)

def show_old_gold_exchange():
    dialog = tk.Toplevel(root)
    dialog.title("Old Gold Exchange")
    dialog.geometry("500x400")
    dialog.transient(root)
    dialog.grab_set()
    
    main_frame = ttk.Frame(dialog, padding=20)
    main_frame.pack(fill=tk.BOTH, expand=True)
    
    ttk.Label(main_frame, text="Old Gold Exchange Entry", font=("Segoe UI", 12, "bold")).pack(pady=10)
    
    form_frame = ttk.Frame(main_frame)
    form_frame.pack(fill=tk.X, pady=10)
    
    customers = fetch_query("SELECT id, name FROM customers ORDER BY name")
    
    ttk.Label(form_frame, text="Customer:").grid(row=0, column=0, sticky='w', pady=5)
    customer_combo = ttk.Combobox(form_frame, values=[f"{c[1]} (ID:{c[0]})" for c in customers], width=30)
    customer_combo.grid(row=0, column=1, pady=5, padx=5)
    customer_data = {f"{c[1]} (ID:{c[0]})": c[0] for c in customers}
    
    ttk.Label(form_frame, text="Item Description:").grid(row=1, column=0, sticky='w', pady=5)
    desc_entry = ttk.Entry(form_frame, width=33)
    desc_entry.grid(row=1, column=1, pady=5, padx=5)
    
    ttk.Label(form_frame, text="Gross Weight (gm):").grid(row=2, column=0, sticky='w', pady=5)
    gross_entry = ttk.Entry(form_frame, width=33)
    gross_entry.grid(row=2, column=1, pady=5, padx=5)
    
    ttk.Label(form_frame, text="Purity:").grid(row=3, column=0, sticky='w', pady=5)
    purity_combo = ttk.Combobox(form_frame, values=['24K', '22K', '18K', '14K', 'Unknown'], width=30)
    purity_combo.set('22K')
    purity_combo.grid(row=3, column=1, pady=5, padx=5)
    
    ttk.Label(form_frame, text="Rate per gm:").grid(row=4, column=0, sticky='w', pady=5)
    rate_entry = ttk.Entry(form_frame, width=33)
    current_rate = GoldRateService.get_current_rate('22K')
    if current_rate:
        rate_entry.insert(0, str(current_rate['rate_per_gram']))
    rate_entry.grid(row=4, column=1, pady=5, padx=5)
    
    ttk.Label(form_frame, text="Deduction %:").grid(row=5, column=0, sticky='w', pady=5)
    deduction_entry = ttk.Entry(form_frame, width=33)
    deduction_entry.insert(0, "5")
    deduction_entry.grid(row=5, column=1, pady=5, padx=5)
    
    result_var = tk.StringVar(value="Total Value: 0.00")
    ttk.Label(form_frame, textvariable=result_var, font=("Segoe UI", 11, "bold")).grid(row=6, column=0, columnspan=2, pady=10)
    
    def calculate():
        try:
            gross = float(gross_entry.get())
            rate = float(rate_entry.get())
            deduction = float(deduction_entry.get())
            net = gross * (1 - deduction/100)
            total = net * rate
            result_var.set(f"Net Weight: {net:.3f} gm | Total Value: {total:,.2f}")
        except:
            pass
    
    ttk.Button(form_frame, text="Calculate", command=calculate).grid(row=7, column=0, columnspan=2, pady=5)
    
    def save():
        customer_id = customer_data.get(customer_combo.get())
        try:
            gross = float(gross_entry.get())
            rate = float(rate_entry.get())
            deduction = float(deduction_entry.get())
            net = gross * (1 - deduction/100)
            total = net * rate
            
            execute_query("""
                INSERT INTO old_gold_exchange (customer_id, exchange_date, item_description,
                                              gross_weight, purity, net_weight, rate_per_gram,
                                              deduction_percent, total_value, date_created)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (customer_id, datetime.now().date(), desc_entry.get(),
                  gross, purity_combo.get(), net, rate, deduction, total, datetime.now()))
            
            messagebox.showinfo("Success", f"Exchange recorded!\nTotal Value: {total:,.2f}")
            dialog.destroy()
        except Exception as e:
            messagebox.showerror("Error", f"Error: {str(e)}")
    
    ttk.Button(main_frame, text="Save Exchange", command=save, width=15).pack(pady=15)

def show_diamond_rates():
    dialog = tk.Toplevel(root)
    dialog.title("Diamond Rate Management")
    dialog.geometry("800x500")
    dialog.transient(root)
    
    main_frame = ttk.Frame(dialog, padding=10)
    main_frame.pack(fill=tk.BOTH, expand=True)
    
    ttk.Label(main_frame, text="Diamond Rate Management", font=("Segoe UI", 14, "bold")).pack(pady=10)
    
    add_frame = ttk.LabelFrame(main_frame, text="Add/Update Rate", padding=10)
    add_frame.pack(fill=tk.X, pady=10)
    
    row1 = ttk.Frame(add_frame)
    row1.pack(fill=tk.X, pady=5)
    
    ttk.Label(row1, text="Clarity:").pack(side=tk.LEFT, padx=5)
    clarity_combo = ttk.Combobox(row1, values=DiamondRateService.CLARITIES, width=8)
    clarity_combo.set('VS1')
    clarity_combo.pack(side=tk.LEFT, padx=5)
    
    ttk.Label(row1, text="Color:").pack(side=tk.LEFT, padx=10)
    color_combo = ttk.Combobox(row1, values=DiamondRateService.COLORS, width=6)
    color_combo.set('G')
    color_combo.pack(side=tk.LEFT, padx=5)
    
    ttk.Label(row1, text="Shape:").pack(side=tk.LEFT, padx=10)
    shape_combo = ttk.Combobox(row1, values=DiamondRateService.SHAPES, width=10)
    shape_combo.set('Round')
    shape_combo.pack(side=tk.LEFT, padx=5)
    
    ttk.Label(row1, text="Rate/Carat:").pack(side=tk.LEFT, padx=10)
    rate_entry = ttk.Entry(row1, width=12)
    rate_entry.pack(side=tk.LEFT, padx=5)
    
    def add_rate():
        try:
            rate = float(rate_entry.get())
            DiamondRateService.update_rate(
                clarity_combo.get(), color_combo.get(), rate,
                shape=shape_combo.get()
            )
            messagebox.showinfo("Success", "Diamond rate updated!")
            refresh_rates()
        except Exception as e:
            messagebox.showerror("Error", f"Error: {str(e)}")
    
    ttk.Button(row1, text="Add/Update", command=add_rate).pack(side=tk.LEFT, padx=20)
    
    columns = ('ID', 'Date', 'Shape', 'Clarity', 'Color', 'Carat Range', 'Rate/Carat', 'Certification')
    tree = ttk.Treeview(main_frame, columns=columns, height=15, show='headings')
    
    for col in columns:
        tree.heading(col, text=col)
        tree.column(col, width=90)
    
    tree.pack(fill=tk.BOTH, expand=True, pady=10)
    
    def refresh_rates():
        for item in tree.get_children():
            tree.delete(item)
        rates = DiamondRateService.get_rate_history()
        for r in rates:
            tree.insert('', 'end', values=(
                r[0], r[1], r[2], r[3], r[4], f"{r[5]}-{r[6]}", f"{r[7]:,.2f}", r[8] or 'N/A'
            ))
    
    refresh_rates()
    ttk.Button(main_frame, text="Close", command=dialog.destroy).pack(pady=10)

root = tk.Tk()
root.title(APP_TITLE)
root.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")

style = ttk.Style()
style.theme_use('clam')

container = tk.Frame(root)
container.pack(fill=tk.BOTH, expand=True)

navbar = tk.Frame(container, bg=PRIMARY_COLOR, width=200)
navbar.pack(side=tk.LEFT, fill=tk.Y, padx=0, pady=0)
navbar.pack_propagate(False)

logo_frame = tk.Frame(navbar, bg=PRIMARY_COLOR)
logo_frame.pack(fill=tk.X, padx=10, pady=20)

logo_label = tk.Label(logo_frame, text="MT GOLD LAND", font=("Segoe UI", 13, "bold"), 
                      fg="white", bg=PRIMARY_COLOR)
logo_label.pack()

subtitle_label = tk.Label(logo_frame, text="Gold & Diamond", font=("Segoe UI", 9), 
                          fg="#aaa", bg=PRIMARY_COLOR)
subtitle_label.pack()

version_label = tk.Label(logo_frame, text=f"v{APP_VERSION}", font=("Segoe UI", 8), 
                         fg="#888", bg=PRIMARY_COLOR)
version_label.pack()

separator = tk.Frame(navbar, bg=SECONDARY_COLOR, height=2)
separator.pack(fill=tk.X, pady=10, padx=10)

make_nav_button(navbar, "Dashboard", show_dashboard)
make_nav_button(navbar, "New Bill", show_new_bill)
make_nav_button(navbar, "Advance Orders", show_advance_orders)
make_nav_button(navbar, "Manage Items", show_manage_items)
make_nav_button(navbar, "Customers", show_manage_customers)
make_nav_button(navbar, "Employees", show_manage_employees)
make_nav_button(navbar, "Reports", show_reports)
make_nav_button(navbar, "Gold/Diamond Rates", show_gold_rates)
make_nav_button(navbar, "Data Import", show_data_import)

separator2 = tk.Frame(navbar, bg=SECONDARY_COLOR, height=2)
separator2.pack(fill=tk.X, pady=15, padx=10)

quick_label = tk.Label(navbar, text="Quick Actions", font=("Segoe UI", 10, "bold"), 
                       fg="white", bg=PRIMARY_COLOR)
quick_label.pack(fill=tk.X, padx=20, pady=5)

make_nav_button(navbar, "Quick Sale", quick_sales_entry)
make_nav_button(navbar, "Quick Purchase", quick_purchase_entry)
make_nav_button(navbar, "Collection", cash_collection)
make_nav_button(navbar, "Payment", cash_payment)

content_frame = tk.Frame(container, bg="white")
content_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

menubar = Menu(root)

dashboard_menu = Menu(menubar, tearoff=0)
dashboard_menu.add_command(label="Dashboard", command=show_dashboard)
dashboard_menu.add_separator()
dashboard_menu.add_command(label="Today's Summary", command=today_summary)
dashboard_menu.add_command(label="Refresh", command=show_dashboard)
menubar.add_cascade(label="Dashboard", menu=dashboard_menu)

master_menu = Menu(menubar, tearoff=0)
master_menu.add_command(label="Items", command=show_manage_items)
master_menu.add_command(label="Customers", command=show_manage_customers)
master_menu.add_command(label="Employees", command=show_manage_employees)
master_menu.add_separator()

category_menu = Menu(master_menu, tearoff=0)
category_menu.add_command(label="Add Category", command=add_item_category)
category_menu.add_command(label="Manage Categories", command=manage_categories)
master_menu.add_cascade(label="Item Categories", menu=category_menu)

supplier_menu = Menu(master_menu, tearoff=0)
supplier_menu.add_command(label="Add Supplier", command=add_supplier)
supplier_menu.add_command(label="Manage Suppliers", command=manage_suppliers)
master_menu.add_cascade(label="Suppliers", menu=supplier_menu)

master_menu.add_separator()
master_menu.add_command(label="Artisan/Smith", command=show_artisan_management)
master_menu.add_command(label="Old Gold Exchange", command=show_old_gold_exchange)
master_menu.add_separator()
master_menu.add_command(label="Gold Rates", command=show_gold_rates)
master_menu.add_command(label="Diamond Rates", command=show_diamond_rates)
master_menu.add_separator()
master_menu.add_command(label="Data Import", command=show_data_import)
menubar.add_cascade(label="Master", menu=master_menu)

transactions_menu = Menu(menubar, tearoff=0)

sales_menu = Menu(transactions_menu, tearoff=0)
sales_menu.add_command(label="Sales Invoice", command=quick_sales_entry)
sales_menu.add_command(label="View Sales Bills", command=show_new_bill)
transactions_menu.add_cascade(label="Sales", menu=sales_menu)

purchase_menu = Menu(transactions_menu, tearoff=0)
purchase_menu.add_command(label="Purchase Invoice", command=quick_purchase_entry)
purchase_menu.add_command(label="View Purchase Bills", command=show_new_bill)
transactions_menu.add_cascade(label="Purchase", menu=purchase_menu)

transactions_menu.add_separator()
transactions_menu.add_command(label="Advance Orders", command=show_advance_orders)
transactions_menu.add_separator()
transactions_menu.add_command(label="Cash Receipt", command=cash_collection)
transactions_menu.add_command(label="Cash Payment", command=cash_payment)
menubar.add_cascade(label="Transactions", menu=transactions_menu)

stock_menu = Menu(menubar, tearoff=0)
stock_menu.add_command(label="Manage Stock", command=show_manage_items)
stock_menu.add_command(label="Stock Report", command=stock_report)
stock_menu.add_separator()
stock_menu.add_command(label="Low Stock Items", command=lambda: messagebox.showinfo("Low Stock", 
    "\n".join([f"{i[1]}: {i[2]} units" for i in StockService.get_low_stock_items()]) or "No low stock items"))
menubar.add_cascade(label="Stock", menu=stock_menu)

reports_menu = Menu(menubar, tearoff=0)
reports_menu.add_command(label="Stock Report", command=stock_report)
reports_menu.add_command(label="Sales Report", command=sales_report)
reports_menu.add_command(label="Purchase Report", command=purchase_report)
reports_menu.add_separator()
reports_menu.add_command(label="Today's Summary", command=today_summary)
reports_menu.add_command(label="All Reports", command=show_reports)
menubar.add_cascade(label="Reports", menu=reports_menu)

help_menu = Menu(menubar, tearoff=0)
help_menu.add_command(label="About", command=lambda: messagebox.showinfo("About", 
    f"MT GOLD LAND\nJewelry Management System\nVersion {APP_VERSION}\n\nSupports Gold & Diamond"))
help_menu.add_command(label="Help", command=lambda: messagebox.showinfo("Help", "Contact support for help"))
menubar.add_cascade(label="Help", menu=help_menu)

root.config(menu=menubar)

show_dashboard()

root.mainloop()
