import tkinter as tk
from tkinter import messagebox, ttk
from database.db import execute_query, fetch_query
from datetime import datetime

def employees_page(parent):
    for widget in parent.winfo_children():
        widget.destroy()
    
    frame = ttk.Frame(parent)
    frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    
    # Title
    title_label = ttk.Label(frame, text="Employee Management", font=("Segoe UI", 16, "bold"))
    title_label.pack(pady=10)
    
    # Button frame
    button_frame = ttk.Frame(frame)
    button_frame.pack(fill=tk.X, pady=10)
    
    ttk.Button(button_frame, text="Add Employee", command=lambda: show_add_employee_dialog(parent)).pack(side=tk.LEFT, padx=5)
    ttk.Button(button_frame, text="View Details", command=lambda: show_employee_details(parent)).pack(side=tk.LEFT, padx=5)
    ttk.Button(button_frame, text="Refresh", command=lambda: refresh_employees_list(tree)).pack(side=tk.LEFT, padx=5)
    
    # Treeview for employees
    columns = ('ID', 'Name', 'Position', 'Phone', 'Salary', 'Status')
    tree = ttk.Treeview(frame, columns=columns, height=15)
    
    for col in columns:
        tree.column(col, width=150)
        tree.heading(col, text=col)
    
    tree.pack(fill=tk.BOTH, expand=True)
    
    refresh_employees_list(tree)

def refresh_employees_list(tree):
    for item in tree.get_children():
        tree.delete(item)
    
    employees = fetch_query("""
        SELECT id, name, position, phone, salary, status
        FROM employees
        ORDER BY date_created DESC
    """)
    
    for emp in employees:
        tree.insert('', 'end', values=emp)

def show_add_employee_dialog(parent):
    dialog = tk.Toplevel(parent)
    dialog.title("Add New Employee")
    dialog.geometry("400x500")
    
    fields = {}
    
    labels = ['Name', 'Position', 'Phone', 'Email', 'Address', 'Salary', 'Date Joined']
    
    for label in labels:
        ttk.Label(dialog, text=f"{label}:").pack(pady=5)
        fields[label.lower()] = ttk.Entry(dialog, width=40)
        fields[label.lower()].pack(pady=5)
    
    def save_employee():
        try:
            execute_query("""
                INSERT INTO employees (name, position, phone, email, address, salary, date_joined, status, date_created, date_modified)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                fields['name'].get(),
                fields['position'].get(),
                fields['phone'].get(),
                fields['email'].get(),
                fields['address'].get(),
                float(fields['salary'].get()),
                fields['date joined'].get(),
                'Active',
                datetime.now(),
                datetime.now()
            ))
            messagebox.showinfo("Success", "Employee added successfully!")
            dialog.destroy()
        except Exception as e:
            messagebox.showerror("Error", f"Error adding employee: {str(e)}")
    
    ttk.Button(dialog, text="Save", command=save_employee).pack(pady=20)

def show_employee_details(parent):
    messagebox.showinfo("Employee Details", "Select employee from list to view details")