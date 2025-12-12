import tkinter as tk
from tkinter import messagebox, ttk
from database.db import execute_query, fetch_query, fetch_one
from datetime import datetime

employees_tree = None

def employees_page(parent):
    global employees_tree
    
    for widget in parent.winfo_children():
        widget.destroy()
    
    frame = ttk.Frame(parent)
    frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    
    title_frame = ttk.Frame(frame)
    title_frame.pack(fill=tk.X, pady=10)
    
    title_label = ttk.Label(title_frame, text="Employee Management", font=("Segoe UI", 16, "bold"))
    title_label.pack(side=tk.LEFT)
    
    search_frame = ttk.Frame(frame)
    search_frame.pack(fill=tk.X, pady=5)
    
    ttk.Label(search_frame, text="Search:").pack(side=tk.LEFT, padx=5)
    search_var = tk.StringVar()
    search_entry = ttk.Entry(search_frame, textvariable=search_var, width=30)
    search_entry.pack(side=tk.LEFT, padx=5)
    
    def search_employees():
        refresh_employees_list(employees_tree, search_var.get())
    
    ttk.Button(search_frame, text="Search", command=search_employees).pack(side=tk.LEFT, padx=5)
    ttk.Button(search_frame, text="Clear", command=lambda: [search_var.set(""), refresh_employees_list(employees_tree)]).pack(side=tk.LEFT, padx=5)
    
    filter_frame = ttk.Frame(frame)
    filter_frame.pack(fill=tk.X, pady=5)
    
    ttk.Label(filter_frame, text="Status:").pack(side=tk.LEFT, padx=5)
    status_var = tk.StringVar(value="All")
    status_combo = ttk.Combobox(filter_frame, textvariable=status_var, values=['All', 'Active', 'Inactive'], width=15)
    status_combo.pack(side=tk.LEFT, padx=5)
    status_combo.bind('<<ComboboxSelected>>', lambda e: refresh_employees_list(employees_tree, "", status_var.get()))
    
    button_frame = ttk.Frame(frame)
    button_frame.pack(fill=tk.X, pady=10)
    
    ttk.Button(button_frame, text="Add Employee", command=lambda: show_add_employee_dialog(parent)).pack(side=tk.LEFT, padx=5)
    ttk.Button(button_frame, text="Edit Employee", command=lambda: show_edit_employee_dialog(parent, employees_tree)).pack(side=tk.LEFT, padx=5)
    ttk.Button(button_frame, text="Delete Employee", command=lambda: delete_employee(employees_tree)).pack(side=tk.LEFT, padx=5)
    ttk.Button(button_frame, text="View Details", command=lambda: view_employee_details(employees_tree)).pack(side=tk.LEFT, padx=5)
    ttk.Button(button_frame, text="Toggle Status", command=lambda: toggle_employee_status(employees_tree)).pack(side=tk.LEFT, padx=5)
    ttk.Button(button_frame, text="Refresh", command=lambda: refresh_employees_list(employees_tree)).pack(side=tk.LEFT, padx=5)
    
    tree_frame = ttk.Frame(frame)
    tree_frame.pack(fill=tk.BOTH, expand=True)
    
    columns = ('ID', 'Name', 'Position', 'Phone', 'Email', 'Salary', 'Date Joined', 'Status')
    employees_tree = ttk.Treeview(tree_frame, columns=columns, height=15, show='headings')
    
    col_widths = {'ID': 50, 'Name': 150, 'Position': 100, 'Phone': 100, 
                  'Email': 150, 'Salary': 100, 'Date Joined': 100, 'Status': 80}
    
    for col in columns:
        employees_tree.column(col, width=col_widths.get(col, 100), anchor='center')
        employees_tree.heading(col, text=col, command=lambda c=col: sort_column(employees_tree, c, False))
    
    scrollbar_y = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=employees_tree.yview)
    employees_tree.configure(yscroll=scrollbar_y.set)
    
    employees_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y)
    
    employees_tree.bind('<Double-1>', lambda e: view_employee_details(employees_tree))
    
    refresh_employees_list(employees_tree)
    
    status_frame = ttk.Frame(frame)
    status_frame.pack(fill=tk.X, pady=5)
    
    active_count = fetch_query("SELECT COUNT(*) FROM employees WHERE status = 'Active'")[0][0]
    total_count = fetch_query("SELECT COUNT(*) FROM employees")[0][0]
    total_salary = fetch_query("SELECT COALESCE(SUM(salary), 0) FROM employees WHERE status = 'Active'")[0][0]
    ttk.Label(status_frame, text=f"Active: {active_count}/{total_count} | Monthly Salary Total: ₹{total_salary:,.2f}").pack(side=tk.LEFT)

def sort_column(tree, col, reverse):
    items = [(tree.set(k, col), k) for k in tree.get_children('')]
    try:
        items.sort(key=lambda t: float(t[0].replace('₹','').replace(',','')) if '₹' in t[0] else t[0], reverse=reverse)
    except:
        items.sort(reverse=reverse)
    
    for index, (val, k) in enumerate(items):
        tree.move(k, '', index)
    
    tree.heading(col, command=lambda: sort_column(tree, col, not reverse))

def refresh_employees_list(tree, search_term="", status_filter="All"):
    if tree is None:
        return
        
    for item in tree.get_children():
        tree.delete(item)
    
    query = """
        SELECT id, name, position, phone, email, salary, date_joined, status
        FROM employees
        WHERE 1=1
    """
    params = []
    
    if search_term:
        query += " AND (name LIKE ? OR position LIKE ? OR phone LIKE ?)"
        search_pattern = f"%{search_term}%"
        params.extend([search_pattern, search_pattern, search_pattern])
    
    if status_filter and status_filter != "All":
        query += " AND status = ?"
        params.append(status_filter)
    
    query += " ORDER BY name"
    
    employees = fetch_query(query, tuple(params)) if params else fetch_query(query)
    
    for emp in employees:
        formatted = (
            emp[0], emp[1], emp[2] or "N/A", emp[3] or "N/A",
            emp[4] or "N/A", f"₹{emp[5]:,.2f}" if emp[5] else "₹0.00",
            emp[6] or "N/A", emp[7]
        )
        tree.insert('', 'end', values=formatted)

def show_add_employee_dialog(parent):
    dialog = tk.Toplevel(parent)
    dialog.title("Add New Employee")
    dialog.geometry("450x550")
    dialog.transient(parent)
    dialog.grab_set()
    
    main_frame = ttk.Frame(dialog, padding=20)
    main_frame.pack(fill=tk.BOTH, expand=True)
    
    ttk.Label(main_frame, text="Add New Employee", font=("Segoe UI", 14, "bold")).pack(pady=10)
    
    form_frame = ttk.Frame(main_frame)
    form_frame.pack(fill=tk.X)
    
    fields = {}
    
    row = 0
    ttk.Label(form_frame, text="Name *:").grid(row=row, column=0, sticky='w', pady=5)
    fields['name'] = ttk.Entry(form_frame, width=35)
    fields['name'].grid(row=row, column=1, pady=5, padx=5)
    
    row += 1
    ttk.Label(form_frame, text="Position:").grid(row=row, column=0, sticky='w', pady=5)
    fields['position'] = ttk.Combobox(form_frame, values=['Manager', 'Sales Executive', 'Accountant', 'Goldsmith', 'Cashier', 'Other'], width=32)
    fields['position'].grid(row=row, column=1, pady=5, padx=5)
    
    row += 1
    ttk.Label(form_frame, text="Phone:").grid(row=row, column=0, sticky='w', pady=5)
    fields['phone'] = ttk.Entry(form_frame, width=35)
    fields['phone'].grid(row=row, column=1, pady=5, padx=5)
    
    row += 1
    ttk.Label(form_frame, text="Email:").grid(row=row, column=0, sticky='w', pady=5)
    fields['email'] = ttk.Entry(form_frame, width=35)
    fields['email'].grid(row=row, column=1, pady=5, padx=5)
    
    row += 1
    ttk.Label(form_frame, text="Address:").grid(row=row, column=0, sticky='w', pady=5)
    fields['address'] = ttk.Entry(form_frame, width=35)
    fields['address'].grid(row=row, column=1, pady=5, padx=5)
    
    row += 1
    ttk.Label(form_frame, text="Salary (₹):").grid(row=row, column=0, sticky='w', pady=5)
    fields['salary'] = ttk.Entry(form_frame, width=35)
    fields['salary'].grid(row=row, column=1, pady=5, padx=5)
    
    row += 1
    ttk.Label(form_frame, text="Date Joined:").grid(row=row, column=0, sticky='w', pady=5)
    fields['date_joined'] = ttk.Entry(form_frame, width=35)
    fields['date_joined'].insert(0, datetime.now().strftime('%Y-%m-%d'))
    fields['date_joined'].grid(row=row, column=1, pady=5, padx=5)
    
    row += 1
    ttk.Label(form_frame, text="Status:").grid(row=row, column=0, sticky='w', pady=5)
    fields['status'] = ttk.Combobox(form_frame, values=['Active', 'Inactive'], width=32)
    fields['status'].set('Active')
    fields['status'].grid(row=row, column=1, pady=5, padx=5)
    
    def save_employee():
        name = fields['name'].get().strip()
        
        if not name:
            messagebox.showwarning("Validation", "Employee name is required!")
            return
        
        try:
            salary = float(fields['salary'].get() or 0)
        except ValueError:
            messagebox.showerror("Error", "Invalid salary amount!")
            return
        
        try:
            execute_query("""
                INSERT INTO employees (name, position, phone, email, address, salary, 
                                       date_joined, status, date_created, date_modified)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                name, fields['position'].get() or None, fields['phone'].get() or None,
                fields['email'].get() or None, fields['address'].get() or None, salary,
                fields['date_joined'].get() or None, fields['status'].get() or 'Active',
                datetime.now(), datetime.now()
            ))
            messagebox.showinfo("Success", "Employee added successfully!")
            dialog.destroy()
            if employees_tree:
                refresh_employees_list(employees_tree)
        except Exception as e:
            if "UNIQUE constraint failed" in str(e):
                messagebox.showerror("Error", "An employee with this name already exists!")
            else:
                messagebox.showerror("Error", f"Error adding employee: {str(e)}")
    
    btn_frame = ttk.Frame(main_frame)
    btn_frame.pack(pady=20)
    
    ttk.Button(btn_frame, text="Save", command=save_employee, width=15).pack(side=tk.LEFT, padx=10)
    ttk.Button(btn_frame, text="Cancel", command=dialog.destroy, width=15).pack(side=tk.LEFT, padx=10)

def show_edit_employee_dialog(parent, tree):
    selected = tree.selection()
    if not selected:
        messagebox.showwarning("Warning", "Please select an employee to edit!")
        return
    
    emp_id = tree.item(selected[0])['values'][0]
    
    emp = fetch_one("""
        SELECT id, name, position, phone, email, address, salary, date_joined, status
        FROM employees WHERE id = ?
    """, (emp_id,))
    
    if not emp:
        messagebox.showerror("Error", "Employee not found!")
        return
    
    dialog = tk.Toplevel(parent)
    dialog.title("Edit Employee")
    dialog.geometry("450x550")
    dialog.transient(parent)
    dialog.grab_set()
    
    main_frame = ttk.Frame(dialog, padding=20)
    main_frame.pack(fill=tk.BOTH, expand=True)
    
    ttk.Label(main_frame, text="Edit Employee", font=("Segoe UI", 14, "bold")).pack(pady=10)
    
    form_frame = ttk.Frame(main_frame)
    form_frame.pack(fill=tk.X)
    
    fields = {}
    
    row = 0
    ttk.Label(form_frame, text="Name *:").grid(row=row, column=0, sticky='w', pady=5)
    fields['name'] = ttk.Entry(form_frame, width=35)
    fields['name'].insert(0, emp[1] or "")
    fields['name'].grid(row=row, column=1, pady=5, padx=5)
    
    row += 1
    ttk.Label(form_frame, text="Position:").grid(row=row, column=0, sticky='w', pady=5)
    fields['position'] = ttk.Combobox(form_frame, values=['Manager', 'Sales Executive', 'Accountant', 'Goldsmith', 'Cashier', 'Other'], width=32)
    if emp[2]:
        fields['position'].set(emp[2])
    fields['position'].grid(row=row, column=1, pady=5, padx=5)
    
    row += 1
    ttk.Label(form_frame, text="Phone:").grid(row=row, column=0, sticky='w', pady=5)
    fields['phone'] = ttk.Entry(form_frame, width=35)
    fields['phone'].insert(0, emp[3] or "")
    fields['phone'].grid(row=row, column=1, pady=5, padx=5)
    
    row += 1
    ttk.Label(form_frame, text="Email:").grid(row=row, column=0, sticky='w', pady=5)
    fields['email'] = ttk.Entry(form_frame, width=35)
    fields['email'].insert(0, emp[4] or "")
    fields['email'].grid(row=row, column=1, pady=5, padx=5)
    
    row += 1
    ttk.Label(form_frame, text="Address:").grid(row=row, column=0, sticky='w', pady=5)
    fields['address'] = ttk.Entry(form_frame, width=35)
    fields['address'].insert(0, emp[5] or "")
    fields['address'].grid(row=row, column=1, pady=5, padx=5)
    
    row += 1
    ttk.Label(form_frame, text="Salary (₹):").grid(row=row, column=0, sticky='w', pady=5)
    fields['salary'] = ttk.Entry(form_frame, width=35)
    fields['salary'].insert(0, str(emp[6]) if emp[6] else "0")
    fields['salary'].grid(row=row, column=1, pady=5, padx=5)
    
    row += 1
    ttk.Label(form_frame, text="Date Joined:").grid(row=row, column=0, sticky='w', pady=5)
    fields['date_joined'] = ttk.Entry(form_frame, width=35)
    fields['date_joined'].insert(0, str(emp[7]) if emp[7] else "")
    fields['date_joined'].grid(row=row, column=1, pady=5, padx=5)
    
    row += 1
    ttk.Label(form_frame, text="Status:").grid(row=row, column=0, sticky='w', pady=5)
    fields['status'] = ttk.Combobox(form_frame, values=['Active', 'Inactive'], width=32)
    fields['status'].set(emp[8] or 'Active')
    fields['status'].grid(row=row, column=1, pady=5, padx=5)
    
    def update_employee():
        name = fields['name'].get().strip()
        
        if not name:
            messagebox.showwarning("Validation", "Employee name is required!")
            return
        
        try:
            salary = float(fields['salary'].get() or 0)
        except ValueError:
            messagebox.showerror("Error", "Invalid salary amount!")
            return
        
        try:
            execute_query("""
                UPDATE employees 
                SET name = ?, position = ?, phone = ?, email = ?, address = ?, 
                    salary = ?, date_joined = ?, status = ?, date_modified = ?
                WHERE id = ?
            """, (
                name, fields['position'].get() or None, fields['phone'].get() or None,
                fields['email'].get() or None, fields['address'].get() or None, salary,
                fields['date_joined'].get() or None, fields['status'].get() or 'Active',
                datetime.now(), emp_id
            ))
            messagebox.showinfo("Success", "Employee updated successfully!")
            dialog.destroy()
            refresh_employees_list(tree)
        except Exception as e:
            messagebox.showerror("Error", f"Error updating employee: {str(e)}")
    
    btn_frame = ttk.Frame(main_frame)
    btn_frame.pack(pady=20)
    
    ttk.Button(btn_frame, text="Update", command=update_employee, width=15).pack(side=tk.LEFT, padx=10)
    ttk.Button(btn_frame, text="Cancel", command=dialog.destroy, width=15).pack(side=tk.LEFT, padx=10)

def delete_employee(tree):
    selected = tree.selection()
    if not selected:
        messagebox.showwarning("Warning", "Please select an employee to delete!")
        return
    
    emp_id = tree.item(selected[0])['values'][0]
    emp_name = tree.item(selected[0])['values'][1]
    
    bills = fetch_query("SELECT COUNT(*) FROM bills WHERE employee_id = ?", (emp_id,))[0][0]
    if bills > 0:
        messagebox.showwarning("Warning", f"Cannot delete employee '{emp_name}' because they have {bills} associated bills.\n\nConsider marking them as 'Inactive' instead.")
        return
    
    if messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete employee '{emp_name}'?\n\nThis action cannot be undone."):
        try:
            execute_query("DELETE FROM employees WHERE id = ?", (emp_id,))
            messagebox.showinfo("Success", "Employee deleted successfully!")
            refresh_employees_list(tree)
        except Exception as e:
            messagebox.showerror("Error", f"Error deleting employee: {str(e)}")

def toggle_employee_status(tree):
    selected = tree.selection()
    if not selected:
        messagebox.showwarning("Warning", "Please select an employee!")
        return
    
    emp_id = tree.item(selected[0])['values'][0]
    current_status = tree.item(selected[0])['values'][7]
    new_status = 'Inactive' if current_status == 'Active' else 'Active'
    
    try:
        execute_query("""
            UPDATE employees SET status = ?, date_modified = ? WHERE id = ?
        """, (new_status, datetime.now(), emp_id))
        messagebox.showinfo("Success", f"Employee status changed to {new_status}")
        refresh_employees_list(tree)
    except Exception as e:
        messagebox.showerror("Error", f"Error updating status: {str(e)}")

def view_employee_details(tree):
    selected = tree.selection()
    if not selected:
        messagebox.showwarning("Warning", "Please select an employee to view!")
        return
    
    emp_id = tree.item(selected[0])['values'][0]
    
    emp = fetch_one("""
        SELECT * FROM employees WHERE id = ?
    """, (emp_id,))
    
    if not emp:
        messagebox.showerror("Error", "Employee not found!")
        return
    
    bills_count = fetch_query("SELECT COUNT(*) FROM bills WHERE employee_id = ?", (emp_id,))[0][0]
    
    details = f"""
EMPLOYEE DETAILS
{'='*40}

Name: {emp[1]}
Position: {emp[5] or 'N/A'}
Phone: {emp[2] or 'N/A'}
Email: {emp[3] or 'N/A'}
Address: {emp[4] or 'N/A'}

EMPLOYMENT
Salary: ₹{emp[6]:,.2f} if emp[6] else 'N/A'
Date Joined: {emp[7] or 'N/A'}
Status: {emp[8]}

STATISTICS
Bills Processed: {bills_count}

Created: {emp[9]}
Modified: {emp[10]}
    """
    
    messagebox.showinfo("Employee Details", details)
