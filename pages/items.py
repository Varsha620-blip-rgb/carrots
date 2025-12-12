import tkinter as tk
from tkinter import messagebox, ttk
from database.db import execute_query, fetch_query, fetch_one
from datetime import datetime
from services.stock_service import StockService

items_tree = None

def items_page(parent):
    global items_tree
    
    for widget in parent.winfo_children():
        widget.destroy()
    
    frame = ttk.Frame(parent)
    frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    
    title_frame = ttk.Frame(frame)
    title_frame.pack(fill=tk.X, pady=10)
    
    title_label = ttk.Label(title_frame, text="Item Management (Gold & Diamond)", font=("Segoe UI", 16, "bold"))
    title_label.pack(side=tk.LEFT)
    
    filter_frame = ttk.Frame(frame)
    filter_frame.pack(fill=tk.X, pady=5)
    
    ttk.Label(filter_frame, text="Material:").pack(side=tk.LEFT, padx=5)
    material_var = tk.StringVar(value="All")
    material_combo = ttk.Combobox(filter_frame, textvariable=material_var, 
                                   values=['All', 'Gold', 'Diamond', 'Silver', 'Platinum'], width=12)
    material_combo.pack(side=tk.LEFT, padx=5)
    
    ttk.Label(filter_frame, text="Search:").pack(side=tk.LEFT, padx=10)
    search_var = tk.StringVar()
    search_entry = ttk.Entry(filter_frame, textvariable=search_var, width=25)
    search_entry.pack(side=tk.LEFT, padx=5)
    
    def search_items():
        refresh_items_list(items_tree, search_var.get(), material_var.get())
    
    ttk.Button(filter_frame, text="Search", command=search_items).pack(side=tk.LEFT, padx=5)
    ttk.Button(filter_frame, text="Clear", command=lambda: [search_var.set(""), material_var.set("All"), refresh_items_list(items_tree)]).pack(side=tk.LEFT, padx=5)
    
    button_frame = ttk.Frame(frame)
    button_frame.pack(fill=tk.X, pady=10)
    
    ttk.Button(button_frame, text="Add Item", command=lambda: show_add_item_dialog(parent)).pack(side=tk.LEFT, padx=5)
    ttk.Button(button_frame, text="Edit Item", command=lambda: show_edit_item_dialog(parent, items_tree)).pack(side=tk.LEFT, padx=5)
    ttk.Button(button_frame, text="Delete Item", command=lambda: delete_item(items_tree)).pack(side=tk.LEFT, padx=5)
    ttk.Button(button_frame, text="Adjust Stock", command=lambda: show_stock_adjustment_dialog(parent, items_tree)).pack(side=tk.LEFT, padx=5)
    ttk.Button(button_frame, text="View Details", command=lambda: view_item_details(items_tree)).pack(side=tk.LEFT, padx=5)
    ttk.Button(button_frame, text="Stock History", command=lambda: view_stock_history(items_tree)).pack(side=tk.LEFT, padx=5)
    ttk.Button(button_frame, text="Refresh", command=lambda: refresh_items_list(items_tree)).pack(side=tk.LEFT, padx=5)
    
    tree_frame = ttk.Frame(frame)
    tree_frame.pack(fill=tk.BOTH, expand=True)
    
    columns = ('ID', 'Name', 'Material', 'Category', 'Price', 'Stock', 'Weight', 'Purity/Clarity', 'Barcode')
    items_tree = ttk.Treeview(tree_frame, columns=columns, height=15, show='headings')
    
    col_widths = {'ID': 50, 'Name': 150, 'Material': 80, 'Category': 100, 'Price': 100, 
                  'Stock': 60, 'Weight': 80, 'Purity/Clarity': 80, 'Barcode': 100}
    
    for col in columns:
        items_tree.column(col, width=col_widths.get(col, 100), anchor='center')
        items_tree.heading(col, text=col, command=lambda c=col: sort_column(items_tree, c, False))
    
    scrollbar_y = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=items_tree.yview)
    items_tree.configure(yscroll=scrollbar_y.set)
    
    items_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y)
    
    items_tree.bind('<Double-1>', lambda e: view_item_details(items_tree))
    
    refresh_items_list(items_tree)
    
    status_frame = ttk.Frame(frame)
    status_frame.pack(fill=tk.X, pady=5)
    
    stats = get_item_stats()
    ttk.Label(status_frame, text=f"Total Items: {stats['total']} | Gold: {stats['gold']} | Diamond: {stats['diamond']} | Low Stock: {stats['low_stock']}").pack(side=tk.LEFT)

def get_item_stats():
    total = fetch_query("SELECT COUNT(*) FROM items WHERE is_active = 1")[0][0]
    gold = fetch_query("""
        SELECT COUNT(*) FROM items i
        JOIN materials m ON i.material_id = m.id
        WHERE i.is_active = 1 AND m.name = 'Gold'
    """)[0][0]
    diamond = fetch_query("""
        SELECT COUNT(*) FROM items i
        JOIN materials m ON i.material_id = m.id
        WHERE i.is_active = 1 AND m.name = 'Diamond'
    """)[0][0]
    low_stock = fetch_query("SELECT COUNT(*) FROM items WHERE is_active = 1 AND quantity <= 2")[0][0]
    return {'total': total, 'gold': gold, 'diamond': diamond, 'low_stock': low_stock}

def sort_column(tree, col, reverse):
    items = [(tree.set(k, col), k) for k in tree.get_children('')]
    try:
        items.sort(key=lambda t: float(t[0].replace('₹','').replace(',','')) if '₹' in t[0] else (float(t[0]) if t[0].replace('.','',1).replace('-','').isdigit() else t[0]), reverse=reverse)
    except:
        items.sort(reverse=reverse)
    
    for index, (val, k) in enumerate(items):
        tree.move(k, '', index)
    
    tree.heading(col, command=lambda: sort_column(tree, col, not reverse))

def refresh_items_list(tree, search_term="", material_filter="All"):
    if tree is None:
        return
        
    for item in tree.get_children():
        tree.delete(item)
    
    query = """
        SELECT i.id, i.name, COALESCE(m.name, 'N/A'), COALESCE(ic.name, 'N/A'), i.price, 
               i.quantity, i.weight_in_gm, 
               CASE WHEN m.name = 'Diamond' THEN i.diamond_clarity ELSE i.purity END as quality,
               i.barcode
        FROM items i
        LEFT JOIN item_categories ic ON i.category_id = ic.id
        LEFT JOIN materials m ON i.material_id = m.id
        WHERE i.is_active = 1
    """
    params = []
    
    if search_term:
        query += " AND (i.name LIKE ? OR i.barcode LIKE ? OR ic.name LIKE ?)"
        search_pattern = f"%{search_term}%"
        params.extend([search_pattern, search_pattern, search_pattern])
    
    if material_filter and material_filter != "All":
        query += " AND m.name = ?"
        params.append(material_filter)
    
    query += " ORDER BY i.name"
    
    items = fetch_query(query, tuple(params)) if params else fetch_query(query)
    
    for item in items:
        formatted_item = (
            item[0], item[1], item[2], item[3],
            f"₹{item[4]:,.2f}" if item[4] else "₹0.00",
            item[5], f"{item[6]:.3f}" if item[6] else "0.000", 
            item[7] or "N/A", item[8] or "N/A"
        )
        tree.insert('', 'end', values=formatted_item)

def get_categories():
    categories = fetch_query("SELECT id, name FROM item_categories ORDER BY name")
    return {cat[1]: cat[0] for cat in categories}

def get_materials():
    materials = fetch_query("SELECT id, name FROM materials WHERE is_active = 1 ORDER BY name")
    return {mat[1]: mat[0] for mat in materials}

def show_add_item_dialog(parent):
    dialog = tk.Toplevel(parent)
    dialog.title("Add New Item (Gold/Diamond)")
    dialog.geometry("550x750")
    dialog.transient(parent)
    dialog.grab_set()
    
    canvas = tk.Canvas(dialog)
    scrollbar = ttk.Scrollbar(dialog, orient="vertical", command=canvas.yview)
    scrollable_frame = ttk.Frame(canvas)
    
    scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)
    
    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")
    
    main_frame = ttk.Frame(scrollable_frame, padding=20)
    main_frame.pack(fill=tk.BOTH, expand=True)
    
    ttk.Label(main_frame, text="Add New Item", font=("Segoe UI", 14, "bold")).pack(pady=10)
    
    form_frame = ttk.Frame(main_frame)
    form_frame.pack(fill=tk.X)
    
    fields = {}
    materials = get_materials()
    categories = get_categories()
    
    row = 0
    ttk.Label(form_frame, text="Material Type *:").grid(row=row, column=0, sticky='w', pady=5)
    fields['material'] = ttk.Combobox(form_frame, values=list(materials.keys()), width=32, state='readonly')
    fields['material'].set('Gold')
    fields['material'].grid(row=row, column=1, pady=5, padx=5)
    
    row += 1
    ttk.Label(form_frame, text="Item Name *:").grid(row=row, column=0, sticky='w', pady=5)
    fields['name'] = ttk.Entry(form_frame, width=35)
    fields['name'].grid(row=row, column=1, pady=5, padx=5)
    
    row += 1
    ttk.Label(form_frame, text="Category:").grid(row=row, column=0, sticky='w', pady=5)
    fields['category'] = ttk.Combobox(form_frame, values=list(categories.keys()), width=32)
    fields['category'].grid(row=row, column=1, pady=5, padx=5)
    
    row += 1
    ttk.Label(form_frame, text="Price (₹) *:").grid(row=row, column=0, sticky='w', pady=5)
    fields['price'] = ttk.Entry(form_frame, width=35)
    fields['price'].grid(row=row, column=1, pady=5, padx=5)
    
    row += 1
    ttk.Label(form_frame, text="Cost Price (₹):").grid(row=row, column=0, sticky='w', pady=5)
    fields['cost_price'] = ttk.Entry(form_frame, width=35)
    fields['cost_price'].grid(row=row, column=1, pady=5, padx=5)
    
    row += 1
    ttk.Label(form_frame, text="Quantity:").grid(row=row, column=0, sticky='w', pady=5)
    fields['quantity'] = ttk.Entry(form_frame, width=35)
    fields['quantity'].insert(0, "1")
    fields['quantity'].grid(row=row, column=1, pady=5, padx=5)
    
    row += 1
    ttk.Label(form_frame, text="Gross Weight (gm):").grid(row=row, column=0, sticky='w', pady=5)
    fields['weight'] = ttk.Entry(form_frame, width=35)
    fields['weight'].insert(0, "0")
    fields['weight'].grid(row=row, column=1, pady=5, padx=5)
    
    gold_frame = ttk.LabelFrame(form_frame, text="Gold Details", padding=10)
    gold_frame.grid(row=row+1, column=0, columnspan=2, sticky='ew', pady=10)
    
    gold_fields = {}
    ttk.Label(gold_frame, text="Purity:").grid(row=0, column=0, sticky='w', pady=3)
    gold_fields['purity'] = ttk.Combobox(gold_frame, values=['24K', '22K', '21K', '18K', '14K', '916', '875', '750', '585'], width=15)
    gold_fields['purity'].set('22K')
    gold_fields['purity'].grid(row=0, column=1, pady=3, padx=5)
    
    ttk.Label(gold_frame, text="Gold Weight (gm):").grid(row=0, column=2, sticky='w', pady=3, padx=10)
    gold_fields['gold_weight'] = ttk.Entry(gold_frame, width=12)
    gold_fields['gold_weight'].insert(0, "0")
    gold_fields['gold_weight'].grid(row=0, column=3, pady=3)
    
    ttk.Label(gold_frame, text="Making Charges:").grid(row=1, column=0, sticky='w', pady=3)
    gold_fields['making_charges'] = ttk.Entry(gold_frame, width=18)
    gold_fields['making_charges'].insert(0, "0")
    gold_fields['making_charges'].grid(row=1, column=1, pady=3, padx=5)
    
    ttk.Label(gold_frame, text="Hallmark:").grid(row=1, column=2, sticky='w', pady=3, padx=10)
    gold_fields['hallmark'] = ttk.Entry(gold_frame, width=12)
    gold_fields['hallmark'].grid(row=1, column=3, pady=3)
    
    diamond_frame = ttk.LabelFrame(form_frame, text="Diamond Details", padding=10)
    diamond_frame.grid(row=row+2, column=0, columnspan=2, sticky='ew', pady=10)
    
    diamond_fields = {}
    ttk.Label(diamond_frame, text="Clarity:").grid(row=0, column=0, sticky='w', pady=3)
    diamond_fields['clarity'] = ttk.Combobox(diamond_frame, values=['FL', 'IF', 'VVS1', 'VVS2', 'VS1', 'VS2', 'SI1', 'SI2', 'I1', 'I2'], width=10)
    diamond_fields['clarity'].grid(row=0, column=1, pady=3, padx=5)
    
    ttk.Label(diamond_frame, text="Color:").grid(row=0, column=2, sticky='w', pady=3, padx=10)
    diamond_fields['color'] = ttk.Combobox(diamond_frame, values=['D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M'], width=8)
    diamond_fields['color'].grid(row=0, column=3, pady=3)
    
    ttk.Label(diamond_frame, text="Cut:").grid(row=1, column=0, sticky='w', pady=3)
    diamond_fields['cut'] = ttk.Combobox(diamond_frame, values=['Excellent', 'Very Good', 'Good', 'Fair', 'Poor'], width=10)
    diamond_fields['cut'].grid(row=1, column=1, pady=3, padx=5)
    
    ttk.Label(diamond_frame, text="Carat:").grid(row=1, column=2, sticky='w', pady=3, padx=10)
    diamond_fields['carat'] = ttk.Entry(diamond_frame, width=10)
    diamond_fields['carat'].insert(0, "0")
    diamond_fields['carat'].grid(row=1, column=3, pady=3)
    
    ttk.Label(diamond_frame, text="Diamond Count:").grid(row=2, column=0, sticky='w', pady=3)
    diamond_fields['count'] = ttk.Entry(diamond_frame, width=13)
    diamond_fields['count'].insert(0, "0")
    diamond_fields['count'].grid(row=2, column=1, pady=3, padx=5)
    
    ttk.Label(diamond_frame, text="Certification:").grid(row=2, column=2, sticky='w', pady=3, padx=10)
    diamond_fields['certification'] = ttk.Combobox(diamond_frame, values=['GIA', 'IGI', 'AGS', 'HRD', 'Other', 'None'], width=8)
    diamond_fields['certification'].grid(row=2, column=3, pady=3)
    
    other_frame = ttk.LabelFrame(form_frame, text="Other Details", padding=10)
    other_frame.grid(row=row+3, column=0, columnspan=2, sticky='ew', pady=10)
    
    ttk.Label(other_frame, text="Barcode:").grid(row=0, column=0, sticky='w', pady=3)
    fields['barcode'] = ttk.Entry(other_frame, width=20)
    fields['barcode'].grid(row=0, column=1, pady=3, padx=5)
    
    ttk.Label(other_frame, text="HSN Code:").grid(row=0, column=2, sticky='w', pady=3, padx=10)
    fields['hsn_code'] = ttk.Entry(other_frame, width=15)
    fields['hsn_code'].grid(row=0, column=3, pady=3)
    
    ttk.Label(other_frame, text="Stone Weight:").grid(row=1, column=0, sticky='w', pady=3)
    fields['stone_weight'] = ttk.Entry(other_frame, width=20)
    fields['stone_weight'].insert(0, "0")
    fields['stone_weight'].grid(row=1, column=1, pady=3, padx=5)
    
    ttk.Label(other_frame, text="Stone Type:").grid(row=1, column=2, sticky='w', pady=3, padx=10)
    fields['stone_type'] = ttk.Combobox(other_frame, values=['Ruby', 'Emerald', 'Sapphire', 'Pearl', 'Coral', 'Other'], width=13)
    fields['stone_type'].grid(row=1, column=3, pady=3)
    
    desc_frame = ttk.Frame(form_frame)
    desc_frame.grid(row=row+4, column=0, columnspan=2, sticky='ew', pady=10)
    
    ttk.Label(desc_frame, text="Description:").pack(anchor='w')
    fields['description'] = tk.Text(desc_frame, width=50, height=3)
    fields['description'].pack(fill=tk.X, pady=5)
    
    def save_item():
        name = fields['name'].get().strip()
        price_str = fields['price'].get().strip()
        material_name = fields['material'].get()
        
        if not name:
            messagebox.showwarning("Validation", "Item name is required!")
            return
        if not price_str:
            messagebox.showwarning("Validation", "Price is required!")
            return
        if not material_name:
            messagebox.showwarning("Validation", "Material type is required!")
            return
        
        try:
            price = float(price_str)
            cost_price = float(fields['cost_price'].get() or 0)
            quantity = int(fields['quantity'].get() or 0)
            weight = float(fields['weight'].get() or 0)
            gold_weight = float(gold_fields['gold_weight'].get() or 0)
            making_charges = float(gold_fields['making_charges'].get() or 0)
            diamond_carat = float(diamond_fields['carat'].get() or 0)
            diamond_count = int(diamond_fields['count'].get() or 0)
            stone_weight = float(fields['stone_weight'].get() or 0)
        except ValueError:
            messagebox.showerror("Error", "Invalid number format!")
            return
        
        category_name = fields['category'].get()
        category_id = categories.get(category_name) if category_name else None
        material_id = materials.get(material_name)
        
        try:
            execute_query("""
                INSERT INTO items (name, category_id, material_id, item_type, price, cost_price, 
                                   quantity, weight_in_gm, purity, making_charges, making_charges_type,
                                   gold_weight, diamond_weight, diamond_count, diamond_clarity, 
                                   diamond_color, diamond_cut, diamond_carat, diamond_certification,
                                   stone_weight, stone_type, hallmark, hsn_code, barcode, description,
                                   date_created, date_modified)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                name, category_id, material_id, 'finished', price, cost_price,
                quantity, weight, gold_fields['purity'].get() or None, making_charges, 'per_gram',
                gold_weight, diamond_carat, diamond_count, diamond_fields['clarity'].get() or None,
                diamond_fields['color'].get() or None, diamond_fields['cut'].get() or None, 
                diamond_carat, diamond_fields['certification'].get() or None,
                stone_weight, fields['stone_type'].get() or None, 
                gold_fields['hallmark'].get() or None, fields['hsn_code'].get() or None,
                fields['barcode'].get() or None,
                fields['description'].get("1.0", tk.END).strip() or None,
                datetime.now(), datetime.now()
            ))
            messagebox.showinfo("Success", "Item added successfully!")
            dialog.destroy()
            if items_tree:
                refresh_items_list(items_tree)
        except Exception as e:
            messagebox.showerror("Error", f"Error adding item: {str(e)}")
    
    btn_frame = ttk.Frame(main_frame)
    btn_frame.pack(pady=20)
    
    ttk.Button(btn_frame, text="Save Item", command=save_item, width=15).pack(side=tk.LEFT, padx=10)
    ttk.Button(btn_frame, text="Cancel", command=dialog.destroy, width=15).pack(side=tk.LEFT, padx=10)

def show_edit_item_dialog(parent, tree):
    selected = tree.selection()
    if not selected:
        messagebox.showwarning("Warning", "Please select an item to edit!")
        return
    
    item_id = tree.item(selected[0])['values'][0]
    
    item = fetch_one("""
        SELECT i.*, m.name as material_name, ic.name as category_name
        FROM items i
        LEFT JOIN materials m ON i.material_id = m.id
        LEFT JOIN item_categories ic ON i.category_id = ic.id
        WHERE i.id = ?
    """, (item_id,))
    
    if not item:
        messagebox.showerror("Error", "Item not found!")
        return
    
    dialog = tk.Toplevel(parent)
    dialog.title("Edit Item")
    dialog.geometry("550x700")
    dialog.transient(parent)
    dialog.grab_set()
    
    main_frame = ttk.Frame(dialog, padding=20)
    main_frame.pack(fill=tk.BOTH, expand=True)
    
    ttk.Label(main_frame, text="Edit Item", font=("Segoe UI", 14, "bold")).pack(pady=10)
    
    form_frame = ttk.Frame(main_frame)
    form_frame.pack(fill=tk.X)
    
    fields = {}
    materials = get_materials()
    categories = get_categories()
    
    row = 0
    ttk.Label(form_frame, text="Material Type:").grid(row=row, column=0, sticky='w', pady=5)
    fields['material'] = ttk.Combobox(form_frame, values=list(materials.keys()), width=32)
    if item['material_name']:
        fields['material'].set(item['material_name'])
    fields['material'].grid(row=row, column=1, pady=5, padx=5)
    
    row += 1
    ttk.Label(form_frame, text="Item Name *:").grid(row=row, column=0, sticky='w', pady=5)
    fields['name'] = ttk.Entry(form_frame, width=35)
    fields['name'].insert(0, item['name'] or "")
    fields['name'].grid(row=row, column=1, pady=5, padx=5)
    
    row += 1
    ttk.Label(form_frame, text="Category:").grid(row=row, column=0, sticky='w', pady=5)
    fields['category'] = ttk.Combobox(form_frame, values=list(categories.keys()), width=32)
    if item['category_name']:
        fields['category'].set(item['category_name'])
    fields['category'].grid(row=row, column=1, pady=5, padx=5)
    
    row += 1
    ttk.Label(form_frame, text="Price (₹) *:").grid(row=row, column=0, sticky='w', pady=5)
    fields['price'] = ttk.Entry(form_frame, width=35)
    fields['price'].insert(0, str(item['price']) if item['price'] else "0")
    fields['price'].grid(row=row, column=1, pady=5, padx=5)
    
    row += 1
    ttk.Label(form_frame, text="Cost Price (₹):").grid(row=row, column=0, sticky='w', pady=5)
    fields['cost_price'] = ttk.Entry(form_frame, width=35)
    fields['cost_price'].insert(0, str(item['cost_price']) if item['cost_price'] else "0")
    fields['cost_price'].grid(row=row, column=1, pady=5, padx=5)
    
    row += 1
    ttk.Label(form_frame, text="Quantity:").grid(row=row, column=0, sticky='w', pady=5)
    fields['quantity'] = ttk.Entry(form_frame, width=35)
    fields['quantity'].insert(0, str(item['quantity']) if item['quantity'] else "0")
    fields['quantity'].grid(row=row, column=1, pady=5, padx=5)
    
    row += 1
    ttk.Label(form_frame, text="Gross Weight (gm):").grid(row=row, column=0, sticky='w', pady=5)
    fields['weight'] = ttk.Entry(form_frame, width=35)
    fields['weight'].insert(0, str(item['weight_in_gm']) if item['weight_in_gm'] else "0")
    fields['weight'].grid(row=row, column=1, pady=5, padx=5)
    
    row += 1
    ttk.Label(form_frame, text="Purity:").grid(row=row, column=0, sticky='w', pady=5)
    fields['purity'] = ttk.Combobox(form_frame, values=['24K', '22K', '21K', '18K', '14K', '916', '875', '750', '585'], width=32)
    if item['purity']:
        fields['purity'].set(item['purity'])
    fields['purity'].grid(row=row, column=1, pady=5, padx=5)
    
    row += 1
    ttk.Label(form_frame, text="Barcode:").grid(row=row, column=0, sticky='w', pady=5)
    fields['barcode'] = ttk.Entry(form_frame, width=35)
    fields['barcode'].insert(0, item['barcode'] or "")
    fields['barcode'].grid(row=row, column=1, pady=5, padx=5)
    
    row += 1
    ttk.Label(form_frame, text="Description:").grid(row=row, column=0, sticky='w', pady=5)
    fields['description'] = tk.Text(form_frame, width=26, height=3)
    if item['description']:
        fields['description'].insert("1.0", item['description'])
    fields['description'].grid(row=row, column=1, pady=5, padx=5)
    
    def update_item():
        name = fields['name'].get().strip()
        price_str = fields['price'].get().strip()
        
        if not name:
            messagebox.showwarning("Validation", "Item name is required!")
            return
        if not price_str:
            messagebox.showwarning("Validation", "Price is required!")
            return
        
        try:
            price = float(price_str)
            cost_price = float(fields['cost_price'].get() or 0)
            quantity = int(fields['quantity'].get() or 0)
            weight = float(fields['weight'].get() or 0)
        except ValueError:
            messagebox.showerror("Error", "Invalid number format!")
            return
        
        category_name = fields['category'].get()
        category_id = categories.get(category_name) if category_name else None
        material_name = fields['material'].get()
        material_id = materials.get(material_name) if material_name else None
        
        try:
            execute_query("""
                UPDATE items 
                SET name = ?, category_id = ?, material_id = ?, price = ?, cost_price = ?, 
                    quantity = ?, weight_in_gm = ?, purity = ?, barcode = ?, description = ?, 
                    date_modified = ?
                WHERE id = ?
            """, (
                name, category_id, material_id, price, cost_price, quantity, weight,
                fields['purity'].get() or None,
                fields['barcode'].get() or None,
                fields['description'].get("1.0", tk.END).strip() or None,
                datetime.now(), item_id
            ))
            messagebox.showinfo("Success", "Item updated successfully!")
            dialog.destroy()
            refresh_items_list(tree)
        except Exception as e:
            messagebox.showerror("Error", f"Error updating item: {str(e)}")
    
    btn_frame = ttk.Frame(main_frame)
    btn_frame.pack(pady=20)
    
    ttk.Button(btn_frame, text="Update", command=update_item, width=15).pack(side=tk.LEFT, padx=10)
    ttk.Button(btn_frame, text="Cancel", command=dialog.destroy, width=15).pack(side=tk.LEFT, padx=10)

def show_stock_adjustment_dialog(parent, tree):
    selected = tree.selection()
    if not selected:
        messagebox.showwarning("Warning", "Please select an item to adjust stock!")
        return
    
    item_id = tree.item(selected[0])['values'][0]
    item_name = tree.item(selected[0])['values'][1]
    current_stock = tree.item(selected[0])['values'][5]
    current_weight = tree.item(selected[0])['values'][6]
    
    dialog = tk.Toplevel(parent)
    dialog.title("Adjust Stock")
    dialog.geometry("400x350")
    dialog.transient(parent)
    dialog.grab_set()
    
    main_frame = ttk.Frame(dialog, padding=20)
    main_frame.pack(fill=tk.BOTH, expand=True)
    
    ttk.Label(main_frame, text="Stock Adjustment", font=("Segoe UI", 14, "bold")).pack(pady=10)
    ttk.Label(main_frame, text=f"Item: {item_name}", font=("Segoe UI", 11)).pack(pady=5)
    
    form_frame = ttk.Frame(main_frame)
    form_frame.pack(fill=tk.X, pady=10)
    
    ttk.Label(form_frame, text=f"Current Stock: {current_stock}").grid(row=0, column=0, columnspan=2, sticky='w', pady=5)
    ttk.Label(form_frame, text=f"Current Weight: {current_weight} gm").grid(row=1, column=0, columnspan=2, sticky='w', pady=5)
    
    ttk.Label(form_frame, text="New Quantity:").grid(row=2, column=0, sticky='w', pady=10)
    new_qty_entry = ttk.Entry(form_frame, width=15)
    new_qty_entry.insert(0, str(current_stock))
    new_qty_entry.grid(row=2, column=1, pady=10, padx=5)
    
    ttk.Label(form_frame, text="New Weight (gm):").grid(row=3, column=0, sticky='w', pady=10)
    new_weight_entry = ttk.Entry(form_frame, width=15)
    weight_val = str(current_weight).replace(' gm', '').replace('gm', '').strip()
    new_weight_entry.insert(0, weight_val)
    new_weight_entry.grid(row=3, column=1, pady=10, padx=5)
    
    ttk.Label(form_frame, text="Reason *:").grid(row=4, column=0, sticky='w', pady=10)
    reason_combo = ttk.Combobox(form_frame, values=[
        'Physical Count Correction',
        'Damage/Loss',
        'Found Extra Stock',
        'Data Entry Error',
        'Return from Customer',
        'Other'
    ], width=25)
    reason_combo.grid(row=4, column=1, pady=10, padx=5)
    
    ttk.Label(form_frame, text="Notes:").grid(row=5, column=0, sticky='w', pady=5)
    notes_entry = ttk.Entry(form_frame, width=30)
    notes_entry.grid(row=5, column=1, pady=5, padx=5)
    
    def adjust_stock():
        reason = reason_combo.get()
        if not reason:
            messagebox.showwarning("Validation", "Please select a reason for adjustment!")
            return
        
        try:
            new_qty = int(new_qty_entry.get())
            new_weight = float(new_weight_entry.get())
        except ValueError:
            messagebox.showerror("Error", "Invalid quantity or weight!")
            return
        
        if new_qty < 0:
            messagebox.showerror("Error", "Quantity cannot be negative!")
            return
        
        notes = notes_entry.get() or ""
        full_reason = f"{reason}: {notes}" if notes else reason
        
        try:
            StockService.adjust_stock(item_id, new_qty, new_weight, full_reason, "Admin")
            messagebox.showinfo("Success", f"Stock adjusted successfully!\n\nNew Quantity: {new_qty}\nNew Weight: {new_weight} gm")
            dialog.destroy()
            refresh_items_list(tree)
        except Exception as e:
            messagebox.showerror("Error", f"Error adjusting stock: {str(e)}")
    
    btn_frame = ttk.Frame(main_frame)
    btn_frame.pack(pady=20)
    
    ttk.Button(btn_frame, text="Adjust Stock", command=adjust_stock, width=15).pack(side=tk.LEFT, padx=10)
    ttk.Button(btn_frame, text="Cancel", command=dialog.destroy, width=15).pack(side=tk.LEFT, padx=10)

def view_stock_history(tree):
    selected = tree.selection()
    if not selected:
        messagebox.showwarning("Warning", "Please select an item to view history!")
        return
    
    item_id = tree.item(selected[0])['values'][0]
    item_name = tree.item(selected[0])['values'][1]
    
    movements = StockService.get_stock_movements(item_id, limit=50)
    
    if not movements:
        messagebox.showinfo("Stock History", f"No stock movements found for {item_name}")
        return
    
    dialog = tk.Toplevel()
    dialog.title(f"Stock History - {item_name}")
    dialog.geometry("800x400")
    
    columns = ('ID', 'Type', 'Qty Change', 'Weight Change', 'Prev Qty', 'New Qty', 'Reason', 'By', 'Date')
    hist_tree = ttk.Treeview(dialog, columns=columns, height=15, show='headings')
    
    col_widths = {'ID': 40, 'Type': 80, 'Qty Change': 80, 'Weight Change': 80, 
                  'Prev Qty': 70, 'New Qty': 70, 'Reason': 150, 'By': 80, 'Date': 120}
    
    for col in columns:
        hist_tree.heading(col, text=col)
        hist_tree.column(col, width=col_widths.get(col, 80))
    
    for mov in movements:
        hist_tree.insert('', 'end', values=(
            mov[0], mov[2], mov[3], mov[4], mov[5], mov[6], mov[7] or "N/A", mov[8] or "System", 
            str(mov[9])[:19] if mov[9] else "N/A"
        ))
    
    hist_tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    ttk.Button(dialog, text="Close", command=dialog.destroy).pack(pady=10)

def delete_item(tree):
    selected = tree.selection()
    if not selected:
        messagebox.showwarning("Warning", "Please select an item to delete!")
        return
    
    item_id = tree.item(selected[0])['values'][0]
    item_name = tree.item(selected[0])['values'][1]
    
    if messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete '{item_name}'?\n\nThis will mark the item as inactive."):
        try:
            execute_query("""
                UPDATE items SET is_active = 0, date_modified = ? WHERE id = ?
            """, (datetime.now(), item_id))
            messagebox.showinfo("Success", "Item deleted successfully!")
            refresh_items_list(tree)
        except Exception as e:
            messagebox.showerror("Error", f"Error deleting item: {str(e)}")

def view_item_details(tree):
    selected = tree.selection()
    if not selected:
        messagebox.showwarning("Warning", "Please select an item to view!")
        return
    
    item_id = tree.item(selected[0])['values'][0]
    
    item = fetch_one("""
        SELECT i.*, m.name as material_name, ic.name as category_name
        FROM items i
        LEFT JOIN materials m ON i.material_id = m.id
        LEFT JOIN item_categories ic ON i.category_id = ic.id
        WHERE i.id = ?
    """, (item_id,))
    
    if not item:
        messagebox.showerror("Error", "Item not found!")
        return
    
    details = f"""
ITEM DETAILS
{'='*45}

Name: {item['name']}
Material: {item['material_name'] or 'N/A'}
Category: {item['category_name'] or 'N/A'}
Barcode: {item['barcode'] or 'N/A'}

PRICING
Selling Price: {item['price']:,.2f}
Cost Price: {item['cost_price']:,.2f} if {item['cost_price']} else 'N/A'
Making Charges: {item['making_charges']:,.2f}/gm if {item['making_charges']} else 'N/A'

STOCK
Quantity: {item['quantity']}
Gross Weight: {item['weight_in_gm']:.3f} gm
Gold Weight: {item['gold_weight']:.3f} gm if {item['gold_weight']} else 'N/A'
Purity: {item['purity'] or 'N/A'}
Hallmark: {item['hallmark'] or 'N/A'}

DIAMOND DETAILS
Carat: {item['diamond_carat']} ct if {item['diamond_carat']} else 'N/A'
Clarity: {item['diamond_clarity'] or 'N/A'}
Color: {item['diamond_color'] or 'N/A'}
Cut: {item['diamond_cut'] or 'N/A'}
Count: {item['diamond_count'] or 'N/A'}
Certification: {item['diamond_certification'] or 'N/A'}

Description: {item['description'] or 'N/A'}
    """
    
    messagebox.showinfo("Item Details", details)
