import tkinter as tk
from tkinter import Menu, messagebox, ttk

# --- Functions for menu commands ---
def dummy_action(name):
    messagebox.showinfo("Action", f"You clicked on {name}")

# --- Main App Window ---
root = tk.Tk()
root.title("MT GOLD LAND")
root.geometry("1200x700")


# Create a container frame for navbar + main content area
container = tk.Frame(root)
container.pack(fill=tk.BOTH, expand=True)

# Vertical navbar frame on left
navbar = tk.Frame(container, bg="#1e2d3d", width=220)
navbar.pack(side=tk.LEFT, fill=tk.Y)

# Content frame on right to load different pages
content_frame = tk.Frame(container, bg="white")
content_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

# Style for navbar buttons
def make_nav_button(parent, text, command):
    btn = tk.Button(parent, text=text, font=("Segoe UI", 12), fg="white", bg="#1e2d3d", 
                    activebackground="#3a5068", activeforeground="white", bd=0, relief=tk.FLAT,
                    anchor="w", padx=20, pady=12, command=command)
    btn.pack(fill=tk.X)
    return btn

# Placeholders for page switching - replace with your actual form logic
def show_new_bill():
    for widget in content_frame.winfo_children():
        widget.destroy()
    tk.Label(content_frame, text="New Bill Entry Page", font=("Segoe UI", 16), fg="#1e2d3d").pack(pady=80)

def show_manage_items():
    for widget in content_frame.winfo_children():
        widget.destroy()
    tk.Label(content_frame, text="Manage Items (Add/Del/Edit)", font=("Segoe UI", 16), fg="#1e2d3d").pack(pady=80)

def show_manage_customers():
    for widget in content_frame.winfo_children():
        widget.destroy()
    tk.Label(content_frame, text="Manage Customers (Add/Del/Edit)", font=("Segoe UI", 16), fg="#1e2d3d").pack(pady=80)

def show_manage_employees():
    for widget in content_frame.winfo_children():
        widget.destroy()
    tk.Label(content_frame, text="Manage Employees (Add/Del/Edit)", font=("Segoe UI", 16), fg="#1e2d3d").pack(pady=80)

# Add buttons to navbar
make_nav_button(navbar, "Enter New Bill", show_new_bill)
make_nav_button(navbar, "Manage Items", show_manage_items)
make_nav_button(navbar, "Manage Customers", show_manage_customers)
make_nav_button(navbar, "Manage Employees", show_manage_employees)

# Initially show dashboard or blank page
show_new_bill()

# Keep your existing menus and other UI intact below
# e.g. menubar with Transactions, Reports etc. remains as before


# --- Menu Bar ---
menubar = Menu(root)

#-----------DASHBOARD--------------------
deshboard_menu = Menu(menubar, tearoff=0)
deshboard_menu.add_command(label="Dashboard Option", command=lambda: dummy_action("Dashboard"))
menubar.add_cascade(label="Dashboard", menu=deshboard_menu)

# ---------------- MASTER MENU ----------------
master_menu = Menu(menubar, tearoff=0)

# Direct command
master_menu.add_command(label="Items", command=lambda: dummy_action("Items"))

# Item Category submenu
item_category_submenu = Menu(master_menu, tearoff=0)
item_category_submenu.add_command(label="Product", command=lambda: dummy_action("Product"))
item_category_submenu.add_command(label="Brand", command=lambda: dummy_action("Brand"))
item_category_submenu.add_command(label="Model", command=lambda: dummy_action("Model"))
item_category_submenu.add_command(label="Unit", command=lambda: dummy_action("Unit"))
item_category_submenu.add_command(label="Sub Group", command=lambda: dummy_action("Sub Group"))
item_category_submenu.add_command(label="Item Category Prefix", command=lambda: dummy_action("Item Category Prefix"))
master_menu.add_cascade(label="Item Category", menu=item_category_submenu)

# Direct command
master_menu.add_command(label="Rate Update", command=lambda: dummy_action("Rate Update"))

# Barcode List submenu
barcode_submenu = Menu(master_menu, tearoff=0)
barcode_submenu.add_command(label="Barcode List", command=lambda: dummy_action("Barcode List"))
barcode_submenu.add_command(label="Barcode Printing", command=lambda: dummy_action("Barcode Printing"))
barcode_submenu.add_command(label="Barcode Edit", command=lambda: dummy_action("Barcode Edit"))
master_menu.add_cascade(label="Barcode List", menu=barcode_submenu)

# Direct commands
master_menu.add_command(label="Customer", command=lambda: dummy_action("Customer"))
master_menu.add_command(label="Supplier", command=lambda: dummy_action("Supplier"))
master_menu.add_command(label="Employee", command=lambda: dummy_action("Employee"))
master_menu.add_command(label="Smith", command=lambda: dummy_action("Smith"))
master_menu.add_command(label="Jeweller", command=lambda: dummy_action("Jeweller"))
master_menu.add_command(label="Refiner", command=lambda: dummy_action("Refiner"))
master_menu.add_command(label="Account Heads", command=lambda: dummy_action("Account Heads"))
master_menu.add_command(label="Sub Schedule", command=lambda: dummy_action("Sub Schedule"))
master_menu.add_command(label="Cash Flow", command=lambda: dummy_action("Cash Flow"))
master_menu.add_command(label="Schedule", command=lambda: dummy_action("Schedule"))

# Miscellaneous submenu
misc_submenu = Menu(master_menu, tearoff=0)
misc_submenu.add_command(label="Agent", command=lambda: dummy_action("Agent"))
master_menu.add_cascade(label="Miscellaneous", menu=misc_submenu)

# Remaining direct options
master_menu.add_command(label="Complementary Master", command=lambda: dummy_action("Complementary Master"))
master_menu.add_command(label="Custom Voucher", command=lambda: dummy_action("Custom Voucher"))
master_menu.add_command(label="Branch Master", command=lambda: dummy_action("Branch Master"))

# Attach to menubar
menubar.add_cascade(label="Master", menu=master_menu)

# ---------------- TRANSACTIONS MENU (Improved) -------------------------------
transactionsmenu = Menu(menubar, tearoff=0)
# SALES submenu
salesmenu = Menu(transactionsmenu, tearoff=0)
salesmenu.add_command(label="Sales Invoice", command=lambda:dummy_action("Sales Invoice"))
salesmenu.add_command(label="Sales Return", command=lambda:dummy_action("Sales Return"))
salesmenu.add_command(label="DMD Return/DMD OP", command=lambda:dummy_action("DMD Return/DMD OP"))
salesmenu.add_command(label="DMD Sales Wholesale", command=lambda:dummy_action("DMD Sales Wholesale"))
transactionsmenu.add_cascade(label="Sales", menu=salesmenu)

# PURCHASE submenu
purchasemenu = Menu(transactionsmenu, tearoff=0)
purchasemenu.add_command(label="Purchase Invoice", command=lambda:dummy_action("Purchase Invoice"))
purchasemenu.add_command(label="Purchase Return", command=lambda:dummy_action("Purchase Return"))
purchasemenu.add_command(label="Diamond Purchase", command=lambda:dummy_action("Diamond Purchase"))
purchasemenu.add_command(label="Diamond Purchase Return", command=lambda:dummy_action("Diamond Purchase Return"))
purchasemenu.add_command(label="Direct Purchase", command=lambda:dummy_action("Direct Purchase"))
purchasemenu.add_command(label="Direct Purchase Return", command=lambda:dummy_action("Direct Purchase Return"))
purchasemenu.add_command(label="DMD Stone Purchase", command=lambda:dummy_action("DMD Stone Purchase"))
transactionsmenu.add_cascade(label="Purchase", menu=purchasemenu)

# SALES ORDER submenu
salesordermenu = Menu(transactionsmenu, tearoff=0)
salesordermenu.add_command(label="New Order", command=lambda:dummy_action("New Order"))
salesordermenu.add_command(label="Additional Order Advance", command=lambda:dummy_action("Additional Order Advance"))
salesordermenu.add_command(label="Order Advance Cash Refund", command=lambda:dummy_action("Order Advance Cash Refund"))
transactionsmenu.add_cascade(label="Sales Order", menu=salesordermenu)

# BARCODE ENTRY
transactionsmenu.add_command(label="Barcode Entry (Ctrl+F4)", command=lambda:dummy_action("Barcode Entry"))

# TRANSFERS submenu
transfersmenu = Menu(transactionsmenu, tearoff=0)
transfersmenu.add_command(label="Smith (Ctrl+S)", command=lambda:dummy_action("Smith"))
transfersmenu.add_command(label="Cash for Weight (Smith)", command=lambda:dummy_action("Cash for Weight Smith"))
transfersmenu.add_command(label="Jeweller (Alt+J)", command=lambda:dummy_action("Jeweller"))
transfersmenu.add_command(label="Cash for Weight (Jeweller)", command=lambda:dummy_action("Cash for Weight Jeweller"))
transfersmenu.add_command(label="Item Transfer", command=lambda:dummy_action("Item Transfer"))
transfersmenu.add_command(label="Branch Transfer", command=lambda:dummy_action("Branch Transfer"))
transactionsmenu.add_cascade(label="Transfers", menu=transfersmenu)

# STOCK ADJUSTMENTS
transactionsmenu.add_command(label="Stock Adjustments", command=lambda:dummy_action("Stock Adjustments"))

# REFINING submenu
refiningmenu = Menu(transactionsmenu, tearoff=0)
refiningmenu.add_command(label="Issue", command=lambda:dummy_action("Refining Issue"))
refiningmenu.add_command(label="Return", command=lambda:dummy_action("Refining Return"))
refiningmenu.add_command(label="Final Return", command=lambda:dummy_action("Refining Final Return"))
refiningmenu.add_command(label="Melting Issue", command=lambda:dummy_action("Refining Melting Issue"))
refiningmenu.add_command(label="Melting Return", command=lambda:dummy_action("Refining Melting Return"))
transactionsmenu.add_cascade(label="Refining", menu=refiningmenu)

# SAMPLE submenu
samplemenu = Menu(transactionsmenu, tearoff=0)
samplemenu.add_command(label="Issue", command=lambda:dummy_action("Sample Issue"))
samplemenu.add_command(label="Return", command=lambda:dummy_action("Sample Return"))
transactionsmenu.add_cascade(label="Sample", menu=samplemenu)

# GOLD DEPOSIT / WITHDRAWAL submenu
golddepomenu = Menu(transactionsmenu, tearoff=0)
golddepomenu.add_command(label="Deposit", command=lambda:dummy_action("Gold Deposit"))
golddepomenu.add_command(label="Withdrawal", command=lambda:dummy_action("Gold Withdrawal"))
transactionsmenu.add_cascade(label="Gold Deposit / Withdrawal", menu=golddepomenu)

# COMPLIMENTARY ITEMS submenu
complimentarymenu = Menu(transactionsmenu, tearoff=0)
complimentarymenu.add_command(label="Purchase", command=lambda:dummy_action("Complimentary Purchase"))
complimentarymenu.add_command(label="Sales / Issue", command=lambda:dummy_action("Complimentary Sales / Issue"))
transactionsmenu.add_cascade(label="Complimentary Items", menu=complimentarymenu)

# POLISHING
transactionsmenu.add_command(label="Polishing", command=lambda:dummy_action("Polishing"))

# SERVICE submenu
servicemenu = Menu(transactionsmenu, tearoff=0)
servicemenu.add_command(label="New Service / Job", command=lambda:dummy_action("New Service / Job"))
servicemenu.add_command(label="Close Service / Job", command=lambda:dummy_action("Close Service / Job"))
transactionsmenu.add_cascade(label="Service", menu=servicemenu)

# BILL WISE TRANSACTION submenu
billwisemenu = Menu(transactionsmenu, tearoff=0)
billwisemenu.add_command(label="Collection (Alt+C)", command=lambda:dummy_action("Collection"))
billwisemenu.add_command(label="Payment (Alt+P)", command=lambda:dummy_action("Payment"))
billwisemenu.add_command(label="Discount in Debit Note", command=lambda:dummy_action("Discount in Debit Note"))
billwisemenu.add_command(label="Discount in Credit Note", command=lambda:dummy_action("Discount in Credit Note"))
transactionsmenu.add_cascade(label="Bill wise Transaction", menu=billwisemenu)

# CUSTOM VOUCHER
transactionsmenu.add_command(label="Custom Voucher", command=lambda:dummy_action("Custom Voucher"))

# ACCOUNTS submenu
accountsmenu = Menu(transactionsmenu, tearoff=0)
accountsmenu.add_command(label="Cash Receipt (Ctrl+R)", command=lambda:dummy_action("Cash Receipt"))
accountsmenu.add_command(label="Cash Payment (Ctrl+P)", command=lambda:dummy_action("Cash Payment"))
accountsmenu.add_command(label="Bank Deposit", command=lambda:dummy_action("Bank Deposit"))
accountsmenu.add_command(label="Bank Withdrawals", command=lambda:dummy_action("Bank Withdrawals"))
accountsmenu.add_command(label="Journal Voucher", command=lambda:dummy_action("Journal Voucher"))
accountsmenu.add_command(label="PDC Transactions", command=lambda:dummy_action("PDC Transactions"))
accountsmenu.add_command(label="Direct Entry", command=lambda:dummy_action("Direct Entry"))
transactionsmenu.add_cascade(label="Accounts", menu=accountsmenu)

# Open Stock Account Entry
transactionsmenu.add_command(label="Opening Stock Account Entry", command=lambda:dummy_action("Opening Stock Account Entry"))

# Cash Point
transactionsmenu.add_command(label="Cash Point", command=lambda:dummy_action("Cash Point"))

# Attach the menu
menubar.add_cascade(label="Transactions", menu=transactionsmenu)


# ---------------- REPORTS MENU (Improved) -------------------------------
reportsmenu = Menu(menubar, tearoff=0)

# Stock submenu
stockmenu = Menu(reportsmenu, tearoff=0)
currentstockmenu = Menu(stockmenu, tearoff=0)
currentstockmenu.add_command(label="Item Wise (Ctrl+I)", command=lambda: dummy_action("Item Wise"))
currentstockmenu.add_command(label="Barcode Wise", command=lambda: dummy_action("Barcode Wise"))
currentstockmenu.add_command(label="Category Wise", command=lambda: dummy_action("Category Wise"))
currentstockmenu.add_command(label="Product Wise", command=lambda: dummy_action("Product Wise"))
currentstockmenu.add_command(label="Type Wise", command=lambda: dummy_action("Type Wise"))
currentstockmenu.add_command(label="Diamond Stock", command=lambda: dummy_action("Diamond Stock"))
stockmenu.add_cascade(label="CurrentStock", menu=currentstockmenu)
stockmenu.add_command(label="Opening Stock", command=lambda: dummy_action("Opening Stock"))
stockmenu.add_command(label="Stock Reconciliation", command=lambda: dummy_action("Stock Reconciliation"))
stockmenu.add_command(label="Reconciliation Crosstab", command=lambda: dummy_action("Reconciliation Crosstab"))
stockmenu.add_command(label="Stock Ledger", command=lambda: dummy_action("Stock Ledger"))
stockmenu.add_command(label="Smith/Jeweller Stock", command=lambda: dummy_action("Smith/Jeweller Stock"))
reportsmenu.add_cascade(label="Stock", menu=stockmenu)

# Sales
reportsmenu.add_command(label="Sales", command=lambda: dummy_action("Sales Report"))

# Sales Profit
reportsmenu.add_command(label="Sales Profit", command=lambda: dummy_action("Sales Profit"))

# Sales Return
reportsmenu.add_command(label="Sales Return", command=lambda: dummy_action("Sales Return"))

# Exchange
reportsmenu.add_command(label="Exchange", command=lambda: dummy_action("Exchange Report"))

# Purchase
reportsmenu.add_command(label="Purchase", command=lambda: dummy_action("Purchase Report"))

# Purchase Return
reportsmenu.add_command(label="Purchase Return", command=lambda: dummy_action("Purchase Return Report"))

# Direct Gold Purchase
reportsmenu.add_command(label="Direct Gold Purchase", command=lambda: dummy_action("Direct Gold Purchase Report"))
reportsmenu.add_command(label="Direct Gold Purchase Return", command=lambda: dummy_action("Direct Gold Purchase Return Report"))

# Diamond submenu
diamondmenu = Menu(reportsmenu, tearoff=0)
diamondmenu.add_command(label="Purchase", command=lambda: dummy_action("Diamond Purchase Report"))
diamondmenu.add_command(label="Purchase Return", command=lambda: dummy_action("Diamond Purchase Return Report"))
diamondmenu.add_command(label="Sales", command=lambda: dummy_action("Diamond Sales Report"))
reportsmenu.add_cascade(label="Diamond", menu=diamondmenu)

# Stock Adjustment
reportsmenu.add_command(label="Stock Adjustment", command=lambda: dummy_action("Stock Adjustment Report"))

# Transfers submenu
transfersmenu = Menu(reportsmenu, tearoff=0)
smithmenu = Menu(transfersmenu, tearoff=0)
smithmenu.add_command(label="Smith Transfer", command=lambda: dummy_action("Smith Transfer"))
smithmenu.add_command(label="Smith Ledger", command=lambda: dummy_action("Smith Ledger"))
smithmenu.add_command(label="Smith Ledger Detailed", command=lambda: dummy_action("Smith Ledger Detailed"))
smithmenu.add_command(label="Smith Reconciliation", command=lambda: dummy_action("Smith Reconciliation"))
transfersmenu.add_cascade(label="Smith", menu=smithmenu)
jewellermenu = Menu(transfersmenu, tearoff=0)
jewellermenu.add_command(label="Jeweller Transfer", command=lambda: dummy_action("Jeweller Transfer"))
jewellermenu.add_command(label="Ledger", command=lambda: dummy_action("Jeweller Ledger"))
jewellermenu.add_command(label="Ledger Detailed", command=lambda: dummy_action("Jeweller Ledger Detailed"))
jewellermenu.add_command(label="Reconciliation", command=lambda: dummy_action("Jeweller Reconciliation"))
transfersmenu.add_cascade(label="Jeweller", menu=jewellermenu)
transfersmenu.add_command(label="Refiner", command=lambda: dummy_action("Refiner Transfer"))
transfersmenu.add_command(label="Item Transfer", command=lambda: dummy_action("Item Transfer"))
transfersmenu.add_command(label="Polishing", command=lambda: dummy_action("Polishing Transfer"))
reportsmenu.add_cascade(label="Transfers", menu=transfersmenu)

# Sample Issue/Return
reportsmenu.add_command(label="Sample Issue/Return", command=lambda: dummy_action("Sample Issue/Return Report"))

# Sales Order submenu
salesordermenu = Menu(reportsmenu, tearoff=0)
salesordermenu.add_command(label="Sales Order", command=lambda: dummy_action("Sales Order Report"))
salesordermenu.add_command(label="Additional Order Advance", command=lambda: dummy_action("Additional Order Advance Report"))
salesordermenu.add_command(label="Order Advance Refund", command=lambda: dummy_action("Order Advance Refund"))
reportsmenu.add_cascade(label="Sales Order", menu=salesordermenu)

# Gold Deposit
reportsmenu.add_command(label="Gold Deposit", command=lambda: dummy_action("Gold Deposit Report"))

# Today's Dues submenu
todaysduesmenu = Menu(reportsmenu, tearoff=0)
todaysduesmenu.add_command(label="Sales Dues", command=lambda: dummy_action("Sales Dues Report"))
todaysduesmenu.add_command(label="Purchase Dues", command=lambda: dummy_action("Purchase Dues Report"))
reportsmenu.add_cascade(label="Today's Dues", menu=todaysduesmenu)

# Barcode Entry
reportsmenu.add_command(label="Barcode Entry", command=lambda: dummy_action("Barcode Entry Report"))

# Day end Report
dayendreport = Menu(reportsmenu, tearoff=0)
dayendreport.add_command(label="Day Summary", command=lambda: dummy_action("Day Summary"))
dayendreport.add_command(label="Day Close Print", command=lambda: dummy_action("Day Close Print"))
dayendreport.add_command(label="Weight and Cash Summary", command=lambda: dummy_action("Weight and Cash Summary"))
dayendreport.add_command(label="Day Book", command=lambda: dummy_action("Day Book"))
dayendreport.add_command(label="Day Book-2024", command=lambda: dummy_action("Day Book-2024"))
reportsmenu.add_cascade(label="Day end Report", menu=dayendreport)

# Tax Reports
reportsmenu.add_command(label="Tax Reports", command=lambda: dummy_action("Tax Reports"))

# Service / Job
reportsmenu.add_command(label="Service / Job", command=lambda: dummy_action("Service / Job Report"))

# Bills Reports
reportsmenu.add_command(label="Bills Reports", command=lambda: dummy_action("Bills Reports"))

# Bills Payables
reportsmenu.add_command(label="Bills Payables", command=lambda: dummy_action("Bills Payables Report"))

# Cash Point
reportsmenu.add_command(label="Cash Point", command=lambda: dummy_action("Cash Point Report"))

# Discount Voucher
reportsmenu.add_command(label="Discount Voucher", command=lambda: dummy_action("Discount Voucher Report"))

# Complementary Items
reportsmenu.add_command(label="Complementary Items", command=lambda: dummy_action("Complementary Items Report"))

# Attach Reports menu
menubar.add_cascade(label="Reports", menu=reportsmenu)


# ---------------- FINANCIAL REPORTS MENU -------------------------------
financialmenu = Menu(menubar, tearoff=0)

# Core books and ledgers
financialmenu.add_command(label="Cash Book (Alt+H)", command=lambda: dummy_action("Cash Book"))
financialmenu.add_command(label="Bank Book", command=lambda: dummy_action("Bank Book"))
financialmenu.add_command(label="Ledger (Ctrl+L)", command=lambda: dummy_action("Ledger"))

# Voucher Reports submenu
vouchermenu = Menu(financialmenu, tearoff=0)
vouchermenu.add_command(label="Day Book", command=lambda: dummy_action("Day Book"))
vouchermenu.add_command(label="Day Account Transactions", command=lambda: dummy_action("Day Account Transactions"))
vouchermenu.add_command(label="Account List", command=lambda: dummy_action("Account List"))
vouchermenu.add_command(label="Receipts / Payments", command=lambda: dummy_action("Receipts / Payments"))
vouchermenu.add_command(label="Journal Register", command=lambda: dummy_action("Journal Register"))
vouchermenu.add_command(label="Chart Of Accounts", command=lambda: dummy_action("Chart Of Accounts"))
financialmenu.add_cascade(label="Voucher Reports", menu=vouchermenu)

# Top-level reports
financialmenu.add_command(label="Trail Balance", command=lambda: dummy_action("Trail Balance"))
financialmenu.add_command(label="Trading Account", command=lambda: dummy_action("Trading Account"))
financialmenu.add_command(label="Trading, P&L Account", command=lambda: dummy_action("Trading, P&L Account"))
financialmenu.add_command(label="Profit or Loss Account", command=lambda: dummy_action("Profit or Loss Account"))
financialmenu.add_command(label="Balance Sheet", command=lambda: dummy_action("Balance Sheet"))
financialmenu.add_command(label="Sundry Debtors", command=lambda: dummy_action("Sundry Debtors"))
financialmenu.add_command(label="Sundry Creditors", command=lambda: dummy_action("Sundry Creditors"))
financialmenu.add_command(label="Opening Balance", command=lambda: dummy_action("Opening Balance"))
financialmenu.add_command(label="Receipt Due Report", command=lambda: dummy_action("Receipt Due Report"))
financialmenu.add_command(label="Sub Schedule Wise Ledger", command=lambda: dummy_action("Sub Schedule Wise Ledger"))

menubar.add_cascade(label="Financial Reports", menu=financialmenu)


# ---------------- SCHEME/CHITTY MENU -------------------------------
schememenu = Menu(menubar, tearoff=0)

schememenu.add_command(label="Scheme Master", command=lambda: dummy_action("Scheme Master"))
schememenu.add_command(label="Scheme Members", command=lambda: dummy_action("Scheme Members"))
schememenu.add_command(label="Scheme Collection       Ctrl+Shift+S", command=lambda: dummy_action("Scheme Collection"))
schememenu.add_command(label="Scheme Refund/Close", command=lambda: dummy_action("Scheme Refund/Close"))
schememenu.add_command(label="Scheme Collection Report", command=lambda: dummy_action("Scheme Collection Report"))
schememenu.add_command(label="Scheme Member Ledger", command=lambda: dummy_action("Scheme Member Ledger"))



menubar.add_cascade(label="Scheme/Chitty", menu=schememenu)

# ---------------- UTILITIES & HELP MENU -------------------------------
utilities_menu = Menu(menubar, tearoff=0)
utilities_menu.add_command(label="Utilities Option", command=lambda: dummy_action("Utilities"))
menubar.add_cascade(label="Utilities", menu=utilities_menu)

help_menu = Menu(menubar, tearoff=0)
help_menu.add_command(label="Help Option", command=lambda: dummy_action("Help"))
menubar.add_cascade(label="Help", menu=help_menu)

# Attach Menu to Root Window
root.config(menu=menubar)
root.mainloop()
