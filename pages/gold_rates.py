import tkinter as tk
from tkinter import messagebox, ttk
from database.db import execute_query, fetch_query, fetch_one
from datetime import datetime, date
from services.gold_rate_service import GoldRateService

rates_tree = None

def gold_rates_page(parent):
    global rates_tree
    
    for widget in parent.winfo_children():
        widget.destroy()
    
    frame = ttk.Frame(parent)
    frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    
    title_frame = ttk.Frame(frame)
    title_frame.pack(fill=tk.X, pady=10)
    
    title_label = ttk.Label(title_frame, text="Gold Rate Management", font=("Segoe UI", 16, "bold"))
    title_label.pack(side=tk.LEFT)
    
    current_rates_frame = ttk.LabelFrame(frame, text="Current Rates (Today)", padding=10)
    current_rates_frame.pack(fill=tk.X, pady=10)
    
    current_rates = GoldRateService.get_all_current_rates()
    
    if current_rates:
        for i, rate in enumerate(current_rates):
            rate_text = f"{rate['purity']}: ₹{rate['rate_per_gram']:,.2f}/gm"
            if rate['making_charges']:
                rate_text += f" (Making: ₹{rate['making_charges']:,.2f}/gm)"
            ttk.Label(current_rates_frame, text=rate_text, font=("Segoe UI", 11)).grid(row=0, column=i, padx=20)
    else:
        ttk.Label(current_rates_frame, text="No rates set. Please add rates below.", font=("Segoe UI", 11)).pack()
    
    update_frame = ttk.LabelFrame(frame, text="Update Gold Rates", padding=10)
    update_frame.pack(fill=tk.X, pady=10)
    
    form_row = ttk.Frame(update_frame)
    form_row.pack(fill=tk.X, pady=5)
    
    ttk.Label(form_row, text="Date:").pack(side=tk.LEFT, padx=5)
    date_entry = ttk.Entry(form_row, width=12)
    date_entry.insert(0, datetime.now().strftime('%Y-%m-%d'))
    date_entry.pack(side=tk.LEFT, padx=5)
    
    ttk.Label(form_row, text="Purity:").pack(side=tk.LEFT, padx=10)
    purity_combo = ttk.Combobox(form_row, values=GoldRateService.PURITIES, width=8)
    purity_combo.set('22K')
    purity_combo.pack(side=tk.LEFT, padx=5)
    
    ttk.Label(form_row, text="Rate/gm (₹):").pack(side=tk.LEFT, padx=10)
    rate_entry = ttk.Entry(form_row, width=12)
    rate_entry.pack(side=tk.LEFT, padx=5)
    
    ttk.Label(form_row, text="Making/gm (₹):").pack(side=tk.LEFT, padx=10)
    making_entry = ttk.Entry(form_row, width=10)
    making_entry.insert(0, "0")
    making_entry.pack(side=tk.LEFT, padx=5)
    
    def update_rate():
        purity = purity_combo.get()
        rate_str = rate_entry.get()
        
        if not purity or not rate_str:
            messagebox.showwarning("Validation", "Please enter purity and rate!")
            return
        
        try:
            rate = float(rate_str)
            making = float(making_entry.get() or 0)
            rate_date = date_entry.get()
        except ValueError:
            messagebox.showerror("Error", "Invalid rate value!")
            return
        
        try:
            GoldRateService.update_rate(purity, rate, making, "", rate_date)
            messagebox.showinfo("Success", f"Rate updated for {purity}!\n\nNew Rate: ₹{rate:,.2f}/gm")
            gold_rates_page(parent)
        except Exception as e:
            messagebox.showerror("Error", f"Error updating rate: {str(e)}")
    
    ttk.Button(form_row, text="Update Rate", command=update_rate).pack(side=tk.LEFT, padx=20)
    
    quick_update = ttk.LabelFrame(frame, text="Quick Update All Rates", padding=10)
    quick_update.pack(fill=tk.X, pady=10)
    
    quick_row = ttk.Frame(quick_update)
    quick_row.pack(fill=tk.X)
    
    rate_entries = {}
    purities_to_show = ['24K', '22K', '18K', '916']
    
    for purity in purities_to_show:
        ttk.Label(quick_row, text=f"{purity}:").pack(side=tk.LEFT, padx=5)
        rate_entries[purity] = ttk.Entry(quick_row, width=10)
        current = GoldRateService.get_current_rate(purity)
        if current:
            rate_entries[purity].insert(0, str(current['rate_per_gram']))
        rate_entries[purity].pack(side=tk.LEFT, padx=5)
    
    def update_all_rates():
        updated = 0
        for purity, entry in rate_entries.items():
            rate_str = entry.get().strip()
            if rate_str:
                try:
                    rate = float(rate_str)
                    GoldRateService.update_rate(purity, rate, 0, "Bulk update")
                    updated += 1
                except:
                    pass
        
        if updated > 0:
            messagebox.showinfo("Success", f"Updated {updated} rates successfully!")
            gold_rates_page(parent)
        else:
            messagebox.showwarning("Warning", "No rates were updated!")
    
    ttk.Button(quick_row, text="Update All", command=update_all_rates).pack(side=tk.LEFT, padx=20)
    
    history_frame = ttk.LabelFrame(frame, text="Rate History", padding=10)
    history_frame.pack(fill=tk.BOTH, expand=True, pady=10)
    
    filter_row = ttk.Frame(history_frame)
    filter_row.pack(fill=tk.X, pady=5)
    
    ttk.Label(filter_row, text="Filter by Purity:").pack(side=tk.LEFT, padx=5)
    filter_purity = ttk.Combobox(filter_row, values=['All'] + GoldRateService.PURITIES, width=10)
    filter_purity.set('All')
    filter_purity.pack(side=tk.LEFT, padx=5)
    filter_purity.bind('<<ComboboxSelected>>', lambda e: refresh_history())
    
    columns = ('ID', 'Date', 'Purity', 'Rate/gm', 'Making/gm', 'Notes')
    rates_tree = ttk.Treeview(history_frame, columns=columns, height=10, show='headings')
    
    col_widths = {'ID': 40, 'Date': 100, 'Purity': 80, 'Rate/gm': 120, 'Making/gm': 100, 'Notes': 150}
    for col in columns:
        rates_tree.heading(col, text=col)
        rates_tree.column(col, width=col_widths.get(col, 100), anchor='center')
    
    scrollbar = ttk.Scrollbar(history_frame, orient=tk.VERTICAL, command=rates_tree.yview)
    rates_tree.configure(yscroll=scrollbar.set)
    rates_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
    def refresh_history():
        for item in rates_tree.get_children():
            rates_tree.delete(item)
        
        purity_filter = filter_purity.get()
        if purity_filter == 'All':
            history = GoldRateService.get_rate_history(limit=100)
        else:
            history = GoldRateService.get_rate_history(purity=purity_filter, limit=100)
        
        for rate in history:
            rates_tree.insert('', 'end', values=(
                rate[0], rate[1], rate[2],
                f"₹{rate[3]:,.2f}", f"₹{rate[4]:,.2f}" if rate[4] else "₹0.00",
                rate[5] or ""
            ))
    
    refresh_history()
    
    btn_frame = ttk.Frame(history_frame)
    btn_frame.pack(fill=tk.X, pady=5)
    
    def delete_selected():
        selected = rates_tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select a rate to delete!")
            return
        
        rate_id = rates_tree.item(selected[0])['values'][0]
        if messagebox.askyesno("Confirm", "Are you sure you want to delete this rate entry?"):
            GoldRateService.delete_rate(rate_id)
            refresh_history()
    
    ttk.Button(btn_frame, text="Delete Selected", command=delete_selected).pack(side=tk.LEFT, padx=5)
    ttk.Button(btn_frame, text="Refresh", command=refresh_history).pack(side=tk.LEFT, padx=5)
