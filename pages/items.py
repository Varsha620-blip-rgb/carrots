import tkinter as tk
from tkinter import messagebox, ttk
from database.db import execute_query, fetch_query, fetch_one
from datetime import datetime

def items_page(parent):
    for widget in parent.winfo_children():
        widget.destroy()
    
    frame = ttk.Frame(parent)
    frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    
    # Title
    title_label = ttk.Label(frame, text="Item Management", font=("Segoe UI", 16, "bold"))
    title_label.pack(pady=10)
    
    # Button frame
    button_frame = ttk.Frame(frame)
    button_frame.pack(fill=tk.X, pady=10)
    
    ttk.Button(button_frame, text="Add Item", command=lambda: show_add_item_dialog(parent)).pack(side=tk.LEFT, padx=5)
    ttk.Button(button_frame, text="Edit Item", command=lambda: show_edit_item_dialog(parent)).pack(side=tk.LEFT, padx=5)
    ttk.Button(button_frame, text="Delete Item", command=lambda: delete_item_dialog(parent)).pack(side=tk.LEFT, padx=5)
    ttk.Button(button_frame, text="Refresh", command=lambda: refresh_items_list(tree)).pack(side=tk.LEFT, padx=5)
    
    # Treeview for items
    columns = ('ID', 'Name', 'Category', 'Price', 'Stock', 'Weight(gm)', 'Purity')
    tree = ttk.Treeview(frame, columns=columns, height=15)
    
    for col in columns:
        tree.column(col, width=120)
        tree.heading(col, text=col)
    
    tree.pack(fill=tk.BOTH, expand=True)
    
    # Scrollbar
    scrollbar = ttk.Scrollbar(frame, orient=tk.VERTICAL, command=tree.yview)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    tree.config(yscroll=scrollbar.set)
    
    refresh_items_list(tree)

def refresh_items_list(tree):
    for item in tree.get_children():
        tree.delete(item)
    
    items = fetch_query("""
        SELECT i.id, i.name, ic.name, i.price, i.quantity, i.weight_in_gm, i.purity
        FROM items i
        LEFT JOIN item_categories ic ON i.category_id = ic.id
        WHERE i.is_active = 1
    """)
    
    for item in items:
        tree.insert('', 'end', values=item)

def show_add_item_dialog(parent):
    dialog = tk.Toplevel(parent)
    dialog.title("Add New Item")
    dialog.geometry("400x500")
    
    fields = {}
    
    ttk.Label(dialog, text="Item Name:").pack(pady=5)
    fields['name'] = ttk.Entry(dialog, width=40)
    fields['name'].pack(pady=5)
    
    ttk.Label(dialog, text="Category:").pack(pady=5)
    fields['category'] = ttk.Entry(dialog, width=40)
    fields['category'].pack(pady=5)
    
    ttk.Label(dialog, text="Price:").pack(pady=5)
    fields['price'] = ttk.Entry(dialog, width=40)
    fields['price'].pack(pady=5)
    
    ttk.Label(dialog, text="Cost Price:").pack(pady=5)
    fields['cost_price'] = ttk.Entry(dialog, width=40)
    fields['cost_price'].pack(pady=5)
    
    ttk.Label(dialog, text="Quantity:").pack(pady=5)
    fields['quantity'] = ttk.Entry(dialog, width=40)
    fields['quantity'].pack(pady=5)
    
    ttk.Label(dialog, text="Weight (gm):").pack(pady=5)
    fields['weight'] = ttk.Entry(dialog, width=40)
    fields['weight'].pack(pady=5)
    
    ttk.Label(dialog, text="Purity:").pack(pady=5)
    fields['purity'] = ttk.Entry(dialog, width=40)
    fields['purity'].pack(pady=5)
    
    ttk.Label(dialog, text="Barcode:").pack(pady=5)
    fields['barcode'] = ttk.Entry(dialog, width=40)
    fields['barcode'].pack(pady=5)
    
    def save_item():
        try:
            execute_query("""
                INSERT INTO items (name, price, cost_price, quantity, weight_in_gm, purity, barcode, date_created, date_modified)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                fields['name'].get(),
                float(fields['price'].get()),
                float(fields['cost_price'].get()),
                int(fields['quantity'].get()),
                float(fields['weight'].get()),
                fields['purity'].get(),
                fields['barcode'].get(),
                datetime.now(),
                datetime.now()
            ))
            messagebox.showinfo("Success", "Item added successfully!")
            dialog.destroy()
        except Exception as e:
            messagebox.showerror("Error", f"Error adding item: {str(e)}")
    
    ttk.Button(dialog, text="Save", command=save_item).pack(pady=20)

def show_edit_item_dialog(parent):
    messagebox.showinfo("Edit Item", "Select item from list and click Edit")

def delete_item_dialog(parent):
    messagebox.showinfo("Delete Item", "Select item from list and confirm deletion")