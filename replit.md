# MT GOLD LAND - Gold Shop Management System

## Overview
A desktop GUI application for managing gold shop operations, built with Python and Tkinter.

## Project Structure
```
├── main.py              # Main application entry point with Tkinter GUI
├── config.py            # Application configuration and settings
├── database/
│   ├── db.py           # Database connection and query utilities
│   └── goldshop.db     # SQLite database
├── pages/              # UI page modules
│   ├── bills.py        # Bill management
│   ├── customers.py    # Customer management
│   ├── dashboard.py    # Dashboard view
│   ├── data_import.py  # Data import functionality
│   ├── employees.py    # Employee management
│   ├── gold_rates.py   # Gold rate management
│   ├── items.py        # Item management
│   ├── reports.py      # Reports generation
│   └── transactions.py # Transaction handling
├── services/           # Business logic services
│   ├── gold_rate_service.py
│   ├── purchase_service.py
│   ├── sales_service.py
│   └── stock_service.py
├── utils/              # Utility functions
│   ├── export.py       # Export functionality
│   ├── helpers.py      # Helper functions
│   └── validators.py   # Input validation
└── requirements.txt    # Python dependencies
```

## Technology Stack
- **Language**: Python 3.11
- **GUI Framework**: Tkinter
- **Database**: SQLite (local file: goldshop.db)
- **Dependencies**: Flask, openpyxl, Pillow, reportlab, matplotlib, pandas

## Running the Application
The application runs as a desktop GUI via VNC. Use the "Gold Shop Management" workflow to start.

## Features
- Dashboard with business overview
- Customer and employee management
- Item inventory management
- Gold rate tracking
- Sales and purchase transactions
- Bill generation
- Reports generation
- Data import/export capabilities

## Recent Changes
- December 12, 2025: Initial setup in Replit environment with Python 3.11 and VNC display
