import sqlite3 as sql
from datetime import datetime

# Connect to the SQLite database
conn = sql.connect("test.db")
print("Database created successfully.")

# Creating tables
try:
    # Users table
    conn.execute('''
        CREATE TABLE IF NOT EXISTS Users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL,
            phone TEXT,
            address TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    print("Users table created successfully.")
except Exception as e:
    print(f"Exception {e} occurred while creating Users table.")

try:
    # Purchases table
    conn.execute('''
        CREATE TABLE IF NOT EXISTS Purchases (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            total_amount FLOAT NOT NULL,
            paid_amount FLOAT NOT NULL,
            balance FLOAT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES Users (id)
        )
    ''')
    print("Purchases table created successfully.")
except Exception as e:
    print(f"Exception {e} occurred while creating Purchases table.")

try:
    # PurchaseDetails table
    conn.execute('''
        CREATE TABLE IF NOT EXISTS PurchaseDetails (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            purchase_id INTEGER NOT NULL,
            product_id INTEGER NOT NULL,
            quantity INTEGER NOT NULL,
            sub_total REAL NOT NULL,
            FOREIGN KEY (purchase_id) REFERENCES Purchases (id),
            FOREIGN KEY (product_id) REFERENCES Products (id)
        )
    ''')
    print("PurchaseDetails table created successfully.")
except Exception as e:
    print(f"Exception {e} occurred while creating PurchaseDetails table.")

try:
    # Denominations table
    conn.execute('''
        CREATE TABLE IF NOT EXISTS Denominations (
            value INTEGER PRIMARY KEY,
            count INTEGER NOT NULL
        )
    ''')
    print("Denominations table created successfully.")
except Exception as e:
    print(f"Exception {e} occurred while creating Denominations table.")

try:
    # Products table
    conn.execute('''
        CREATE TABLE IF NOT EXISTS Products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            available_stocks INTEGER NOT NULL,
            price_per_unit REAL NOT NULL,
            tax_percentage REAL NOT NULL
        )
    ''')
    print("Products table created successfully.")
except Exception as e:
    print(f"Exception {e} occurred while creating Products table.")

finally:
    print("All tables created successfully.")
    conn.close()
