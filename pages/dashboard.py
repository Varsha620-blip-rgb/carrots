import tkinter as tk
from tkinter import ttk
from database.db import fetch_query
from datetime import datetime, timedelta
import matplotlib
matplotlib.use('TkAgg')
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

PRIMARY_COLOR = "#1e2d3d"
SECONDARY_COLOR = "#3a5068"
SUCCESS_COLOR = "#28a745"
WARNING_COLOR = "#ffc107"
INFO_COLOR = "#17a2b8"

def dashboard_page(parent):
    for widget in parent.winfo_children():
        widget.destroy()
    
    main_frame = ttk.Frame(parent)
    main_frame.pack(fill=tk.BOTH, expand=True)
    
    canvas = tk.Canvas(main_frame)
    scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
    scrollable_frame = ttk.Frame(canvas)
    
    scrollable_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
    )
    
    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)
    
    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")
    
    title_frame = ttk.Frame(scrollable_frame)
    title_frame.pack(fill=tk.X, padx=20, pady=10)
    
    title_label = ttk.Label(title_frame, text="Dashboard", font=("Segoe UI", 20, "bold"))
    title_label.pack(side=tk.LEFT)
    
    refresh_btn = ttk.Button(title_frame, text="Refresh", command=lambda: dashboard_page(parent))
    refresh_btn.pack(side=tk.RIGHT, padx=5)
    
    today = datetime.now().date()
    
    total_customers = fetch_query("SELECT COUNT(*) FROM customers")[0][0]
    total_items = fetch_query("SELECT COUNT(*) FROM items WHERE is_active = 1")[0][0]
    total_employees = fetch_query("SELECT COUNT(*) FROM employees WHERE status = 'Active'")[0][0]
    total_suppliers = fetch_query("SELECT COUNT(*) FROM suppliers")[0][0]
    
    today_sales = fetch_query("""
        SELECT COALESCE(SUM(total_amount), 0)
        FROM bills
        WHERE bill_type = 'Sales' AND DATE(bill_date) = ?
    """, (today,))[0][0]
    
    today_purchases = fetch_query("""
        SELECT COALESCE(SUM(total_amount), 0)
        FROM bills
        WHERE bill_type = 'Purchase' AND DATE(bill_date) = ?
    """, (today,))[0][0]
    
    total_stock_value = fetch_query("""
        SELECT COALESCE(SUM(quantity * price), 0) FROM items WHERE is_active = 1
    """)[0][0]
    
    current_rate = fetch_query("""
        SELECT rate_per_gram FROM gold_rates 
        WHERE purity = '22K' AND is_active = 1
        ORDER BY rate_date DESC LIMIT 1
    """)
    gold_rate_22k = current_rate[0][0] if current_rate else 0
    
    stats_frame = ttk.Frame(scrollable_frame)
    stats_frame.pack(fill=tk.X, padx=20, pady=10)
    
    stats = [
        ("Today's Sales", f"₹{today_sales:,.2f}", SUCCESS_COLOR),
        ("Today's Purchases", f"₹{today_purchases:,.2f}", WARNING_COLOR),
        ("Gold Rate (22K)", f"₹{gold_rate_22k:,.2f}/gm", INFO_COLOR),
        ("Stock Value", f"₹{total_stock_value:,.2f}", PRIMARY_COLOR),
    ]
    
    for i, (title, value, color) in enumerate(stats):
        create_stat_card(stats_frame, title, value, i, color)
    
    stats_frame2 = ttk.Frame(scrollable_frame)
    stats_frame2.pack(fill=tk.X, padx=20, pady=10)
    
    stats2 = [
        ("Total Customers", str(total_customers), INFO_COLOR),
        ("Total Items", str(total_items), SUCCESS_COLOR),
        ("Active Employees", str(total_employees), WARNING_COLOR),
        ("Total Suppliers", str(total_suppliers), SECONDARY_COLOR),
    ]
    
    for i, (title, value, color) in enumerate(stats2):
        create_stat_card(stats_frame2, title, value, i, color)
    
    charts_frame = ttk.Frame(scrollable_frame)
    charts_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
    
    left_chart = ttk.LabelFrame(charts_frame, text="Sales vs Purchases (Last 7 Days)", padding=10)
    left_chart.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
    
    create_sales_chart(left_chart)
    
    right_chart = ttk.LabelFrame(charts_frame, text="Stock Distribution by Category", padding=10)
    right_chart.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
    
    create_stock_pie_chart(right_chart)
    
    bottom_frame = ttk.Frame(scrollable_frame)
    bottom_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
    
    recent_sales_frame = ttk.LabelFrame(bottom_frame, text="Recent Sales", padding=10)
    recent_sales_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
    
    create_recent_sales_table(recent_sales_frame)
    
    top_items_frame = ttk.LabelFrame(bottom_frame, text="Top Items by Value", padding=10)
    top_items_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
    
    create_top_items_chart(top_items_frame)

def create_stat_card(parent, title, value, column, color):
    card = tk.Frame(parent, bg="white", relief=tk.RAISED, bd=1)
    card.grid(row=0, column=column, padx=10, pady=5, sticky='nsew')
    parent.columnconfigure(column, weight=1)
    
    color_bar = tk.Frame(card, bg=color, height=4)
    color_bar.pack(fill=tk.X)
    
    content = tk.Frame(card, bg="white", padx=15, pady=10)
    content.pack(fill=tk.BOTH, expand=True)
    
    title_lbl = tk.Label(content, text=title, font=("Segoe UI", 10), bg="white", fg="#666")
    title_lbl.pack(anchor="w")
    
    value_lbl = tk.Label(content, text=value, font=("Segoe UI", 18, "bold"), bg="white", fg="#333")
    value_lbl.pack(anchor="w")

def create_sales_chart(parent):
    dates = []
    sales_data = []
    purchase_data = []
    
    for i in range(6, -1, -1):
        date = datetime.now().date() - timedelta(days=i)
        dates.append(date.strftime("%d/%m"))
        
        sale = fetch_query("""
            SELECT COALESCE(SUM(total_amount), 0)
            FROM bills WHERE bill_type = 'Sales' AND DATE(bill_date) = ?
        """, (date,))[0][0]
        sales_data.append(float(sale))
        
        purchase = fetch_query("""
            SELECT COALESCE(SUM(total_amount), 0)
            FROM bills WHERE bill_type = 'Purchase' AND DATE(bill_date) = ?
        """, (date,))[0][0]
        purchase_data.append(float(purchase))
    
    fig = Figure(figsize=(5, 3), dpi=100)
    ax = fig.add_subplot(111)
    
    x = range(len(dates))
    width = 0.35
    
    bars1 = ax.bar([i - width/2 for i in x], sales_data, width, label='Sales', color=SUCCESS_COLOR)
    bars2 = ax.bar([i + width/2 for i in x], purchase_data, width, label='Purchases', color=WARNING_COLOR)
    
    ax.set_ylabel('Amount (₹)')
    ax.set_xticks(x)
    ax.set_xticklabels(dates, rotation=45)
    ax.legend()
    ax.set_facecolor('#f8f9fa')
    fig.patch.set_facecolor('#f8f9fa')
    fig.tight_layout()
    
    canvas = FigureCanvasTkAgg(fig, master=parent)
    canvas.draw()
    canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

def create_stock_pie_chart(parent):
    category_data = fetch_query("""
        SELECT COALESCE(ic.name, 'Uncategorized') as category, 
               COUNT(*) as count,
               COALESCE(SUM(i.quantity * i.price), 0) as value
        FROM items i
        LEFT JOIN item_categories ic ON i.category_id = ic.id
        WHERE i.is_active = 1
        GROUP BY ic.name
        ORDER BY value DESC
        LIMIT 6
    """)
    
    if not category_data or all(row[2] == 0 for row in category_data):
        no_data_label = ttk.Label(parent, text="No stock data available", font=("Segoe UI", 12))
        no_data_label.pack(expand=True)
        return
    
    labels = [row[0] for row in category_data]
    sizes = [float(row[2]) for row in category_data]
    colors = ['#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0', '#9966FF', '#FF9F40']
    
    fig = Figure(figsize=(4, 3), dpi=100)
    ax = fig.add_subplot(111)
    
    wedges, texts, autotexts = ax.pie(sizes, labels=labels, colors=colors[:len(sizes)], 
                                       autopct='%1.1f%%', startangle=90)
    ax.axis('equal')
    fig.patch.set_facecolor('#f8f9fa')
    fig.tight_layout()
    
    canvas = FigureCanvasTkAgg(fig, master=parent)
    canvas.draw()
    canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

def create_recent_sales_table(parent):
    columns = ('Bill #', 'Customer', 'Amount', 'Date')
    tree = ttk.Treeview(parent, columns=columns, height=6, show='headings')
    
    for col in columns:
        tree.heading(col, text=col)
        tree.column(col, width=100)
    
    recent_sales = fetch_query("""
        SELECT b.bill_number, COALESCE(c.name, 'Walk-in'), b.total_amount, b.bill_date
        FROM bills b
        LEFT JOIN customers c ON b.customer_id = c.id
        WHERE b.bill_type = 'Sales'
        ORDER BY b.date_created DESC
        LIMIT 5
    """)
    
    for sale in recent_sales:
        tree.insert('', 'end', values=(sale[0], sale[1], f"₹{sale[2]:,.2f}", sale[3]))
    
    tree.pack(fill=tk.BOTH, expand=True)

def create_top_items_chart(parent):
    items_data = fetch_query("""
        SELECT name, quantity * price as value
        FROM items
        WHERE is_active = 1 AND quantity > 0
        ORDER BY value DESC
        LIMIT 5
    """)
    
    if not items_data:
        no_data_label = ttk.Label(parent, text="No items data available", font=("Segoe UI", 12))
        no_data_label.pack(expand=True)
        return
    
    names = [row[0][:15] + '...' if len(row[0]) > 15 else row[0] for row in items_data]
    values = [float(row[1]) for row in items_data]
    
    fig = Figure(figsize=(4, 3), dpi=100)
    ax = fig.add_subplot(111)
    
    bars = ax.barh(names, values, color=INFO_COLOR)
    ax.set_xlabel('Value (₹)')
    ax.invert_yaxis()
    ax.set_facecolor('#f8f9fa')
    fig.patch.set_facecolor('#f8f9fa')
    fig.tight_layout()
    
    canvas = FigureCanvasTkAgg(fig, master=parent)
    canvas.draw()
    canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
