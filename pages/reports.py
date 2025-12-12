import tkinter as tk
from tkinter import messagebox, ttk, filedialog
from database.db import fetch_query
from datetime import datetime, timedelta
import pandas as pd
import os

def reports_page(parent):
    for widget in parent.winfo_children():
        widget.destroy()
    
    frame = ttk.Frame(parent)
    frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    
    title_label = ttk.Label(frame, text="Reports", font=("Segoe UI", 16, "bold"))
    title_label.pack(pady=10)
    
    date_frame = ttk.LabelFrame(frame, text="Date Range", padding=10)
    date_frame.pack(fill=tk.X, pady=5)
    
    ttk.Label(date_frame, text="From:").pack(side=tk.LEFT, padx=5)
    from_date = ttk.Entry(date_frame, width=12)
    from_date.insert(0, (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d'))
    from_date.pack(side=tk.LEFT, padx=5)
    
    ttk.Label(date_frame, text="To:").pack(side=tk.LEFT, padx=5)
    to_date = ttk.Entry(date_frame, width=12)
    to_date.insert(0, datetime.now().strftime('%Y-%m-%d'))
    to_date.pack(side=tk.LEFT, padx=5)
    
    button_frame = ttk.Frame(frame)
    button_frame.pack(fill=tk.X, pady=10)
    
    ttk.Button(button_frame, text="Stock Report", command=lambda: show_stock_report(frame, from_date.get(), to_date.get())).pack(side=tk.LEFT, padx=5)
    ttk.Button(button_frame, text="Sales Report", command=lambda: show_sales_report(frame, from_date.get(), to_date.get())).pack(side=tk.LEFT, padx=5)
    ttk.Button(button_frame, text="Purchase Report", command=lambda: show_purchase_report(frame, from_date.get(), to_date.get())).pack(side=tk.LEFT, padx=5)
    ttk.Button(button_frame, text="Customer Report", command=lambda: show_customer_report(frame)).pack(side=tk.LEFT, padx=5)
    ttk.Button(button_frame, text="Daily Summary", command=lambda: show_daily_summary(frame, from_date.get(), to_date.get())).pack(side=tk.LEFT, padx=5)
    
    global report_frame
    report_frame = ttk.Frame(frame)
    report_frame.pack(fill=tk.BOTH, expand=True, pady=10)
    
    info_label = ttk.Label(report_frame, text="Select a report type to view", font=("Segoe UI", 12))
    info_label.pack(expand=True)

def clear_report_frame():
    for widget in report_frame.winfo_children():
        widget.destroy()

def show_stock_report(parent, from_date, to_date):
    clear_report_frame()
    
    title = ttk.Label(report_frame, text="Stock Report", font=("Segoe UI", 14, "bold"))
    title.pack(pady=10)
    
    data = fetch_query("""
        SELECT i.id, i.name, COALESCE(ic.name, 'Uncategorized') as category, 
               i.quantity, i.weight_in_gm, i.purity, i.price,
               (i.quantity * i.price) as total_value
        FROM items i
        LEFT JOIN item_categories ic ON i.category_id = ic.id
        WHERE i.is_active = 1
        ORDER BY ic.name, i.name
    """)
    
    columns = ('ID', 'Item Name', 'Category', 'Qty', 'Weight(gm)', 'Purity', 'Price', 'Total Value')
    tree = ttk.Treeview(report_frame, columns=columns, height=15, show='headings')
    
    widths = {'ID': 40, 'Item Name': 150, 'Category': 100, 'Qty': 60, 'Weight(gm)': 80, 'Purity': 60, 'Price': 100, 'Total Value': 120}
    for col in columns:
        tree.heading(col, text=col)
        tree.column(col, width=widths.get(col, 100), anchor='center')
    
    total_qty = 0
    total_weight = 0
    total_value = 0
    
    for row in data:
        tree.insert('', 'end', values=(
            row[0], row[1], row[2], row[3], f"{row[4]:.2f}",
            row[5] or 'N/A', f"₹{row[6]:,.2f}", f"₹{row[7]:,.2f}"
        ))
        total_qty += row[3] or 0
        total_weight += row[4] or 0
        total_value += row[7] or 0
    
    scrollbar = ttk.Scrollbar(report_frame, orient=tk.VERTICAL, command=tree.yview)
    tree.configure(yscroll=scrollbar.set)
    tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
    summary = ttk.Frame(report_frame)
    summary.pack(fill=tk.X, pady=10)
    
    ttk.Label(summary, text=f"Total Items: {len(data)} | Total Qty: {total_qty} | Total Weight: {total_weight:.2f}gm | Total Value: ₹{total_value:,.2f}", font=("Segoe UI", 10, "bold")).pack()
    
    def export_report():
        export_to_excel(data, columns, "Stock_Report")
    
    ttk.Button(summary, text="Export to Excel", command=export_report).pack(pady=5)

def show_sales_report(parent, from_date, to_date):
    clear_report_frame()
    
    title = ttk.Label(report_frame, text=f"Sales Report ({from_date} to {to_date})", font=("Segoe UI", 14, "bold"))
    title.pack(pady=10)
    
    data = fetch_query("""
        SELECT b.bill_number, b.bill_date, COALESCE(c.name, 'Walk-in') as customer,
               b.total_amount, b.discount_amount, b.paid_amount, b.outstanding_amount, b.status
        FROM bills b
        LEFT JOIN customers c ON b.customer_id = c.id
        WHERE b.bill_type = 'Sales' AND b.bill_date BETWEEN ? AND ?
        ORDER BY b.bill_date DESC
    """, (from_date, to_date))
    
    columns = ('Bill #', 'Date', 'Customer', 'Amount', 'Discount', 'Paid', 'Outstanding', 'Status')
    tree = ttk.Treeview(report_frame, columns=columns, height=15, show='headings')
    
    for col in columns:
        tree.heading(col, text=col)
        tree.column(col, width=100, anchor='center')
    
    total_sales = 0
    total_paid = 0
    total_outstanding = 0
    
    for row in data:
        tree.insert('', 'end', values=(
            row[0], row[1], row[2], f"₹{row[3]:,.2f}",
            f"₹{row[4]:,.2f}", f"₹{row[5]:,.2f}", f"₹{row[6]:,.2f}", row[7]
        ))
        if row[7] != 'Cancelled':
            total_sales += row[3] or 0
            total_paid += row[5] or 0
            total_outstanding += row[6] or 0
    
    scrollbar = ttk.Scrollbar(report_frame, orient=tk.VERTICAL, command=tree.yview)
    tree.configure(yscroll=scrollbar.set)
    tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
    summary = ttk.Frame(report_frame)
    summary.pack(fill=tk.X, pady=10)
    
    ttk.Label(summary, text=f"Total Bills: {len(data)} | Total Sales: ₹{total_sales:,.2f} | Collected: ₹{total_paid:,.2f} | Outstanding: ₹{total_outstanding:,.2f}", font=("Segoe UI", 10, "bold")).pack()
    
    def export_report():
        export_to_excel(data, columns, "Sales_Report")
    
    ttk.Button(summary, text="Export to Excel", command=export_report).pack(pady=5)

def show_purchase_report(parent, from_date, to_date):
    clear_report_frame()
    
    title = ttk.Label(report_frame, text=f"Purchase Report ({from_date} to {to_date})", font=("Segoe UI", 14, "bold"))
    title.pack(pady=10)
    
    data = fetch_query("""
        SELECT b.bill_number, b.bill_date, COALESCE(s.name, 'Unknown') as supplier,
               b.total_amount, b.discount_amount, b.paid_amount, b.outstanding_amount, b.status
        FROM bills b
        LEFT JOIN suppliers s ON b.supplier_id = s.id
        WHERE b.bill_type = 'Purchase' AND b.bill_date BETWEEN ? AND ?
        ORDER BY b.bill_date DESC
    """, (from_date, to_date))
    
    columns = ('Bill #', 'Date', 'Supplier', 'Amount', 'Discount', 'Paid', 'Outstanding', 'Status')
    tree = ttk.Treeview(report_frame, columns=columns, height=15, show='headings')
    
    for col in columns:
        tree.heading(col, text=col)
        tree.column(col, width=100, anchor='center')
    
    total_purchases = 0
    total_paid = 0
    total_outstanding = 0
    
    for row in data:
        tree.insert('', 'end', values=(
            row[0], row[1], row[2], f"₹{row[3]:,.2f}",
            f"₹{row[4]:,.2f}", f"₹{row[5]:,.2f}", f"₹{row[6]:,.2f}", row[7]
        ))
        if row[7] != 'Cancelled':
            total_purchases += row[3] or 0
            total_paid += row[5] or 0
            total_outstanding += row[6] or 0
    
    scrollbar = ttk.Scrollbar(report_frame, orient=tk.VERTICAL, command=tree.yview)
    tree.configure(yscroll=scrollbar.set)
    tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
    summary = ttk.Frame(report_frame)
    summary.pack(fill=tk.X, pady=10)
    
    ttk.Label(summary, text=f"Total Bills: {len(data)} | Total Purchases: ₹{total_purchases:,.2f} | Paid: ₹{total_paid:,.2f} | Payable: ₹{total_outstanding:,.2f}", font=("Segoe UI", 10, "bold")).pack()
    
    def export_report():
        export_to_excel(data, columns, "Purchase_Report")
    
    ttk.Button(summary, text="Export to Excel", command=export_report).pack(pady=5)

def show_customer_report(parent):
    clear_report_frame()
    
    title = ttk.Label(report_frame, text="Customer Report", font=("Segoe UI", 14, "bold"))
    title.pack(pady=10)
    
    data = fetch_query("""
        SELECT c.id, c.name, c.phone, c.city, c.credit_limit, c.outstanding_balance,
               COUNT(b.id) as total_bills,
               COALESCE(SUM(CASE WHEN b.status != 'Cancelled' THEN b.total_amount ELSE 0 END), 0) as total_business
        FROM customers c
        LEFT JOIN bills b ON c.id = b.customer_id
        GROUP BY c.id
        ORDER BY total_business DESC
    """)
    
    columns = ('ID', 'Name', 'Phone', 'City', 'Credit Limit', 'Outstanding', 'Bills', 'Total Business')
    tree = ttk.Treeview(report_frame, columns=columns, height=15, show='headings')
    
    for col in columns:
        tree.heading(col, text=col)
        tree.column(col, width=100, anchor='center')
    
    total_outstanding = 0
    total_business = 0
    
    for row in data:
        tree.insert('', 'end', values=(
            row[0], row[1], row[2] or 'N/A', row[3] or 'N/A',
            f"₹{row[4]:,.2f}", f"₹{row[5]:,.2f}", row[6], f"₹{row[7]:,.2f}"
        ))
        total_outstanding += row[5] or 0
        total_business += row[7] or 0
    
    scrollbar = ttk.Scrollbar(report_frame, orient=tk.VERTICAL, command=tree.yview)
    tree.configure(yscroll=scrollbar.set)
    tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
    summary = ttk.Frame(report_frame)
    summary.pack(fill=tk.X, pady=10)
    
    ttk.Label(summary, text=f"Total Customers: {len(data)} | Total Outstanding: ₹{total_outstanding:,.2f} | Total Business: ₹{total_business:,.2f}", font=("Segoe UI", 10, "bold")).pack()
    
    def export_report():
        export_to_excel(data, columns, "Customer_Report")
    
    ttk.Button(summary, text="Export to Excel", command=export_report).pack(pady=5)

def show_daily_summary(parent, from_date, to_date):
    clear_report_frame()
    
    title = ttk.Label(report_frame, text=f"Daily Summary ({from_date} to {to_date})", font=("Segoe UI", 14, "bold"))
    title.pack(pady=10)
    
    data = fetch_query("""
        SELECT DATE(bill_date) as date,
               SUM(CASE WHEN bill_type = 'Sales' AND status != 'Cancelled' THEN total_amount ELSE 0 END) as sales,
               SUM(CASE WHEN bill_type = 'Purchase' AND status != 'Cancelled' THEN total_amount ELSE 0 END) as purchases,
               COUNT(CASE WHEN bill_type = 'Sales' THEN 1 END) as sales_count,
               COUNT(CASE WHEN bill_type = 'Purchase' THEN 1 END) as purchase_count
        FROM bills
        WHERE bill_date BETWEEN ? AND ?
        GROUP BY DATE(bill_date)
        ORDER BY date DESC
    """, (from_date, to_date))
    
    columns = ('Date', 'Sales', 'Purchases', 'Net', 'Sales Bills', 'Purchase Bills')
    tree = ttk.Treeview(report_frame, columns=columns, height=15, show='headings')
    
    for col in columns:
        tree.heading(col, text=col)
        tree.column(col, width=120, anchor='center')
    
    total_sales = 0
    total_purchases = 0
    
    for row in data:
        net = (row[1] or 0) - (row[2] or 0)
        tree.insert('', 'end', values=(
            row[0], f"₹{row[1]:,.2f}", f"₹{row[2]:,.2f}",
            f"₹{net:,.2f}", row[3], row[4]
        ))
        total_sales += row[1] or 0
        total_purchases += row[2] or 0
    
    scrollbar = ttk.Scrollbar(report_frame, orient=tk.VERTICAL, command=tree.yview)
    tree.configure(yscroll=scrollbar.set)
    tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
    summary = ttk.Frame(report_frame)
    summary.pack(fill=tk.X, pady=10)
    
    net_total = total_sales - total_purchases
    ttk.Label(summary, text=f"Total Sales: ₹{total_sales:,.2f} | Total Purchases: ₹{total_purchases:,.2f} | Net: ₹{net_total:,.2f}", font=("Segoe UI", 10, "bold")).pack()
    
    def export_report():
        export_to_excel(data, columns, "Daily_Summary")
    
    ttk.Button(summary, text="Export to Excel", command=export_report).pack(pady=5)

def export_to_excel(data, columns, filename):
    try:
        exports_dir = "exports"
        if not os.path.exists(exports_dir):
            os.makedirs(exports_dir)
        
        filepath = os.path.join(exports_dir, f"{filename}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx")
        
        df = pd.DataFrame(data, columns=columns)
        df.to_excel(filepath, index=False)
        
        messagebox.showinfo("Success", f"Report exported successfully!\n\nFile: {filepath}")
    except Exception as e:
        messagebox.showerror("Error", f"Error exporting report: {str(e)}")
