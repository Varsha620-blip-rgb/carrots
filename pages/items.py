import tkinter as tk
from tkinter import messagebox, ttk
from database.db import execute_query, fetch_query, fetch_one
from datetime import datetime

items_tree = None

def items_page(parent):
    global items_tree
    
    for widget in parent.winfo_children():
        widget.destroy()
    
    frame = ttk.Frame(parent)
    frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    
    title_frame = ttk.Frame(frame)
    title_frame.pack(fill=tk.X, pady=10)
    
    title_label = ttk.Label(title_frame, text="Item Management", font=("Segoe UI", 16, "bold"))
    title_label.pack(side=tk.LEFT)
    
    search_frame = ttk.Frame(frame)
    search_frame.pack(fill=tk.X, pady=5)
    
    ttk.Label(search_frame, text="Search:").pack(side=tk.LEFT, padx=5)
    search_var = tk.StringVar()
    search_entry = ttk.Entry(search_frame, textvariable=search_var, width=30)
    search_entry.pack(side=tk.LEFT, padx=5)
    
    def search_items():
        search_term = search_var.get()
        refresh_items_list(items_tree, search_term)
    
    ttk.Button(search_frame, text="Search", command=search_items).pack(side=tk.LEFT, padx=5)
    ttk.Button(search_frame, text="Clear", command=lambda: [search_var.set(""), refresh_items_list(items_tree)]).pack(side=tk.LEFT, padx=5)
    
    button_frame = ttk.Frame(frame)
    button_frame.pack(fill=tk.X, pady=10)
    
    ttk.Button(button_frame, text="Add Item", command=lambda: show_add_item_dialog(parent)).pack(side=tk.LEFT, padx=5)
    ttk.Button(button_frame, text="Edit Item", command=lambda: show_edit_item_dialog(parent, items_tree)).pack(side=tk.LEFT, padx=5)
    ttk.Button(button_frame, text="Delete Item", command=lambda: delete_item(items_tree)).pack(side=tk.LEFT, padx=5)
    ttk.Button(button_frame, text="View Details", command=lambda: view_item_details(items_tree)).pack(side=tk.LEFT, padx=5)
    ttk.Button(button_frame, text="Refresh", command=lambda: refresh_items_list(items_tree)).pack(side=tk.LEFT, padx=5)
    
    tree_frame = ttk.Frame(frame)
    tree_frame.pack(fill=tk.BOTH, expand=True)
    
    columns = ('ID', 'Name', 'Category', 'Price', 'Cost Price', 'Stock', 'Weight(gm)', 'Purity', 'Barcode')
    items_tree = ttk.Treeview(tree_frame, columns=columns, height=15, show='headings')
    
    col_widths = {'ID': 50, 'Name': 150, 'Category': 100, 'Price': 100, 'Cost Price': 100, 
                  'Stock': 60, 'Weight(gm)': 80, 'Purity': 60, 'Barcode': 100}
    
    for col in columns:
        items_tree.column(col, width=col_widths.get(col, 100), anchor='center')
        items_tree.heading(col, text=col, command=lambda c=col: sort_column(items_tree, c, False))
    
    scrollbar_y = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=items_tree.yview)
    scrollbar_x = ttk.Scrollbar(tree_frame, orient=tk.HORIZONTAL, command=items_tree.xview)
    items_tree.configure(yscroll=scrollbar_y.set, xscroll=scrollbar_x.set)
    
    items_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y)
    
    items_tree.bind('<Double-1>', lambda e: view_item_details(items_tree))
    
    refresh_items_list(items_tree)
    
    status_frame = ttk.Frame(frame)
    status_frame.pack(fill=tk.X, pady=5)
    
    item_count = fetch_query("SELECT COUNT(*) FROM items WHERE is_active = 1")[0][0]
    ttk.Label(status_frame, text=f"Total Active Items: {item_count}").pack(side=tk.LEFT)

def sort_column(tree, col, reverse):
    items = [(tree.set(k, col), k) for k in tree.get_children('')]
    try:
        items.sort(key=lambda t: float(t[0]) if t[0].replace('.','',1).isdigit() else t[0], reverse=reverse)
    except:
        items.sort(reverse=reverse)
    
    for index, (val, k) in enumerate(items):
        tree.move(k, '', index)
    
    tree.heading(col, command=lambda: sort_column(tree, col, not reverse))

def refresh_items_list(tree, search_term=""):
    if tree is None:
        return
        
    for item in tree.get_children():
        tree.delete(item)
    
    if search_term:
        query = """
            SELECT i.id, i.name, COALESCE(ic.name, 'N/A'), i.price, i.cost_price, 
                   i.quantity, i.weight_in_gm, i.purity, i.barcode
            FROM items i
            LEFT JOIN item_categories ic ON i.category_id = ic.id
            WHERE i.is_active = 1 AND (i.name LIKE ? OR i.barcode LIKE ? OR ic.name LIKE ?)
            ORDER BY i.name
        """
        search_pattern = f"%{search_term}%"
        items = fetch_query(query, (search_pattern, search_pattern, search_pattern))
    else:
        items = fetch_query("""
            SELECT i.id, i.name, COALESCE(ic.name, 'N/A'), i.price, i.cost_price, 
                   i.quantity, i.weight_in_gm, i.purity, i.barcode
            FROM items i
            LEFT JOIN item_categories ic ON i.category_id = ic.id
            WHERE i.is_active = 1
            ORDER BY i.name
        """)
    
    for item in items:
        formatted_item = (
            item[0], item[1], item[2],
            f"₹{item[3]:,.2f}" if item[3] else "₹0.00",
            f"₹{item[4]:,.2f}" if item[4] else "₹0.00",
            item[5], item[6], item[7] or "N/A", item[8] or "N/A"
        )
        tree.insert('', 'end', values=formatted_item)

def get_categories():
    categories = fetch_query("SELECT id, name FROM item_categories ORDER BY name")
    return {cat[1]: cat[0] for cat in categories}

def show_add_item_dialog(parent):
    dialog = tk.Toplevel(parent)
    dialog.title("Add New Item")
    dialog.geometry("450x600")
    dialog.transient(parent)
    dialog.grab_set()
    
    main_frame = ttk.Frame(dialog, padding=20)
    main_frame.pack(fill=tk.BOTH, expand=True)
    
    ttk.Label(main_frame, text="Add New Item", font=("Segoe UI", 14, "bold")).pack(pady=10)
    
    form_frame = ttk.Frame(main_frame)
    form_frame.pack(fill=tk.X)
    
    fields = {}
    
    row = 0
    ttk.Label(form_frame, text="Item Name *:").grid(row=row, column=0, sticky='w', pady=5)
    fields['name'] = ttk.Entry(form_frame, width=35)
    fields['name'].grid(row=row, column=1, pady=5, padx=5)
    
    row += 1
    ttk.Label(form_frame, text="Category:").grid(row=row, column=0, sticky='w', pady=5)
    categories = get_categories()
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
    fields['quantity'].insert(0, "0")
    fields['quantity'].grid(row=row, column=1, pady=5, padx=5)
    
    row += 1
    ttk.Label(form_frame, text="Weight (gm):").grid(row=row, column=0, sticky='w', pady=5)
    fields['weight'] = ttk.Entry(form_frame, width=35)
    fields['weight'].insert(0, "0")
    fields['weight'].grid(row=row, column=1, pady=5, padx=5)
    
    row += 1
    ttk.Label(form_frame, text="Purity:").grid(row=row, column=0, sticky='w', pady=5)
    fields['purity'] = ttk.Combobox(form_frame, values=['24K', '22K', '18K', '14K', '916', '750', '585'], width=32)
    fields['purity'].grid(row=row, column=1, pady=5, padx=5)
    
    row += 1
    ttk.Label(form_frame, text="Barcode:").grid(row=row, column=0, sticky='w', pady=5)
    fields['barcode'] = ttk.Entry(form_frame, width=35)
    fields['barcode'].grid(row=row, column=1, pady=5, padx=5)
    
    row += 1
    ttk.Label(form_frame, text="Description:").grid(row=row, column=0, sticky='w', pady=5)
    fields['description'] = tk.Text(form_frame, width=26, height=3)
    fields['description'].grid(row=row, column=1, pady=5, padx=5)
    
    def save_item():
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
        
        try:
            execute_query("""
                INSERT INTO items (name, category_id, price, cost_price, quantity, weight_in_gm, 
                                   purity, barcode, description, date_created, date_modified)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                name, category_id, price, cost_price, quantity, weight,
                fields['purity'].get() or None,
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
    
    ttk.Button(btn_frame, text="Save", command=save_item, width=15).pack(side=tk.LEFT, padx=10)
    ttk.Button(btn_frame, text="Cancel", command=dialog.destroy, width=15).pack(side=tk.LEFT, padx=10)

def show_edit_item_dialog(parent, tree):
    selected = tree.selection()
    if not selected:
        messagebox.showwarning("Warning", "Please select an item to edit!")
        return
    
    item_id = tree.item(selected[0])['values'][0]
    
    item = fetch_one("""
        SELECT id, name, category_id, price, cost_price, quantity, weight_in_gm, 
               purity, barcode, description
        FROM items WHERE id = ?
    """, (item_id,))
    
    if not item:
        messagebox.showerror("Error", "Item not found!")
        return
    
    dialog = tk.Toplevel(parent)
    dialog.title("Edit Item")
    dialog.geometry("450x600")
    dialog.transient(parent)
    dialog.grab_set()
    
    main_frame = ttk.Frame(dialog, padding=20)
    main_frame.pack(fill=tk.BOTH, expand=True)
    
    ttk.Label(main_frame, text="Edit Item", font=("Segoe UI", 14, "bold")).pack(pady=10)
    
    form_frame = ttk.Frame(main_frame)
    form_frame.pack(fill=tk.X)
    
    fields = {}
    categories = get_categories()
    category_id_to_name = {v: k for k, v in categories.items()}
    
    row = 0
    ttk.Label(form_frame, text="Item Name *:").grid(row=row, column=0, sticky='w', pady=5)
    fields['name'] = ttk.Entry(form_frame, width=35)
    fields['name'].insert(0, item[1] or "")
    fields['name'].grid(row=row, column=1, pady=5, padx=5)
    
    row += 1
    ttk.Label(form_frame, text="Category:").grid(row=row, column=0, sticky='w', pady=5)
    fields['category'] = ttk.Combobox(form_frame, values=list(categories.keys()), width=32)
    if item[2] and item[2] in category_id_to_name:
        fields['category'].set(category_id_to_name[item[2]])
    fields['category'].grid(row=row, column=1, pady=5, padx=5)
    
    row += 1
    ttk.Label(form_frame, text="Price (₹) *:").grid(row=row, column=0, sticky='w', pady=5)
    fields['price'] = ttk.Entry(form_frame, width=35)
    fields['price'].insert(0, str(item[3]) if item[3] else "0")
    fields['price'].grid(row=row, column=1, pady=5, padx=5)
    
    row += 1
    ttk.Label(form_frame, text="Cost Price (₹):").grid(row=row, column=0, sticky='w', pady=5)
    fields['cost_price'] = ttk.Entry(form_frame, width=35)
    fields['cost_price'].insert(0, str(item[4]) if item[4] else "0")
    fields['cost_price'].grid(row=row, column=1, pady=5, padx=5)
    
    row += 1
    ttk.Label(form_frame, text="Quantity:").grid(row=row, column=0, sticky='w', pady=5)
    fields['quantity'] = ttk.Entry(form_frame, width=35)
    fields['quantity'].insert(0, str(item[5]) if item[5] else "0")
    fields['quantity'].grid(row=row, column=1, pady=5, padx=5)
    
    row += 1
    ttk.Label(form_frame, text="Weight (gm):").grid(row=row, column=0, sticky='w', pady=5)
    fields['weight'] = ttk.Entry(form_frame, width=35)
    fields['weight'].insert(0, str(item[6]) if item[6] else "0")
    fields['weight'].grid(row=row, column=1, pady=5, padx=5)
    
    row += 1
    ttk.Label(form_frame, text="Purity:").grid(row=row, column=0, sticky='w', pady=5)
    fields['purity'] = ttk.Combobox(form_frame, values=['24K', '22K', '18K', '14K', '916', '750', '585'], width=32)
    if item[7]:
        fields['purity'].set(item[7])
    fields['purity'].grid(row=row, column=1, pady=5, padx=5)
    
    row += 1
    ttk.Label(form_frame, text="Barcode:").grid(row=row, column=0, sticky='w', pady=5)
    fields['barcode'] = ttk.Entry(form_frame, width=35)
    fields['barcode'].insert(0, item[8] or "")
    fields['barcode'].grid(row=row, column=1, pady=5, padx=5)
    
    row += 1
    ttk.Label(form_frame, text="Description:").grid(row=row, column=0, sticky='w', pady=5)
    fields['description'] = tk.Text(form_frame, width=26, height=3)
    if item[9]:
        fields['description'].insert("1.0", item[9])
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
        
        try:
            execute_query("""
                UPDATE items 
                SET name = ?, category_id = ?, price = ?, cost_price = ?, quantity = ?, 
                    weight_in_gm = ?, purity = ?, barcode = ?, description = ?, date_modified = ?
                WHERE id = ?
            """, (
                name, category_id, price, cost_price, quantity, weight,
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
        SELECT i.*, ic.name as category_name
        FROM items i
        LEFT JOIN item_categories ic ON i.category_id = ic.id
        WHERE i.id = ?
    """, (item_id,))
    
    if not item:
        messagebox.showerror("Error", "Item not found!")
        return
    
    details = f"""
ITEM DETAILS
{'='*40}

Name: {item[1]}
Category: {item['category_name'] or 'N/A'}
Barcode: {item[3] or 'N/A'}

PRICING
Price: ₹{item[4]:,.2f}
Cost Price: ₹{item[5]:,.2f} if item[5] else 'N/A'

STOCK
Quantity: {item[6]}
Weight: {item[7]} gm
Purity: {item[8] or 'N/A'}

Description: {item[9] or 'N/A'}

Created: {item[11]}
Modified: {item[12]}
    """
    
    messagebox.showinfo("Item Details", details)
