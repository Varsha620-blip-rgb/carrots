import tkinter as tk
from tkinter import messagebox, ttk, filedialog
from database.db import execute_query, fetch_query
from datetime import datetime
import pandas as pd
import os

def data_import_page(parent):
    for widget in parent.winfo_children():
        widget.destroy()
    
    frame = ttk.Frame(parent)
    frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    
    title_label = ttk.Label(frame, text="Data Import", font=("Segoe UI", 16, "bold"))
    title_label.pack(pady=10)
    
    info_frame = ttk.LabelFrame(frame, text="Import Instructions", padding=10)
    info_frame.pack(fill=tk.X, pady=10)
    
    info_text = """
This tool allows you to import data from your old software via CSV or Excel files.

Supported Imports:
1. Items - Import inventory items with name, price, quantity, weight, purity
2. Customers - Import customer records with contact details
3. Employees - Import employee records
4. Suppliers - Import supplier records

File Format:
- CSV (.csv) or Excel (.xlsx) files
- First row should contain column headers
- Use the template buttons below to download sample formats

Tips:
- Backup your database before importing
- Check data for duplicates
- Verify imported data after import
    """
    
    ttk.Label(info_frame, text=info_text, justify=tk.LEFT).pack(anchor='w')
    
    template_frame = ttk.LabelFrame(frame, text="Download Templates", padding=10)
    template_frame.pack(fill=tk.X, pady=10)
    
    template_row = ttk.Frame(template_frame)
    template_row.pack(fill=tk.X)
    
    ttk.Button(template_row, text="Items Template", command=lambda: create_template('items')).pack(side=tk.LEFT, padx=5)
    ttk.Button(template_row, text="Customers Template", command=lambda: create_template('customers')).pack(side=tk.LEFT, padx=5)
    ttk.Button(template_row, text="Employees Template", command=lambda: create_template('employees')).pack(side=tk.LEFT, padx=5)
    ttk.Button(template_row, text="Suppliers Template", command=lambda: create_template('suppliers')).pack(side=tk.LEFT, padx=5)
    
    import_frame = ttk.LabelFrame(frame, text="Import Data", padding=10)
    import_frame.pack(fill=tk.BOTH, expand=True, pady=10)
    
    type_row = ttk.Frame(import_frame)
    type_row.pack(fill=tk.X, pady=5)
    
    ttk.Label(type_row, text="Import Type:").pack(side=tk.LEFT, padx=5)
    import_type = ttk.Combobox(type_row, values=['Items', 'Customers', 'Employees', 'Suppliers'], width=15)
    import_type.set('Items')
    import_type.pack(side=tk.LEFT, padx=5)
    
    file_row = ttk.Frame(import_frame)
    file_row.pack(fill=tk.X, pady=5)
    
    ttk.Label(file_row, text="File:").pack(side=tk.LEFT, padx=5)
    file_path = tk.StringVar()
    file_entry = ttk.Entry(file_row, textvariable=file_path, width=50)
    file_entry.pack(side=tk.LEFT, padx=5)
    
    def browse_file():
        filename = filedialog.askopenfilename(
            title="Select Import File",
            filetypes=[("CSV files", "*.csv"), ("Excel files", "*.xlsx"), ("All files", "*.*")]
        )
        if filename:
            file_path.set(filename)
            preview_data()
    
    ttk.Button(file_row, text="Browse", command=browse_file).pack(side=tk.LEFT, padx=5)
    
    preview_frame = ttk.LabelFrame(import_frame, text="Preview (First 10 rows)", padding=10)
    preview_frame.pack(fill=tk.BOTH, expand=True, pady=10)
    
    preview_tree = ttk.Treeview(preview_frame, height=8)
    preview_tree.pack(fill=tk.BOTH, expand=True)
    
    preview_scroll = ttk.Scrollbar(preview_frame, orient=tk.HORIZONTAL, command=preview_tree.xview)
    preview_tree.configure(xscroll=preview_scroll.set)
    preview_scroll.pack(fill=tk.X)
    
    status_var = tk.StringVar(value="")
    status_label = ttk.Label(import_frame, textvariable=status_var, font=("Segoe UI", 10))
    status_label.pack(pady=5)
    
    imported_df = [None]
    
    def preview_data():
        filepath = file_path.get()
        if not filepath or not os.path.exists(filepath):
            return
        
        try:
            if filepath.endswith('.csv'):
                df = pd.read_csv(filepath)
            else:
                df = pd.read_excel(filepath)
            
            imported_df[0] = df
            
            for item in preview_tree.get_children():
                preview_tree.delete(item)
            
            preview_tree['columns'] = list(df.columns)
            preview_tree['show'] = 'headings'
            
            for col in df.columns:
                preview_tree.heading(col, text=col)
                preview_tree.column(col, width=100)
            
            for idx, row in df.head(10).iterrows():
                preview_tree.insert('', 'end', values=list(row))
            
            status_var.set(f"File loaded: {len(df)} rows, {len(df.columns)} columns")
        except Exception as e:
            messagebox.showerror("Error", f"Error reading file: {str(e)}")
    
    def do_import():
        df = imported_df[0]
        if df is None:
            messagebox.showwarning("Warning", "Please select a file first!")
            return
        
        itype = import_type.get().lower()
        
        if messagebox.askyesno("Confirm Import", f"Are you sure you want to import {len(df)} {itype} records?\n\nThis action cannot be undone easily."):
            try:
                if itype == 'items':
                    imported = import_items(df)
                elif itype == 'customers':
                    imported = import_customers(df)
                elif itype == 'employees':
                    imported = import_employees(df)
                elif itype == 'suppliers':
                    imported = import_suppliers(df)
                else:
                    messagebox.showerror("Error", "Invalid import type!")
                    return
                
                messagebox.showinfo("Success", f"Successfully imported {imported} records!")
                status_var.set(f"Import complete: {imported} records imported")
            except Exception as e:
                messagebox.showerror("Error", f"Import failed: {str(e)}")
    
    btn_frame = ttk.Frame(import_frame)
    btn_frame.pack(pady=10)
    
    ttk.Button(btn_frame, text="Import Data", command=do_import, width=20).pack(side=tk.LEFT, padx=10)
    ttk.Button(btn_frame, text="Clear", command=lambda: [file_path.set(""), preview_tree.delete(*preview_tree.get_children()), status_var.set("")]).pack(side=tk.LEFT, padx=10)

def create_template(template_type):
    templates = {
        'items': {
            'columns': ['name', 'category', 'price', 'cost_price', 'quantity', 'weight_in_gm', 'purity', 'barcode', 'description'],
            'sample': [['Gold Ring 22K', 'Rings', 25000, 22000, 5, 10.5, '22K', 'BR001', 'Sample gold ring']]
        },
        'customers': {
            'columns': ['name', 'phone', 'email', 'address', 'city', 'state', 'pincode', 'gst_number', 'credit_limit'],
            'sample': [['John Doe', '9876543210', 'john@email.com', '123 Main St', 'Mumbai', 'Maharashtra', '400001', 'GSTIN123', 50000]]
        },
        'employees': {
            'columns': ['name', 'position', 'phone', 'email', 'address', 'salary', 'date_joined'],
            'sample': [['Jane Smith', 'Sales Executive', '9876543211', 'jane@email.com', '456 Oak St', 25000, '2024-01-15']]
        },
        'suppliers': {
            'columns': ['name', 'phone', 'email', 'address', 'city', 'state', 'pincode', 'gst_number'],
            'sample': [['Gold Suppliers Ltd', '9876543212', 'supplier@email.com', '789 Gold St', 'Delhi', 'Delhi', '110001', 'GSTIN456']]
        }
    }
    
    try:
        template = templates[template_type]
        df = pd.DataFrame(template['sample'], columns=template['columns'])
        
        exports_dir = "exports"
        if not os.path.exists(exports_dir):
            os.makedirs(exports_dir)
        
        filepath = os.path.join(exports_dir, f"{template_type}_template.xlsx")
        df.to_excel(filepath, index=False)
        
        messagebox.showinfo("Template Created", f"Template saved to:\n{filepath}\n\nFill in your data and import it back.")
    except Exception as e:
        messagebox.showerror("Error", f"Error creating template: {str(e)}")

def import_items(df):
    imported = 0
    
    required_cols = ['name', 'price']
    for col in required_cols:
        if col not in df.columns:
            raise ValueError(f"Missing required column: {col}")
    
    for idx, row in df.iterrows():
        try:
            name = str(row.get('name', '')).strip()
            if not name:
                continue
            
            execute_query("""
                INSERT INTO items (name, price, cost_price, quantity, weight_in_gm, purity, barcode, description, is_active, date_created, date_modified)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, 1, ?, ?)
            """, (
                name,
                float(row.get('price', 0) or 0),
                float(row.get('cost_price', 0) or 0),
                int(row.get('quantity', 0) or 0),
                float(row.get('weight_in_gm', 0) or 0),
                str(row.get('purity', '')) or None,
                str(row.get('barcode', '')) or None,
                str(row.get('description', '')) or None,
                datetime.now(), datetime.now()
            ))
            imported += 1
        except Exception as e:
            print(f"Error importing row {idx}: {e}")
            continue
    
    return imported

def import_customers(df):
    imported = 0
    
    if 'name' not in df.columns:
        raise ValueError("Missing required column: name")
    
    for idx, row in df.iterrows():
        try:
            name = str(row.get('name', '')).strip()
            if not name:
                continue
            
            execute_query("""
                INSERT INTO customers (name, phone, email, address, city, state, pincode, gst_number, credit_limit, date_created, date_modified)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                name,
                str(row.get('phone', '')) or None,
                str(row.get('email', '')) or None,
                str(row.get('address', '')) or None,
                str(row.get('city', '')) or None,
                str(row.get('state', '')) or None,
                str(row.get('pincode', '')) or None,
                str(row.get('gst_number', '')) or None,
                float(row.get('credit_limit', 0) or 0),
                datetime.now(), datetime.now()
            ))
            imported += 1
        except Exception as e:
            print(f"Error importing row {idx}: {e}")
            continue
    
    return imported

def import_employees(df):
    imported = 0
    
    if 'name' not in df.columns:
        raise ValueError("Missing required column: name")
    
    for idx, row in df.iterrows():
        try:
            name = str(row.get('name', '')).strip()
            if not name:
                continue
            
            execute_query("""
                INSERT INTO employees (name, position, phone, email, address, salary, date_joined, status, date_created, date_modified)
                VALUES (?, ?, ?, ?, ?, ?, ?, 'Active', ?, ?)
            """, (
                name,
                str(row.get('position', '')) or None,
                str(row.get('phone', '')) or None,
                str(row.get('email', '')) or None,
                str(row.get('address', '')) or None,
                float(row.get('salary', 0) or 0),
                str(row.get('date_joined', '')) or None,
                datetime.now(), datetime.now()
            ))
            imported += 1
        except Exception as e:
            print(f"Error importing row {idx}: {e}")
            continue
    
    return imported

def import_suppliers(df):
    imported = 0
    
    if 'name' not in df.columns:
        raise ValueError("Missing required column: name")
    
    for idx, row in df.iterrows():
        try:
            name = str(row.get('name', '')).strip()
            if not name:
                continue
            
            execute_query("""
                INSERT INTO suppliers (name, phone, email, address, city, state, pincode, gst_number, date_created, date_modified)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                name,
                str(row.get('phone', '')) or None,
                str(row.get('email', '')) or None,
                str(row.get('address', '')) or None,
                str(row.get('city', '')) or None,
                str(row.get('state', '')) or None,
                str(row.get('pincode', '')) or None,
                str(row.get('gst_number', '')) or None,
                datetime.now(), datetime.now()
            ))
            imported += 1
        except Exception as e:
            print(f"Error importing row {idx}: {e}")
            continue
    
    return imported
