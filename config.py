import os
from pathlib import Path

# Application paths
BASE_DIR = Path(__file__).parent
DATABASE_PATH = BASE_DIR / 'database' / 'goldshop.db'
EXPORT_PATH = BASE_DIR / 'exports'
BACKUP_PATH = BASE_DIR / 'backups'
LOGS_PATH = BASE_DIR / 'logs'

# Create directories if they don't exist
for path in [EXPORT_PATH, BACKUP_PATH, LOGS_PATH]:
    path.mkdir(exist_ok=True)

# Application settings
APP_TITLE = "MT GOLD LAND"
APP_VERSION = "1.0.0"
WINDOW_WIDTH = 1200
WINDOW_HEIGHT = 700

# Currency and units
DEFAULT_CURRENCY = "INR"
DEFAULT_WEIGHT_UNIT = "gm"
DECIMAL_PLACES = 3

# Database settings
DB_TIMEOUT = 30
DB_CHECK_SAME_THREAD = False

# UI Colors
PRIMARY_COLOR = "#1e2d3d"
SECONDARY_COLOR = "#3a5068"
SUCCESS_COLOR = "#28a745"
ERROR_COLOR = "#dc3545"
WARNING_COLOR = "#ffc107"
INFO_COLOR = "#17a2b8"

# Default Font
DEFAULT_FONT = ("Segoe UI", 10)
HEADER_FONT = ("Segoe UI", 14, "bold")