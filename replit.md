# MT GOLD LAND - Jewelry Management System (Gold & Diamond)

## Overview
A comprehensive Gold and Diamond Shop Management System built with Python Tkinter. The system manages inventory (both gold and diamond jewelry), billing, customers, employees, suppliers, stock movements, gold/diamond rates, and advance orders.

## Current State
Version 2.0.0 - Multi-material support (Gold and Diamond)

## Features
- **Multi-Material Support**: Full support for Gold and Diamond jewelry with material-specific details
- **Inventory Management**: Track items with material type, purity/clarity, weight, and pricing
- **Billing System**: Sales and purchase bills with auto-customer creation and employee tracking
- **Rate Management**: Separate rate tables for Gold (by purity) and Diamond (by clarity/color/shape)
- **Advance Orders**: Custom order booking system with tracking, payments, and status management
- **Stock Management**: Manual stock adjustments with audit trail
- **Dashboard**: Visual overview with gold and diamond statistics
- **Reports**: Sales, purchases, stock, and financial reports

## Recent Changes
- Added Diamond jewelry support with clarity, color, cut, carat tracking
- Created advance orders system for custom bookings
- Added auto-customer creation when creating bills
- Added employee selection to all billing transactions
- Enhanced stock management with manual adjustment feature
- Updated dashboard with gold/diamond stock statistics
- Added diamond rate management alongside gold rates

## Project Architecture

### Database
- SQLite database (`gold_shop.db`)
- Tables: items, customers, employees, suppliers, bills, bill_items, gold_rates, diamond_rates, advance_orders, stock_movements, materials, etc.

### File Structure
```
/
├── main.py                  # Application entry point, menu, navigation
├── database/
│   └── db.py               # Database connection and table creation
├── pages/
│   ├── dashboard.py        # Dashboard with statistics and charts
│   ├── items.py            # Item management (gold & diamond)
│   ├── bills.py            # Billing system
│   ├── customers.py        # Customer management
│   ├── employees.py        # Employee management
│   ├── gold_rates.py       # Gold & Diamond rate management
│   ├── advance_orders.py   # Advance order booking system
│   ├── reports.py          # Various reports
│   └── ...
├── services/
│   ├── stock_service.py    # Stock management operations
│   ├── gold_rate_service.py # Gold & Diamond rate services
│   ├── advance_order_service.py # Advance order operations
│   ├── sales_service.py    # Sales operations
│   └── purchase_service.py # Purchase operations
└── utils/
    ├── validators.py       # Input validation
    ├── helpers.py          # Helper functions
    └── export.py           # Export functionality
```

### Running the Application
- Uses VNC for GUI display (Tkinter desktop application)
- Run via `python main.py` command
- Workflow: "Gold Shop Management" configured for VNC output

## User Preferences
- Material-aware system for gold and diamond jewelry
- Auto-create customers when adding bills if they don't exist
- Track employee for each transaction
- Support advance orders/custom bookings
- Manual stock adjustments with reasons

## Technical Notes
- Desktop GUI application using Tkinter (not web-based)
- Runs via VNC in Replit environment
- SQLite for data storage
- Matplotlib for dashboard charts
