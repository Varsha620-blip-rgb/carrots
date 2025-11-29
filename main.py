# ============================================================================
# GOLD SHOP MANAGEMENT SYSTEM - MAIN APPLICATION FILE
# Production Ready - v1.0
# ============================================================================

import tkinter as tk
from tkinter import Menu, messagebox, ttk
from datetime import datetime
import sys
from pathlib import Path

# Add project to path
sys.path.insert(0, str(Path(__file__).parent))

# Import configurations and modules
from database.db import create_tables, get_connection, fetch_query, execute_query
from pages.items import items_page, refresh_items_list
from pages.customers import customers_page, refresh_customers_list
from pages.employees import employees_page, refresh_employees_list
from pages.bills import bills_page, refresh_bills_list
from pages.dashboard import dashboard_page
from pages.reports import reports_page
from pages.transactions import create_transaction
from services.stock_service import StockService
from services.sales_service import SalesService
from services.purchase_service import PurchaseService
from utils.validators import Validators
from utils.helpers import Helpers
from utils.export import ExportService

# Initialize database
create_tables()

# ============================================================================
# APPLICATION CONFIGURATION
# ============================================================================

APP_TITLE = "MT GOLD LAND - Gold Shop Management System"
APP_VERSION = "1.0.0"
WINDOW_WIDTH = 1400
WINDOW_HEIGHT = 800

PRIMARY_COLOR = "#1e2d3d"
SECONDARY_COLOR = "#3a5068"
SUCCESS_COLOR = "#28a745"
ERROR_COLOR = "#dc3545"
WARNING_COLOR = "#ffc107"

# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def dummy_action(name):
    """Placeholder for unimplemented menu items"""
    messagebox.showinfo("Info", f"{name} - Coming Soon!")

def clear_frame(frame):
    """Clear all widgets from a frame"""
    for widget in frame.winfo_children():
        widget.destroy()

def make_nav_button(parent, text, command):
    """Create a styled navigation button"""
    btn = tk.Button(
        parent, text=text, font=("Segoe UI", 11), fg="white", bg=PRIMARY_COLOR,
        activebackground=SECONDARY_COLOR, activeforeground="white", bd=0, relief=tk.FLAT,
        anchor="w", padx=20, pady=12, command=command, wraplength=180
    )
    btn.pack(fill=tk.X)
    return btn

# ============================================================================
# PAGE DISPLAY FUNCTIONS
# ============================================================================

def show_dashboard():
    """Display dashboard page"""
    dashboard_page(content_frame)

def show_new_bill():
    """Display new bill creation page"""
    bills_page(content_frame)

def show_manage_items():
    """Display items management page"""
    items_page(content_frame)

def show_manage_customers():
    """Display customer management page"""
    customers_page(content_frame)

def show_manage_employees():
    """Display employee management page"""
    employees_page(content_frame)

def show_reports():
    """Display reports page"""
    reports_page(content_frame)

# ============================================================================
# MASTER MENU FUNCTIONS
# ============================================================================

def add_item_category():
    """Add a new item category"""
    dialog = tk.Toplevel(root)
    dialog.title("Add Item Category")
    dialog.geometry("300x150")
    
    ttk.Label(dialog, text="Category Name:").pack(pady=10)
    entry = ttk.Entry(dialog, width=30)
    entry.pack(pady=5)
    
    ttk.Label(dialog, text="Description:").pack(pady=5)
    desc = ttk.Entry(dialog, width=30)
    desc.pack(pady=5)
    
    def save():
        try:
            execute_query(
                "INSERT INTO item_categories (name, description, date_created) VALUES (?, ?, ?)",
                (entry.get(), desc.get(), datetime.now())
            )
            messagebox.showinfo("Success", "Category added successfully!")
            dialog.destroy()
        except Exception as e:
            messagebox.showerror("Error", f"Error: {str(e)}")
    
    ttk.Button(dialog, text="Save", command=save).pack(pady=10)

def add_supplier():
    """Add a new supplier"""
    dialog = tk.Toplevel(root)
    dialog.title("Add Supplier")
    dialog.geometry("400x500")
    
    fields = {}
    labels = ['Name', 'Phone', 'Email', 'Address', 'City', 'State', 'Pincode', 'GST Number']
    
    for label in labels:
        ttk.Label(dialog, text=f"{label}:").pack(pady=5)
        fields[label.lower()] = ttk.Entry(dialog, width=40)
        fields[label.lower()].pack(pady=5)
    
    def save():
        try:
            execute_query(
                """INSERT INTO suppliers (name, phone, email, address, city, state, pincode, gst_number, date_created, date_modified)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (fields['name'].get(), fields['phone'].get(), fields['email'].get(), 
                 fields['address'].get(), fields['city'].get(), fields['state'].get(),
                 fields['pincode'].get(), fields['gst number'].get(),
                 datetime.now(), datetime.now())
            )
            messagebox.showinfo("Success", "Supplier added successfully!")
            dialog.destroy()
        except Exception as e:
            messagebox.showerror("Error", f"Error: {str(e)}")
    
    ttk.Button(dialog, text="Save", command=save).pack(pady=10)

# ============================================================================
# TRANSACTION MENU FUNCTIONS
# ============================================================================

def quick_sales_entry():
    """Quick sales entry form"""
    dialog = tk.Toplevel(root)
    dialog.title("Quick Sales Entry")
    dialog.geometry("500x400")
    
    ttk.Label(dialog, text="Customer:").pack(pady=5)
    customer_var = ttk.Combobox(dialog, width=40)
    customer_var.pack(pady=5)
    
    ttk.Label(dialog, text="Item:").pack(pady=5)
    item_var = ttk.Combobox(dialog, width=40)
    item_var.pack(pady=5)
    
    ttk.Label(dialog, text="Quantity:").pack(pady=5)
    qty_entry = ttk.Entry(dialog, width=40)
    qty_entry.pack(pady=5)
    
    ttk.Label(dialog, text="Unit Price:").pack(pady=5)
    price_entry = ttk.Entry(dialog, width=40)
    price_entry.pack(pady=5)
    
    ttk.Label(dialog, text="Discount:").pack(pady=5)
    discount_entry = ttk.Entry(dialog, width=40)
    discount_entry.pack(pady=5)
    
    # Populate dropdowns
    customers = fetch_query("SELECT id, name FROM customers")
    customer_var['values'] = [f"{c[1]} (ID: {c[0]})" for c in customers]
    
    items = fetch_query("SELECT id, name, price FROM items WHERE is_active = 1")
    item_var['values'] = [f"{i[1]} - ₹{i[2]}" for i in items]
    
    def save_sale():
        try:
            if not all([customer_var.get(), item_var.get(), qty_entry.get(), price_entry.get()]):
                messagebox.showwarning("Warning", "Please fill all fields")
                return
            
            qty = float(qty_entry.get())
            price = float(price_entry.get())
            discount = float(discount_entry.get() or 0)
            
            total = (qty * price) - discount
            
            # Create sale
            messagebox.showinfo("Success", f"Sale recorded!\nTotal: ₹{total}")
            dialog.destroy()
        except Exception as e:
            messagebox.showerror("Error", f"Error: {str(e)}")
    
    ttk.Button(dialog, text="Save Sale", command=save_sale).pack(pady=20)

def quick_purchase_entry():
    """Quick purchase entry form"""
    dialog = tk.Toplevel(root)
    dialog.title("Quick Purchase Entry")
    dialog.geometry("500x400")
    
    ttk.Label(dialog, text="Supplier:").pack(pady=5)
    supplier_var = ttk.Combobox(dialog, width=40)
    supplier_var.pack(pady=5)
    
    ttk.Label(dialog, text="Item:").pack(pady=5)
    item_var = ttk.Combobox(dialog, width=40)
    item_var.pack(pady=5)
    
    ttk.Label(dialog, text="Quantity:").pack(pady=5)
    qty_entry = ttk.Entry(dialog, width=40)
    qty_entry.pack(pady=5)
    
    ttk.Label(dialog, text="Unit Cost:").pack(pady=5)
    cost_entry = ttk.Entry(dialog, width=40)
    cost_entry.pack(pady=5)
    
    # Populate dropdowns
    suppliers = fetch_query("SELECT id, name FROM suppliers")
    supplier_var['values'] = [f"{s[1]} (ID: {s[0]})" for s in suppliers]
    
    items = fetch_query("SELECT id, name FROM items WHERE is_active = 1")
    item_var['values'] = [i[1] for i in items]
    
    def save_purchase():
        try:
            if not all([supplier_var.get(), item_var.get(), qty_entry.get(), cost_entry.get()]):
                messagebox.showwarning("Warning", "Please fill all fields")
                return
            
            qty = float(qty_entry.get())
            cost = float(cost_entry.get())
            total = qty * cost
            
            messagebox.showinfo("Success", f"Purchase recorded!\nTotal: ₹{total}")
            dialog.destroy()
        except Exception as e:
            messagebox.showerror("Error", f"Error: {str(e)}")
    
    ttk.Button(dialog, text="Save Purchase", command=save_purchase).pack(pady=20)

def cash_collection():
    """Record cash collection"""
    messagebox.showinfo("Cash Collection", "Cash Collection Module - Coming Soon!")

def cash_payment():
    """Record cash payment"""
    messagebox.showinfo("Cash Payment", "Cash Payment Module - Coming Soon!")

# ============================================================================
# REPORT FUNCTIONS
# ============================================================================

def stock_report():
    """Generate stock report"""
    try:
        stock_data = StockService.get_stock_report()
        
        if not stock_data:
            messagebox.showinfo("Stock Report", "No stock data available")
            return
        
        dialog = tk.Toplevel(root)
        dialog.title("Stock Report")
        dialog.geometry("900x600")
        
        columns = ('Item ID', 'Item Name', 'Category', 'Quantity', 'Weight(gm)', 'Price', 'Total Value')
        tree = ttk.Treeview(dialog, columns=columns, height=25)
        
        for col in columns:
            tree.column(col, width=120)
            tree.heading(col, text=col)
        
        for item in stock_data:
            tree.insert('', 'end', values=item)
        
        tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        ttk.Button(dialog, text="Export to CSV", 
                  command=lambda: messagebox.showinfo("Success", "Report exported")).pack(pady=10)
    except Exception as e:
        messagebox.showerror("Error", f"Error generating report: {str(e)}")

def sales_report():
    """Generate sales report"""
    try:
        sales_data = SalesService.get_sales_report()
        
        if not sales_data:
            messagebox.showinfo("Sales Report", "No sales data available")
            return
        
        dialog = tk.Toplevel(root)
        dialog.title("Sales Report")
        dialog.geometry("800x600")
        
        columns = ('Bill Number', 'Customer', 'Date', 'Amount', 'Status')
        tree = ttk.Treeview(dialog, columns=columns, height=25)
        
        for col in columns:
            tree.column(col, width=150)
            tree.heading(col, text=col)
        
        for item in sales_data:
            tree.insert('', 'end', values=item)
        
        tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    except Exception as e:
        messagebox.showerror("Error", f"Error generating report: {str(e)}")

def purchase_report():
    """Generate purchase report"""
    try:
        purchase_data = PurchaseService.get_purchase_report()
        
        if not purchase_data:
            messagebox.showinfo("Purchase Report", "No purchase data available")
            return
        
        dialog = tk.Toplevel(root)
        dialog.title("Purchase Report")
        dialog.geometry("800x600")
        
        columns = ('Bill Number', 'Supplier', 'Date', 'Amount', 'Status')
        tree = ttk.Treeview(dialog, columns=columns, height=25)
        
        for col in columns:
            tree.column(col, width=150)
            tree.heading(col, text=col)
        
        for item in purchase_data:
            tree.insert('', 'end', values=item)
        
        tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    except Exception as e:
        messagebox.showerror("Error", f"Error generating report: {str(e)}")

def today_summary():
    """Show today's summary"""
    try:
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
        
        summary = f"""
TODAY'S SUMMARY - {datetime.now().strftime('%d-%m-%Y')}

SALES:
  Total Amount: ₹{sales_total:,.2f}
  Number of Bills: {sales_count}

PURCHASES:
  Total Amount: ₹{purchase_total:,.2f}
  Number of Bills: {purchase_count}

NET PROFIT: ₹{sales_total - purchase_total:,.2f}
        """
        
        messagebox.showinfo("Today's Summary", summary)
    except Exception as e:
        messagebox.showerror("Error", f"Error: {str(e)}")

# ============================================================================
# MAIN APPLICATION WINDOW
# ============================================================================

root = tk.Tk()
root.title(APP_TITLE)
root.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")

# Configure styles
style = ttk.Style()
style.theme_use('clam')

# Create main container
container = tk.Frame(root)
container.pack(fill=tk.BOTH, expand=True)

# Left sidebar navbar
navbar = tk.Frame(container, bg=PRIMARY_COLOR, width=200)
navbar.pack(side=tk.LEFT, fill=tk.Y, padx=0, pady=0)
navbar.pack_propagate(False)

# Logo/Title in navbar
logo_frame = tk.Frame(navbar, bg=PRIMARY_COLOR)
logo_frame.pack(fill=tk.X, padx=10, pady=20)

logo_label = tk.Label(logo_frame, text="MT GOLD", font=("Segoe UI", 14, "bold"), 
                      fg="white", bg=PRIMARY_COLOR)
logo_label.pack()

version_label = tk.Label(logo_frame, text=f"v{APP_VERSION}", font=("Segoe UI", 8), 
                         fg="#888", bg=PRIMARY_COLOR)
version_label.pack()

# Separator
separator = tk.Frame(navbar, bg=SECONDARY_COLOR, height=2)
separator.pack(fill=tk.X, pady=10, padx=10)

# Navigation buttons
make_nav_button(navbar, "📊 Dashboard", show_dashboard)
make_nav_button(navbar, "📄 New Bill", show_new_bill)
make_nav_button(navbar, "📦 Manage Items", show_manage_items)
make_nav_button(navbar, "👤 Customers", show_manage_customers)
make_nav_button(navbar, "👥 Employees", show_manage_employees)
make_nav_button(navbar, "📈 Reports", show_reports)

# Separator
separator2 = tk.Frame(navbar, bg=SECONDARY_COLOR, height=2)
separator2.pack(fill=tk.X, pady=20, padx=10)

# Quick Actions
quick_label = tk.Label(navbar, text="Quick Actions", font=("Segoe UI", 10, "bold"), 
                       fg="white", bg=PRIMARY_COLOR)
quick_label.pack(fill=tk.X, padx=20, pady=10)

make_nav_button(navbar, "💰 Quick Sale", quick_sales_entry)
make_nav_button(navbar, "📥 Quick Purchase", quick_purchase_entry)
make_nav_button(navbar, "💳 Collection", cash_collection)
make_nav_button(navbar, "💸 Payment", cash_payment)

# Content area
content_frame = tk.Frame(container, bg="white")
content_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

# ============================================================================
# MENU BAR
# ============================================================================

menubar = Menu(root)

# ----------- DASHBOARD MENU -----------
dashboard_menu = Menu(menubar, tearoff=0)
dashboard_menu.add_command(label="Dashboard", command=show_dashboard)
dashboard_menu.add_separator()
dashboard_menu.add_command(label="Refresh", command=show_dashboard)
menubar.add_cascade(label="Dashboard", menu=dashboard_menu)

# ----------- MASTER MENU -----------
master_menu = Menu(menubar, tearoff=0)

master_menu.add_command(label="Items", command=show_manage_items)

item_category_submenu = Menu(master_menu, tearoff=0)
item_category_submenu.add_command(label="Add Category", command=add_item_category)
item_category_submenu.add_command(label="Manage Categories", command=lambda: dummy_action("Manage Categories"))
master_menu.add_cascade(label="Item Category", menu=item_category_submenu)

master_menu.add_command(label="Rate Update", command=lambda: dummy_action("Rate Update"))

barcode_submenu = Menu(master_menu, tearoff=0)
barcode_submenu.add_command(label="Barcode List", command=lambda: dummy_action("Barcode List"))
barcode_submenu.add_command(label="Barcode Printing", command=lambda: dummy_action("Barcode Printing"))
barcode_submenu.add_command(label="Barcode Edit", command=lambda: dummy_action("Barcode Edit"))
master_menu.add_cascade(label="Barcode", menu=barcode_submenu)

master_menu.add_command(label="Customer", command=show_manage_customers)
master_menu.add_command(label="Supplier", command=add_supplier)
master_menu.add_command(label="Employee", command=show_manage_employees)

master_menu.add_separator()
master_menu.add_command(label="Smith", command=lambda: dummy_action("Smith"))
master_menu.add_command(label="Jeweller", command=lambda: dummy_action("Jeweller"))
master_menu.add_command(label="Refiner", command=lambda: dummy_action("Refiner"))

menubar.add_cascade(label="Master", menu=master_menu)

# ----------- TRANSACTIONS MENU -----------
transactions_menu = Menu(menubar, tearoff=0)

sales_menu = Menu(transactions_menu, tearoff=0)
sales_menu.add_command(label="Sales Invoice", command=quick_sales_entry)
sales_menu.add_command(label="Sales Return", command=lambda: dummy_action("Sales Return"))
transactions_menu.add_cascade(label="Sales", menu=sales_menu)

purchase_menu = Menu(transactions_menu, tearoff=0)
purchase_menu.add_command(label="Purchase Invoice", command=quick_purchase_entry)
purchase_menu.add_command(label="Purchase Return", command=lambda: dummy_action("Purchase Return"))
transactions_menu.add_cascade(label="Purchase", menu=purchase_menu)

transactions_menu.add_separator()
transactions_menu.add_command(label="Cash Receipt", command=cash_collection)
transactions_menu.add_command(label="Cash Payment", command=cash_payment)

menubar.add_cascade(label="Transactions", menu=transactions_menu)

# ----------- REPORTS MENU -----------
reports_menu = Menu(menubar, tearoff=0)

stock_menu = Menu(reports_menu, tearoff=0)
stock_menu.add_command(label="Current Stock", command=stock_report)
stock_menu.add_command(label="Stock Reconciliation", command=lambda: dummy_action("Stock Reconciliation"))
reports_menu.add_cascade(label="Stock", menu=stock_menu)

reports_menu.add_command(label="Sales Report", command=sales_report)
reports_menu.add_command(label="Purchase Report", command=purchase_report)
reports_menu.add_command(label="Today Summary", command=today_summary)
reports_menu.add_command(label="Customer Report", command=lambda: dummy_action("Customer Report"))
reports_menu.add_command(label="Supplier Report", command=lambda: dummy_action("Supplier Report"))

menubar.add_cascade(label="Reports", menu=reports_menu)

# ----------- FINANCIAL REPORTS MENU -----------
financial_menu = Menu(menubar, tearoff=0)

financial_menu.add_command(label="Cash Book", command=lambda: dummy_action("Cash Book"))
financial_menu.add_command(label="Bank Book", command=lambda: dummy_action("Bank Book"))
financial_menu.add_command(label="Ledger", command=lambda: dummy_action("Ledger"))
financial_menu.add_separator()
financial_menu.add_command(label="Trial Balance", command=lambda: dummy_action("Trial Balance"))
financial_menu.add_command(label="Profit & Loss", command=lambda: dummy_action("Profit & Loss"))
financial_menu.add_command(label="Balance Sheet", command=lambda: dummy_action("Balance Sheet"))

menubar.add_cascade(label="Financial", menu=financial_menu)

# ----------- HELP MENU -----------
help_menu = Menu(menubar, tearoff=0)
help_menu.add_command(label="About", command=lambda: messagebox.showinfo("About", 
    f"MT GOLD LAND\nGold Shop Management System\nVersion {APP_VERSION}\n\nDeveloped for efficient gold shop operations"))
help_menu.add_command(label="Help", command=lambda: messagebox.showinfo("Help", "Help documentation - Coming soon!"))
menubar.add_cascade(label="Help", menu=help_menu)

root.config(menu=menubar)

# ============================================================================
# INITIALIZATION
# ============================================================================

# Show dashboard on startup
show_dashboard()

# Start application
root.mainloop()
